"""Endpoint extractor for Node.js: Express and NestJS.

It only reads text (P2): it neither runs nor imports the analyzed code. It is not a full
lexical analyzer for JavaScript; it walks calls with balanced parentheses, which is enough
to locate routes, router mounts, middleware and decorators.

Out of scope: Fastify, Koa, Hapi, Next.js (API routes), routes built with
variables or loops, and dynamically added middleware.

`has_auth` criterion (conservative):
- `True`: there is a middleware or authentication guard recognized by name that covers the route.
- `False`: there is none, nor any unknown middleware that could be one.
- `None`: there are middleware or guards that are not recognized (neither as authentication nor as
  harmless) or a public decorator that clashes with an explicit guard; a human must review.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

from ..core.endpoints import (
    ANY_METHOD,
    WRITE_METHODS,
    Endpoint,
    Evidence,
    join_path,
    line_of,
    strip_comments,
)
from ..i18n import Message, msg, render

FRAMEWORK = "node"
FRAMEWORK_NEST = "nestjs"
EXTENSIONS = (".js", ".mjs", ".cjs", ".ts")
MAX_FILE_BYTES = 2_000_000

# --- What counts as authentication -------------------------------------------------
# Compared against each segment of the called name (`passport.authenticate` -> `authenticate`).
AUTH_MIDDLEWARE = re.compile(
    r"(?i)^(authenticate\w*|isAuthenticated|ensureAuthenticated|ensureLoggedIn|ensureLogin|"
    r"requireAuth\w*|requireLogin|requireUser|verifyToken|verifyJWT|authMiddleware|auth|"
    r"jwt|expressjwt|checkJwt|isLoggedIn|protect|withAuth|checkAuth|loginRequired)$"
)
# Passport strategies that are the login itself, not a protected route.
LOGIN_STRATEGIES = re.compile(
    r"(?i)['\"](local|google|facebook|github|twitter|microsoft|saml|oauth2?)['\"]"
)
# Middleware that neither authenticates nor authorizes: it does not make the route doubtful.
HARMLESS_MIDDLEWARE = re.compile(
    r"(?i)^(cors|helmet|morgan|compression|cookieParser|bodyParser|json|urlencoded|static|raw|"
    r"text|rateLimit\w*|limiter|slowDown|session|validate\w*|validator|check|body|param|query|"
    r"checkSchema|celebrate|asyncHandler|catchAsync|wrap|upload|multer|single|array|fields|none|"
    r"csrf|csurf|logger|cache\w*|methodOverride|flash|noCache|timeout|sanitize\w*|"
    r"errorHandler|notFound|trimBody)$"
)
# If the body of a middleware or anonymous handler mentions this, it "seems" to check the session.
INLINE_AUTH_HINT = re.compile(
    r"(?i)isAuthenticated\s*\(|req\.user\b|jwt\.verify|req\.session\.\w*user|"
    r"headers\.authorization|headers\[['\"]authorization|\btoken\b"
)
# NestJS guards that count as authentication or authorization (by name).
NEST_AUTH_GUARD = re.compile(
    r"(?i)(auth|jwt|role|permission|session|token|apikey|api_key|passport|acl|ability)"
)
NEST_HARMLESS_GUARD = re.compile(r"(?i)throttl")
# Decorators that make a route or a class public.
NEST_PUBLIC = frozenset(
    {"Public", "SkipAuth", "AllowAnonymous", "NoAuth", "IsPublic", "Anonymous", "SkipJwtAuth"}
)

_VERBS = {"get": "GET", "post": "POST", "put": "PUT", "patch": "PATCH", "delete": "DELETE",
          "all": ANY_METHOD}  # fmt: skip
_VERB_NAMES = "|".join(_VERBS)
_NEST_VERBS = {"Get": "GET", "Post": "POST", "Put": "PUT", "Patch": "PATCH", "Delete": "DELETE",
               "All": ANY_METHOD}  # fmt: skip

_ROUTER_DECL = re.compile(
    r"(?:const|let|var)\s+([\w$]+)\s*(?::[^=;]+)?=\s*("
    r"require\(\s*['\"]express['\"]\s*\)\s*\.\s*Router\s*\(|"
    r"(?:express\s*\.\s*)?Router\s*\(|"
    r"(?:express|require\(\s*['\"]express['\"]\s*\)\s*)\(\s*\))"
)
_CALL = re.compile(rf"(?<![\w$.])([\w$]+)\s*\.\s*(use|route|{_VERB_NAMES})\s*\(")
_CHAIN = re.compile(rf"\s*\.\s*({_VERB_NAMES})\s*\(")
_REQUIRE = re.compile(r"require\(\s*['\"]([^'\"]+)['\"]\s*\)")
_IMPORT_REQUIRE = re.compile(
    r"(?:const|let|var)\s+(?:([\w$]+)|\{([^}]*)\})\s*=\s*require\(\s*['\"]([^'\"]+)['\"]\s*\)"
)
_IMPORT_ES = re.compile(
    r"import\s+(?:([\w$]+)\s*,?\s*)?(?:\*\s+as\s+([\w$]+)|\{([^}]*)\})?\s*from\s*['\"]([^'\"]+)['\"]"
)
_EXPORT_DEFAULT = re.compile(
    r"module\.exports\s*=\s*([\w$]+)\s*;?|export\s+default\s+([\w$]+)|"
    r"export\s*\{[^}]*?\b([\w$]+)\s+as\s+default\b"
)
_STRING = re.compile(r"""^(?:'((?:\\.|[^'\\])*)'|"((?:\\.|[^"\\])*)"|`([^`$]*)`)$""", re.S)
_ARROW_OR_FUNCTION = re.compile(
    r"^(?:async\s+)?(?:function\b\s*([\w$]*)|\([^)]*\)\s*=>|[\w$]+\s*=>)"
)
_DECORATOR = re.compile(r"@([\w$]+)")
_NEST_CLASS = re.compile(r"\b(?:export\s+)?(?:default\s+)?(?:abstract\s+)?class\s+([\w$]+)")
_NEST_SIGNATURE = re.compile(
    r"\s*(?:(?:public|private|protected|static|async|override|readonly)\s+)*([\w$]+)"
    r"\s*(?:<[^>()]*>)?\s*\("
)
_GLOBAL_PREFIX = re.compile(r"setGlobalPrefix\(\s*['\"]([^'\"]*)['\"]")
_GLOBAL_GUARD = (
    re.compile(r"APP_GUARD\b[^}]*?useClass\s*:\s*([\w$]+)", re.S),
    re.compile(r"useGlobalGuards\(\s*(?:new\s+)?([\w$]+)"),
)


