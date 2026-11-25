"""Route extractor for Django and DRF: reads `urls.py` and the views with `ast`.

It only analyzes the syntax tree; it never imports or runs the code.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

from ..core.endpoints import ANY_METHOD, WRITE_METHODS, Endpoint, Evidence, join_path
from ..i18n import Message, msg

FRAMEWORK = "django"

_AUTH_DECORATORS = {
    "login_required",
    "permission_required",
    "user_passes_test",
    "staff_member_required",
    "superuser_required",
}
_AUTH_MIXINS = {
    "LoginRequiredMixin",
    "PermissionRequiredMixin",
    "UserPassesTestMixin",
    "AccessMixin",
}
_TRANSPARENT_WRAPPERS = {"csrf_exempt", "csrf_protect", "never_cache", "cache_page"}
_DRF_OPEN = {"AllowAny", "IsAuthenticatedOrReadOnly"}
_HTTP_HANDLERS = {
    "get": "GET",
    "post": "POST",
    "put": "PUT",
    "patch": "PATCH",
    "delete": "DELETE",
    "list": "GET",
    "retrieve": "GET",
    "create": "POST",
    "update": "PUT",
    "partial_update": "PATCH",
    "destroy": "DELETE",
}
_ALL = ["GET", "POST", "PUT", "PATCH", "DELETE"]
_BASE_METHODS = {
    "ModelViewSet": _ALL,
    "ReadOnlyModelViewSet": ["GET"],
    "ListAPIView": ["GET"],
    "RetrieveAPIView": ["GET"],
    "CreateAPIView": ["POST"],
    "UpdateAPIView": ["PUT", "PATCH"],
    "DestroyAPIView": ["DELETE"],
    "ListCreateAPIView": ["GET", "POST"],
    "RetrieveUpdateAPIView": ["GET", "PUT", "PATCH"],
    "RetrieveDestroyAPIView": ["GET", "DELETE"],
    "RetrieveUpdateDestroyAPIView": ["GET", "PUT", "PATCH", "DELETE"],
    "CreateView": ["GET", "POST"],
    "UpdateView": ["GET", "POST"],
    "DeleteView": ["GET", "POST"],
    "FormView": ["GET", "POST"],
    "ListView": ["GET"],
    "DetailView": ["GET"],
    "TemplateView": ["GET"],
    "RedirectView": ["GET"],
}
_LOGIN_MIDDLEWARE = "django.contrib.auth.middleware.LoginRequiredMiddleware"


def _name(node: ast.AST) -> str:
    """Last segment of a name: `mixins.LoginRequiredMixin` → `LoginRequiredMixin`."""
    if isinstance(node, ast.Call):
        return _name(node.func)
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value.rsplit(".", 1)[-1]
    return ""


def _names(node: ast.AST | None) -> list[str]:
    if isinstance(node, ast.List | ast.Tuple | ast.Set):
        return [_name(item) for item in node.elts]
    return [_name(node)] if node is not None else []


def _strings(node: ast.AST | None) -> list[str]:
    if isinstance(node, ast.List | ast.Tuple | ast.Set):
        return [
            e.value for e in node.elts if isinstance(e, ast.Constant) and isinstance(e.value, str)
        ]
    return []


@dataclass
class _View:
    name: str
    line: int
    methods: list[str]
    writes: bool
    has_auth: bool | None
    evidence: Evidence
    covers: list[int] = field(default_factory=list)


@dataclass
class _Settings:
    drf_default_open: bool = True  # without DEFAULT_PERMISSION_CLASSES, DRF uses AllowAny
    login_middleware: bool = False
    root_urlconf: str | None = None


class _Module:
    """Views defined in a file, with their authentication verdict."""

    def __init__(self, tree: ast.Module, settings: _Settings) -> None:
        self.settings = settings
        self.functions: dict[str, ast.FunctionDef | ast.AsyncFunctionDef] = {}
        self.classes: dict[str, ast.ClassDef] = {}
        for node in tree.body:
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                self.functions[node.name] = node
            elif isinstance(node, ast.ClassDef):
                self.classes[node.name] = node

    def view(self, name: str) -> _View | None:
        if name in self.functions:
            return self._function(self.functions[name])
        if name in self.classes:
            return self._class(self.classes[name])
        return None

    def _global(self, public: bool) -> tuple[bool, Evidence] | None:
        if self.settings.login_middleware and not public:
            return True, msg("authz.ev.login_middleware")
        return None

    def _drf(self, permissions: list[str] | None) -> tuple[bool, Evidence]:
        if permissions is None:
            if self.settings.drf_default_open:
                return False, msg("authz.ev.drf_default_open")
            return True, msg("authz.ev.drf_default_settings")
        if not permissions or _DRF_OPEN.intersection(permissions):
            return False, f"permission_classes = [{', '.join(permissions)}]"
        return True, f"permission_classes = [{', '.join(permissions)}]"

    def _function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> _View:
        decorators = {_name(d): d for d in node.decorator_list}
        methods = [ANY_METHOD]
        for name in ("api_view", "require_http_methods"):
            call = decorators.get(name)
            if isinstance(call, ast.Call) and call.args:
                methods = [m.upper() for m in _strings(call.args[0])] or methods
        if "require_POST" in decorators:
            methods = ["POST"]
        elif decorators.keys() & {"require_GET", "require_safe"}:
            methods = ["GET"]

        auth = sorted(decorators.keys() & _AUTH_DECORATORS)
        permissions = decorators.get("permission_classes")
        verdict: tuple[bool, Evidence]
        if auth:
            verdict = (True, "@" + ", @".join(auth))
        elif "api_view" in decorators:
            listed = (
                _names(permissions.args[0])
                if isinstance(permissions, ast.Call) and permissions.args
                else None
            )
            verdict = self._drf(listed)
        else:
            verdict = self._global("login_not_required" in decorators) or (
                False,
                msg("authz.ev.django_no_decorator"),
            )
        writes = bool(WRITE_METHODS.intersection(methods)) or (
            methods == [ANY_METHOD] and _body_writes(node)
        )
        return _View(node.name, node.lineno, methods, writes, *verdict)

    def _bases(self, node: ast.ClassDef, seen: set[str] | None = None) -> list[ast.ClassDef]:
        """The class and its bases defined in the same file (local inheritance)."""
        seen = seen or set()
        chain = [node]
        for base in node.bases:
            name = _name(base)
            if name in self.classes and name not in seen:
                seen.add(name)
                chain += self._bases(self.classes[name], seen)
        return chain

    def _class(self, node: ast.ClassDef) -> _View:
        chain = self._bases(node)
        base_names = {_name(base) for cls in chain for base in cls.bases}
        decorators = {
            name for cls in chain for d in cls.decorator_list for name in _decorator_names(d)
        }

        methods, permissions = _class_members(chain, base_names)

        is_drf = permissions is not None or any(
            base.endswith(("APIView", "ViewSet")) for base in base_names
        )
        mixins = sorted(base_names & _AUTH_MIXINS)
        auth_decorators = sorted(decorators & _AUTH_DECORATORS)
        verdict: tuple[bool, Evidence]
        if mixins:
            verdict = (True, ", ".join(mixins))
        elif auth_decorators:
            verdict = (True, "@method_decorator(" + ", ".join(auth_decorators) + ")")
        elif is_drf:
            verdict = self._drf(permissions)
        else:
            verdict = self._global("login_not_required" in decorators) or (
                False,
                msg("authz.ev.django_no_mixin"),
            )
        writes = bool(WRITE_METHODS.intersection(methods)) or methods == [ANY_METHOD]
        return _View(node.name, node.lineno, methods, writes, *verdict)


def _class_members(
    chain: list[ast.ClassDef], base_names: set[str]
) -> tuple[list[str], list[str] | None]:
    """HTTP methods the class handles and its `permission_classes`, if declared."""
    methods: set[str] = set()
    permissions: list[str] | None = None
    for cls in chain:
        for item in cls.body:
            if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
                methods.add(_HTTP_HANDLERS.get(item.name, ""))
            elif (
                isinstance(item, ast.Assign)
                and permissions is None
                and any(_name(target) == "permission_classes" for target in item.targets)
            ):
                permissions = _names(item.value)
    for base in base_names:
        methods.update(_BASE_METHODS.get(base, []))
    return [m for m in _ALL if m in methods] or [ANY_METHOD], permissions


def _decorator_names(node: ast.AST) -> list[str]:
    """Names of a decorator, including the one wrapped by `method_decorator(...)`."""
    names = [_name(node)]
    if isinstance(node, ast.Call) and _name(node) == "method_decorator":
        for arg in node.args:
            names += _names(arg)
    return names


def _body_writes(node: ast.AST) -> bool:
    """Signs that a view with no declared methods modifies data."""
    for child in ast.walk(node):
        if isinstance(child, ast.Attribute) and child.attr in {"POST", "FILES"}:
            return True
        if isinstance(child, ast.Constant) and child.value in WRITE_METHODS:
            return True
        if (
            isinstance(child, ast.Call)
            and isinstance(child.func, ast.Attribute)
            and child.func.attr in {"save", "delete", "create", "update", "bulk_create"}
        ):
            return True
    return False


class DjangoExtractor:
    def __init__(self, root: Path, files: list[str]) -> None:
        self.root = root
        self.files = [f for f in files if f.endswith(".py")]
        self.notes: list[Message] = []
        self._trees: dict[str, ast.Module | None] = {}
        self._modules: dict[str, _Module] = {}
        self.settings = self._read_settings()

    # ------------------------------------------------------------ files

    def _tree(self, file: str) -> ast.Module | None:
        if file not in self._trees:
            try:
                source = (self.root / file).read_text(encoding="utf-8", errors="replace")
                self._trees[file] = ast.parse(source)
            except (OSError, SyntaxError, ValueError):
                self._trees[file] = None
                self.notes.append(msg("authz.note.not_python", file=file))
        return self._trees[file]

    def _module(self, file: str) -> _Module | None:
        if file not in self._modules:
            tree = self._tree(file)
            if tree is None:
                return None
            self._modules[file] = _Module(tree, self.settings)
        return self._modules[file]

    def _find_module(self, dotted: str, origin: str, level: int = 0) -> str | None:
        """File of a module: `app.views` → `app/views.py` (or its package)."""
        parts = [p for p in dotted.split(".") if p]
        if level:
            base = PurePosixPath(origin).parent
            for _ in range(level - 1):
                base = base.parent
            candidates = [(base / "/".join(parts)).as_posix()] if parts else [base.as_posix()]
        else:
            candidates = ["/".join(parts)]
        for candidate in candidates:
            candidate = candidate.lstrip("./")
            for suffix in (f"{candidate}.py", f"{candidate}/__init__.py"):
                for file in self.files:
                    if file == suffix or (not level and file.endswith("/" + suffix)):
                        return file
        return None

    def _read_settings(self) -> _Settings:
        settings = _Settings()
        for file in self.files:
            path = PurePosixPath(file)
            if not (path.name.startswith("settings") or path.parent.name == "settings"):
                continue
            tree = self._tree(file)
            for node in ast.walk(tree) if tree else []:
                if not isinstance(node, ast.Assign):
                    continue
                target = _name(node.targets[0])
                if target == "REST_FRAMEWORK" and isinstance(node.value, ast.Dict):
                    for key, value in zip(node.value.keys, node.value.values, strict=True):
                        if key is not None and _name(key) == "DEFAULT_PERMISSION_CLASSES":
                            listed = _names(value)
                            settings.drf_default_open = not listed or bool(
                                _DRF_OPEN.intersection(listed)
                            )
                elif target == "MIDDLEWARE" and _LOGIN_MIDDLEWARE in _strings(node.value):
                    settings.login_middleware = True
                elif target == "ROOT_URLCONF" and isinstance(node.value, ast.Constant):
                    settings.root_urlconf = str(node.value.value)
        return settings

    # --------------------------------------------------------------- rutas

    def extract(self) -> list[Endpoint]:
        urlconfs = [f for f in self.files if PurePosixPath(f).name == "urls.py"]
        included: set[str] = set()
        collected: dict[str, list[Endpoint]] = {}
        for file in urlconfs:
            collected[file] = self._urlconf(file, "", included, depth=0)

        root = (
            self._find_module(self.settings.root_urlconf, "")
            if self.settings.root_urlconf
            else None
        )
        roots = [root] if root in collected else [f for f in urlconfs if f not in included]
        endpoints = [endpoint for file in roots for endpoint in collected[file]]
        return sorted(endpoints, key=lambda e: (e.path, e.methods, e.handler))

    def _imports(self, tree: ast.Module, file: str) -> dict[str, tuple[str | None, str | None]]:
        """Local name → (module file, imported attribute)."""
        names: dict[str, tuple[str | None, str | None]] = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    local = alias.asname or alias.name
                    # `from . import views` imports a module; `from .views import x`, a name.
                    as_module = self._find_module(
                        f"{module}.{alias.name}".strip("."), file, node.level
                    )
                    if as_module:
                        names[local] = (as_module, None)
                    else:
                        names[local] = (self._find_module(module, file, node.level), alias.name)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    local = alias.asname or alias.name.split(".")[0]
                    names[local] = (self._find_module(alias.name, file), None)
        return names

    def _urlconf(self, file: str, prefix: str, included: set[str], depth: int) -> list[Endpoint]:
        tree = self._tree(file)
        if tree is None or depth > 8:
            return []
        imports = self._imports(tree, file)
        routers = self._routers(tree, file, imports)
        endpoints: list[Endpoint] = []
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Call) and _name(node.func) in {"path", "re_path", "url"}):
                continue
            if len(node.args) < 2 or not isinstance(node.args[0], ast.Constant):
                continue
            route = join_path(prefix, str(node.args[0].value))
            target = node.args[1]
            if isinstance(target, ast.Call) and _name(target.func) == "include":
                endpoints += self._include(target, file, route, imports, routers, included, depth)
            elif _name(target) == "urls" and "site" in ast.dump(target):
                endpoints.append(
                    Endpoint(route, [ANY_METHOD], "admin.site", file, node.lineno, FRAMEWORK,
                             True, msg("authz.ev.django_admin"), True)
                )  # fmt: skip
            else:
                endpoints.append(self._endpoint(route, target, file, node.lineno, imports))
        return endpoints

    def _include(
        self,
        call: ast.Call,
        file: str,
        route: str,
        imports: dict[str, tuple[str | None, str | None]],
        routers: dict[str, list[tuple[str, ast.AST, int]]],
        included: set[str],
        depth: int,
    ) -> list[Endpoint]:
        if not call.args:
            return []
        arg = call.args[0]
        if isinstance(arg, ast.Tuple) and arg.elts:
            arg = arg.elts[0]
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            target = self._find_module(arg.value, file)
            if target is None:
                if not arg.value.startswith(("django.", "rest_framework.")):
                    self.notes.append(msg("authz.note.module_not_found", module=repr(arg.value)))
                return []
            included.add(target)
            return self._urlconf(target, route, included, depth + 1)
        if isinstance(arg, ast.Attribute) and arg.attr == "urls" and _name(arg.value) in routers:
            endpoints = []
            for registered, viewset, line in routers[_name(arg.value)]:
                base = join_path(route, registered)
                collection = self._endpoint(base, viewset, file, line, imports)
                detail = self._endpoint(join_path(base, "{pk}"), viewset, file, line, imports)
                collection.methods = [m for m in collection.methods if m in {"GET", "POST"}] or [
                    "GET"
                ]
                detail.methods = [m for m in detail.methods if m != "POST"] or ["GET"]
                for endpoint in (collection, detail):
                    endpoint.writes = bool(WRITE_METHODS.intersection(endpoint.methods))
                endpoints += [collection, detail]
            return endpoints
        return []

    def _routers(
        self, tree: ast.Module, file: str, imports: dict[str, tuple[str | None, str | None]]
    ) -> dict[str, list[tuple[str, ast.AST, int]]]:
        """`router.register("prefijo", ViewSet)` grouped by router name."""
        routers: dict[str, list[tuple[str, ast.AST, int]]] = {}
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "register"
                and len(node.args) >= 2
                and isinstance(node.args[0], ast.Constant)
            ):
                routers.setdefault(_name(node.func.value), []).append(
                    (str(node.args[0].value), node.args[1], node.lineno)
                )
        return routers

    def _endpoint(
        self,
        route: str,
        target: ast.AST,
        file: str,
        line: int,
        imports: dict[str, tuple[str | None, str | None]],
    ) -> Endpoint:
        wrappers: list[str] = []
        # login_required(vista), csrf_exempt(vista), Vista.as_view(): the layers are peeled off.
        while isinstance(target, ast.Call):
            name = _name(target.func)
            if name == "as_view" and isinstance(target.func, ast.Attribute):
                target = target.func.value
            elif (name in _AUTH_DECORATORS or name in _TRANSPARENT_WRAPPERS) and target.args:
                wrappers.append(name)
                target = target.args[0]
            elif isinstance(target.func, ast.Call) and target.args:
                # permission_required("x")(vista)
                wrappers.append(_name(target.func.func))
                target = target.args[0]
            else:
                break

        label = ast.unparse(target)
        view_file, view = self._resolve(target, file, imports)
        if view is None:
            django_generic = _name(target) in _BASE_METHODS
            endpoint = Endpoint(
                route, _BASE_METHODS.get(_name(target), [ANY_METHOD]), label, file, line,
                FRAMEWORK, False if django_generic else None,
                msg("authz.ev.django_generic_no_mixin") if django_generic
                else msg("authz.ev.view_not_found"), not django_generic,
            )  # fmt: skip
        else:
            endpoint = Endpoint(
                route, view.methods, view.name, view_file, view.line, FRAMEWORK,
                view.has_auth, view.evidence, view.writes, route_file=file, covers=view.covers,
            )  # fmt: skip
        url_auth = sorted(set(wrappers) & _AUTH_DECORATORS)
        if url_auth:
            endpoint.has_auth = True
            endpoint.evidence = msg("authz.ev.url_wrapper", wrappers=url_auth, file=file)
        return endpoint

    def _resolve(
        self, target: ast.AST, file: str, imports: dict[str, tuple[str | None, str | None]]
    ) -> tuple[str, _View | None]:
        if isinstance(target, ast.Name):
            module_file, attr = imports.get(target.id, (file, target.id))
            attr = attr or target.id
        elif isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name):
            module_file, _ = imports.get(target.value.id, (None, None))
            attr = target.attr
        else:
            return file, None
        if module_file is None:
            return file, None
        module = self._module(module_file)
        return module_file, module.view(attr) if module else None