def _balanced(text: str, start: int) -> int:
    """Position of the closer matching the delimiter at `start`; respects strings."""
    pairs = {"(": ")", "[": "]", "{": "}"}
    opener = text[start]
    closer = pairs[opener]
    depth, index, quote = 0, start, ""
    while index < len(text):
        char = text[index]
        if quote:
            if char == "\\":
                index += 1
            elif char == quote:
                quote = ""
        elif char in "'\"`":
            quote = char
        elif char == opener:
            depth += 1
        elif char == closer:
            depth -= 1
            if depth == 0:
                return index
        index += 1
    return len(text) - 1


def _split_args(text: str) -> list[str]:
    """Splits arguments on top-level commas."""
    args: list[str] = []
    depth, quote, begin, index = 0, "", 0, 0
    while index < len(text):
        char = text[index]
        if quote:
            if char == "\\":
                index += 1
            elif char == quote:
                quote = ""
        elif char in "'\"`":
            quote = char
        elif char in "([{":
            depth += 1
        elif char in ")]}":
            depth -= 1
        elif char == "," and depth == 0:
            args.append(text[begin:index].strip())
            begin = index + 1
        index += 1
    tail = text[begin:].strip()
    if tail:
        args.append(tail)
    return args


def _literal(arg: str) -> str | None:
    match = _STRING.match(arg.strip())
    if match is None:
        return None
    return next(group for group in match.groups() if group is not None)


def _call_args(text: str, open_paren: int) -> tuple[list[str], int]:
    close = _balanced(text, open_paren)
    return _split_args(text[open_paren + 1 : close]), close


def _segments(expression: str) -> list[str]:
    """Called name, by segments: `passport.authenticate('jwt')` -> [passport, authenticate]."""
    callee = expression.strip().split("(", 1)[0]
    return [part.strip() for part in callee.replace("?.", ".").split(".") if part.strip()]


@dataclass
class _Guard:
    kind: str  # "auth" | "unknown"
    text: Evidence  # the middleware or guard (code) or a note about it
    origin: Evidence  # where it is declared, for the evidence
    pos: int
    scope: str = ""  # route prefix it applies to; "" = all

    def covers(self, path: str) -> bool:
        if not self.scope or self.scope == "*":
            return True
        scope = join_path(self.scope)
        return path == scope or path.startswith(scope.rstrip("/") + "/")


def _classify(expression: str, origin: Evidence, pos: int, scope: str = "") -> _Guard | None:
    """Authentication, doubtful middleware (`unknown`) or `None` if harmless."""
    expression = expression.strip()
    if not expression or expression.startswith(("...", "[")):
        return _Guard("unknown", expression[:60] or msg("authz.ev.guard_empty"), origin, pos, scope)
    inline = _ARROW_OR_FUNCTION.match(expression)
    if inline:
        if INLINE_AUTH_HINT.search(expression):
            return _Guard("unknown", msg("authz.ev.guard_inline"), origin, pos, scope)
        return None
    segments = _segments(expression)
    if not segments:
        return _Guard("unknown", expression[:60], origin, pos, scope)
    name = ".".join(segments)
    if segments[-1] == "authenticate" and LOGIN_STRATEGIES.search(expression):
        return None  # it is the login
    if segments[-1].lower() in ("optional", "optionalauth"):
        return _Guard("unknown", name, origin, pos, scope)
    if any(AUTH_MIDDLEWARE.match(segment) for segment in segments):
        return _Guard("auth", name, origin, pos, scope)
    if HARMLESS_MIDDLEWARE.match(segments[-1]) or HARMLESS_MIDDLEWARE.match(segments[0]):
        return None
    return _Guard("unknown", name, origin, pos, scope)


def _described(guards: list[_Guard]) -> list[Message]:
    """«text (origin)» of each middleware or guard, without duplicates."""
    items = [msg("authz.ev.guard_item", text=g.text, origin=g.origin) for g in guards]
    unique = {render(item, "en"): item for item in items}
    return list(unique.values())


def _verdict(
    guards: list[_Guard], absent: Message, noun: str = "middleware"
) -> tuple[bool | None, Evidence]:
    auth = [g for g in guards if g.kind == "auth"]
    if auth:
        return True, msg("authz.ev.guard_auth", noun=noun, items=_described(auth))
    unknown = [g for g in guards if g.kind == "unknown"]
    if unknown:
        return None, msg("authz.ev.guard_unknown", noun=noun, items=_described(unknown))
    return False, absent


def _handler_name(arg: str) -> str:
    arg = arg.strip()
    inline = _ARROW_OR_FUNCTION.match(arg)
    if inline:
        return inline.group(1) if inline.lastindex and inline.group(1) else "<anonymous>"
    if re.fullmatch(r"[\w$.]+", arg):
        return arg
    inner = re.fullmatch(r"[\w$.]+\(\s*([\w$.]+)\s*\)", arg)  # asyncHandler(ctrl.list)
    return inner.group(1) if inner else (arg[:50] or "<anonymous>")


@dataclass
class _Route:
    path: str
    methods: list[str]
    handler: str
    line: int
    pos: int
    own: list[_Guard]


@dataclass
class _Use:
    receiver: str
    scope: str
    args: list[str]
    pos: int


@dataclass
class _Mount:
    prefix: str
    pos: int
    target: _Router


@dataclass
class _Router:
    file: str
    name: str
    is_app: bool
    routes: list[_Route] = field(default_factory=list)
    uses: list[_Use] = field(default_factory=list)
    guards: list[_Guard] = field(default_factory=list)
    mounts: list[_Mount] = field(default_factory=list)


@dataclass
class _Module:
    file: str
    routers: dict[str, _Router] = field(default_factory=dict)
    # local name -> (resolved file or None, imported member or None)
    imports: dict[str, tuple[str | None, str | None]] = field(default_factory=dict)
    default: str | None = None


class NodeExtractor:
    def __init__(self, root: Path, files: list[str]) -> None:
        self.root = root
        self.files = [
            f for f in files if f.lower().endswith(EXTENSIONS) and not f.lower().endswith(".d.ts")
        ]
        self.notes: list[Message] = []
        self._known = set(self.files)
        self._modules: dict[str, _Module] = {}

    # ------------------------------------------------------------------ lectura
    def _read(self, file: str) -> str:
        try:
            path = self.root / file
            if path.stat().st_size > MAX_FILE_BYTES:
                self.notes.append(msg("authz.note.too_large", file=file))
                return ""
            return strip_comments(path.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            self.notes.append(msg("authz.note.unreadable", file=file))
            return ""

    def extract(self) -> list[Endpoint]:
        endpoints: list[Endpoint] = []
        nest: list[tuple[str, str]] = []
        sources: dict[str, str] = {}
        for file in self.files:
            text = self._read(file)
            if not text:
                continue
            sources[file] = text
            try:
                if "express" in text or "Router(" in text:
                    self._modules[file] = self._parse_express(file, text)
                if "@Controller" in text:
                    nest.append((file, text))
            except Exception as exc:  # odd file: warn and carry on
                self.notes.append(
                    msg("authz.note.node_routes", file=file, error=type(exc).__name__)
                )
        self._link()
        endpoints += self._express_endpoints()
        endpoints += self._nest_endpoints(nest, sources)
        return sorted(endpoints, key=lambda e: (e.path, e.methods, e.handler))

    # ------------------------------------------------------------------ Express
    def _parse_express(self, file: str, text: str) -> _Module:
        module = _Module(file)
        for match in _ROUTER_DECL.finditer(text):
            module.routers[match.group(1)] = _Router(
                file, match.group(1), "Router" not in match.group(2)
            )
        if "express" in text:
            for name in ("app", "router"):
                module.routers.setdefault(name, _Router(file, name, name == "app"))
        self._parse_imports(module, text)
        export = _EXPORT_DEFAULT.search(text)
        if export:
            module.default = next(g for g in export.groups() if g)
        for match in _CALL.finditer(text):
            router = module.routers.get(match.group(1))
            if router is None:
                continue
            open_paren = match.end() - 1
            args, close = _call_args(text, open_paren)
            kind = match.group(2)
            if kind == "use":
                self._record_use(router, args, match.start())
            elif kind == "route":
                self._record_chain(router, text, args, close, match.start(), file)
            else:
                self._record_route(router, text, kind, args, match.start(), file)
        return module

    def _parse_imports(self, module: _Module, text: str) -> None:
        for match in _IMPORT_REQUIRE.finditer(text):
            default, members, spec = match.groups()
            target = self._resolve(module.file, spec)
            if default:
                module.imports[default] = (target, None)
            for member in _split_args(members or ""):
                original, _, alias = member.partition(":")
                module.imports[(alias or original).strip()] = (target, original.strip())
        for match in _IMPORT_ES.finditer(text):
            default, namespace, members, spec = match.groups()
            target = self._resolve(module.file, spec)
            for name in (default, namespace):
                if name:
                    module.imports[name] = (target, None)
            for member in _split_args(members or ""):
                original, _, alias = member.partition(" as ")
                module.imports[(alias or original).strip()] = (target, original.strip())

    def _resolve(self, from_file: str, spec: str) -> str | None:
        if not spec.startswith("."):
            return None
        base = PurePosixPath(from_file).parent
        parts: list[str] = []
        for part in (base / spec).parts:
            if part == "..":
                if parts:
                    parts.pop()
            elif part != ".":
                parts.append(part)
        stem = "/".join(parts)
        candidates = [stem, *(stem + ext for ext in EXTENSIONS)]
        candidates += [f"{stem}/index{ext}" for ext in EXTENSIONS]
        # `./x.js` in TypeScript points to `x.ts`.
        if stem.endswith((".js", ".mjs", ".cjs")):
            candidates.append(stem.rsplit(".", 1)[0] + ".ts")
        return next((c for c in candidates if c in self._known), None)

    def _record_use(self, router: _Router, args: list[str], pos: int) -> None:
        scope = ""
        if args:
            literal = _literal(args[0])
            if literal is not None:
                scope, args = literal, args[1:]
            elif args[0].startswith(("[", "/")):
                # Route with an array or regular expression: what it covers is unknown.
                router.guards.append(_Guard("unknown", args[0][:40], f"{router.name}.use", pos))
                args = args[1:]
        router.uses.append(_Use(router.name, scope, args, pos))

    def _record_route(
        self, router: _Router, text: str, kind: str, args: list[str], pos: int, file: str
    ) -> None:
        if not args:
            return
        path = _literal(args[0])
        line = line_of(text, pos)
        if path is None or not path.startswith(("/", "*")):
            # `app.get('env')` and similar are not routes; a route with a variable is.
            if path is None and len(args) > 1 and not args[0].startswith(("{", "(")):
                self.notes.append(
                    msg("authz.note.non_literal_route", file=file, line=line, route=args[0][:40])
                )
            return
        mws, handler = (args[1:-1], args[-1]) if len(args) > 1 else ([], "")
        router.routes.append(self._route(router, text, path, [_VERBS[kind]], mws, handler, pos))

    def _record_chain(
        self, router: _Router, text: str, args: list[str], close: int, pos: int, file: str
    ) -> None:
        path = _literal(args[0]) if args else None
        if path is None:
            self.notes.append(
                msg("authz.note.non_literal_chain", file=file, line=line_of(text, pos))
            )
            return
        cursor = close + 1
        while True:
            chain = _CHAIN.match(text, cursor)
            if chain is None:
                return
            verb_args, verb_close = _call_args(text, chain.end() - 1)
            if verb_args:
                router.routes.append(
                    self._route(
                        router,
                        text,
                        path,
                        [_VERBS[chain.group(1)]],
                        verb_args[:-1],
                        verb_args[-1],
                        chain.start(1),
                    )
                )
            cursor = verb_close + 1

    def _route(
        self,
        router: _Router,
        text: str,
        path: str,
        methods: list[str],
        mws: list[str],
        handler: str,
        pos: int,
    ) -> _Route:
        origin = msg("authz.ev.origin_route")
        own = [g for m in mws if (g := _classify(m, origin, pos)) is not None]
        inline = bool(handler) and _ARROW_OR_FUNCTION.match(handler.strip()) is not None
        if inline and INLINE_AUTH_HINT.search(handler) and not any(g.kind == "auth" for g in own):
            own.append(_Guard("unknown", msg("authz.ev.guard_handler"), origin, pos))
        return _Route(path, methods, _handler_name(handler), line_of(text, pos), pos, own)

    # ------------------------------------------------------------------ enlace
    def _exported(self, file: str | None, member: str | None = None) -> _Router | None:
        module = self._modules.get(file or "")
        if module is None:
            return None
        if member and member in module.routers and member not in ("app",):
            return module.routers[member]
        if module.default and module.default in module.routers:
            return module.routers[module.default]
        routers = [r for r in module.routers.values() if not r.is_app and (r.routes or r.uses)]
        return routers[0] if len(routers) == 1 and member is None else None

    def _target(self, module: _Module, arg: str) -> _Router | None:
        arg = arg.strip()
        inline = re.fullmatch(_REQUIRE.pattern, arg)
        if inline:
            return self._exported(self._resolve(module.file, inline.group(1)))
        if re.fullmatch(r"[\w$]+", arg):
            if arg in module.routers and arg != "app":
                return module.routers[arg]
            file, member = module.imports.get(arg, (None, None))
            return self._exported(file, member)
        return None

    def _link(self) -> None:
        for module in self._modules.values():
            for router in module.routers.values():
                for use in router.uses:
                    for arg in use.args:
                        self._link_use(module, router, use, arg)

    def _link_use(self, module: _Module, router: _Router, use: _Use, arg: str) -> None:
        target = self._target(module, arg)
        if target is not None and target is not router:
            router.mounts.append(_Mount(use.scope or "/", use.pos, target))
            return
        if use.scope and re.search(r"(?i)(router|routes?|routing)\)?$|^require\(", arg.strip()):
            self.notes.append(
                msg(
                    "authz.note.unresolved_router",
                    router=arg.strip()[:50],
                    scope=use.scope,
                    file=module.file,
                )
            )
            return
        guard = _classify(arg, f"{use.receiver}.use", use.pos, use.scope)
        if guard is not None:
            router.guards.append(guard)

    def _express_endpoints(self) -> list[Endpoint]:
        routers = [r for m in self._modules.values() for r in m.routers.values()]
        mounted = {id(mount.target) for r in routers for mount in r.mounts}
        out: list[Endpoint] = []
        for router in routers:
            if id(router) in mounted or not (router.routes or router.mounts):
                continue
            if not router.is_app:
                self.notes.append(
                    msg("authz.note.unmounted_router", name=router.name, file=router.file)
                )
            self._walk(router, "", [], set(), out)
        return out

    def _walk(
        self,
        router: _Router,
        prefix: str,
        inherited: list[_Guard],
        seen: set[int],
        out: list[Endpoint],
    ) -> None:
        if id(router) in seen:
            return  # montaje circular
        seen = seen | {id(router)}
        for route in router.routes:
            guards = [
                *inherited,
                *(g for g in router.guards if g.pos < route.pos and g.covers(route.path)),
                *route.own,
            ]
            has_auth, evidence = _verdict(
                guards,
                msg("authz.ev.express_none", router=router.name),
            )
            methods = route.methods
            writes = bool(WRITE_METHODS.intersection(methods)) or methods == [ANY_METHOD]
            out.append(
                Endpoint(
                    join_path(prefix, route.path),
                    methods,
                    route.handler,
                    router.file,
                    route.line,
                    FRAMEWORK,
                    has_auth,
                    evidence,
                    writes,
                )
            )
        for mount in router.mounts:
            applied = [g for g in router.guards if g.pos <= mount.pos and g.covers(mount.prefix)]
            self._walk(
                mount.target, join_path(prefix, mount.prefix), [*inherited, *applied], seen, out
            )

    # ------------------------------------------------------------------ NestJS
    def _nest_endpoints(
        self, nest: list[tuple[str, str]], sources: dict[str, str]
    ) -> list[Endpoint]:
        if not nest:
            return []
        joined = "\n".join(sources.values())
        prefix_match = _GLOBAL_PREFIX.search(joined)
        global_prefix = prefix_match.group(1) if prefix_match else ""
        global_guard = self._global_guard(joined)
        out: list[Endpoint] = []
        for file, text in nest:
            try:
                out += self._nest_file(file, text, global_prefix, global_guard)
            except Exception as exc:
                self.notes.append(
                    msg("authz.note.node_controllers", file=file, error=type(exc).__name__)
                )
        return out

    def _global_guard(self, text: str) -> _Guard | None:
        for pattern in _GLOBAL_GUARD:
            for match in pattern.finditer(text):
                name = match.group(1)
                if NEST_AUTH_GUARD.search(name):
                    return _Guard("auth", name, msg("authz.ev.origin_global_guard"), 0)
        return None

    def _decorators(self, text: str, pos: int, end: int) -> tuple[list[tuple[str, str]], int]:
        found: list[tuple[str, str]] = []
        while True:
            while pos < end and text[pos].isspace():
                pos += 1
            match = _DECORATOR.match(text, pos)
            if match is None:
                return found, pos
            pos = match.end()
            args = ""
            probe = pos
            while probe < end and text[probe] in " \t":
                probe += 1
            if probe < end and text[probe] == "(":
                close = _balanced(text, probe)
                args, pos = text[probe + 1 : close], close + 1
            found.append((match.group(1), args))

    def _nest_file(
        self, file: str, text: str, global_prefix: str, global_guard: _Guard | None
    ) -> list[Endpoint]:
        out: list[Endpoint] = []
        for controller in re.finditer(r"@Controller\b", text):
            klass = _NEST_CLASS.search(text, controller.end())
            if klass is None:
                continue
            start = max(
                text.rfind("\n}", 0, controller.start()), text.rfind(";", 0, controller.start()), 0
            )
            first = _DECORATOR.search(text, start, klass.start())
            class_decorators, _ = self._decorators(
                text, first.start() if first else 0, klass.start()
            )
            brace = text.find("{", klass.end())
            if brace == -1:
                continue
            body_end = _balanced(text, brace)
            out += self._nest_methods(
                file,
                text,
                klass.group(1),
                line_of(text, klass.start(1)),
                class_decorators,
                (brace + 1, body_end),
                global_prefix,
                global_guard,
            )
        return out

    def _nest_methods(
        self,
        file: str,
        text: str,
        class_name: str,
        class_line: int,
        class_decorators: list[tuple[str, str]],
        span: tuple[int, int],
        global_prefix: str,
        global_guard: _Guard | None,
    ) -> list[Endpoint]:
        controller_args = next((a for n, a in class_decorators if n == "Controller"), "")
        base = self._controller_path(controller_args)
        out: list[Endpoint] = []
        pos, end = span
        while pos < end:
            at = _DECORATOR.search(text, pos, end)
            if at is None:
                break
            decorators, after = self._decorators(text, at.start(), end)
            signature = _NEST_SIGNATURE.match(text, after)
            if signature is None:
                pos = max(after, at.end())
                continue
            close = _balanced(text, signature.end() - 1)
            stop = re.compile(r"[{;]").search(text, close)
            pos = (_balanced(text, stop.start()) + 1) if stop and stop.group() == "{" else close + 1
            verbs = [(n, a) for n, a in decorators if n in _NEST_VERBS]
            if not verbs:
                continue
            verb, args = verbs[0]
            route = self._first_string(args)
            has_auth, evidence = self._nest_verdict(decorators, class_decorators, global_guard)
            method = _NEST_VERBS[verb]
            out.append(
                Endpoint(
                    join_path(global_prefix, base, route),
                    [method],
                    f"{class_name}.{signature.group(1)}",
                    file,
                    line_of(text, signature.start(1)),
                    FRAMEWORK_NEST,
                    has_auth,
                    evidence,
                    method in WRITE_METHODS or method == ANY_METHOD,
                    covers=[class_line],
                )
            )
        return out

    @staticmethod
    def _first_string(args: str) -> str:
        match = re.search(r"""['"`]([^'"`]*)['"`]""", args)
        return match.group(1) if match else ""

    def _controller_path(self, args: str) -> str:
        path = re.search(r"""\bpath\s*:\s*['"`]([^'"`]*)['"`]""", args)
        return path.group(1) if path else self._first_string(args)

    @staticmethod
    def _is_public(decorators: list[tuple[str, str]]) -> str:
        for name, args in decorators:
            if name in NEST_PUBLIC:
                return f"@{name}()"
            if name == "SetMetadata" and re.search(r"(?i)public", args) and "true" in args:
                return f"@SetMetadata({args.strip()[:40]})"
        return ""

    @staticmethod
    def _guards(decorators: list[tuple[str, str]], where: Message) -> list[_Guard]:
        guards: list[_Guard] = []
        for name, args in decorators:
            if name != "UseGuards":
                continue
            for arg in _split_args(args):
                guard_name = (_segments(arg) or [arg])[-1].removeprefix("new ").strip()
                shown = arg.strip()[:40]
                if NEST_AUTH_GUARD.search(guard_name):
                    guards.append(
                        _Guard("auth", shown, msg("authz.ev.origin_use_guards", where=where), 0)
                    )
                elif not NEST_HARMLESS_GUARD.search(guard_name):
                    guards.append(
                        _Guard("unknown", shown, msg("authz.ev.origin_use_guards", where=where), 0)
                    )
        return guards

    def _nest_verdict(
        self,
        method: list[tuple[str, str]],
        klass: list[tuple[str, str]],
        global_guard: _Guard | None,
    ) -> tuple[bool | None, Evidence]:
        guards = [
            *self._guards(method, msg("authz.ev.where_method")),
            *self._guards(klass, msg("authz.ev.where_class")),
            *([global_guard] if global_guard else []),
        ]
        public = self._is_public(method)
        where = msg("authz.ev.where_method")
        if not public:
            public, where = self._is_public(klass), msg("authz.ev.where_class")
        if public:
            if global_guard is not None or not guards:
                return False, msg("authz.ev.nest_public", decorator=public, where=where)
            return None, msg("authz.ev.nest_public_guarded", decorator=public, where=where)
        return _verdict(guards, msg("authz.ev.nest_none"), "guard")
