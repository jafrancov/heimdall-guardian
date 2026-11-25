"""Endpoint extractor for ASP.NET (controllers and Minimal APIs).

It neither compiles nor uses Roslyn: it walks the text line by line keeping count
of braces, which is enough to locate classes, actions and their attributes.
"""

from __future__ import annotations

import re
from pathlib import Path

from ..core.endpoints import (
    ANY_METHOD,
    WRITE_METHODS,
    Endpoint,
    Evidence,
    join_path,
    line_of,
    strip_comments,
)
from ..i18n import Message, msg

FRAMEWORK = "aspnet"

_CLASS = re.compile(r"\bclass\s+(\w+)(?:\s*<[^>]*>)?(?:\s*\([^)]*\))?\s*(?::\s*([^{]+))?")
_ACTION = re.compile(
    r"^\s*public\s+(?:(?:async|virtual|override|static|new)\s+)*[\w<>\[\],.?\s]+?\s+(\w+)\s*\("
)
# A `[...]` group; strings may contain brackets: [Route("api/[controller]")].
_ATTRIBUTE_GROUP = re.compile(r"\[((?:[^\[\]\"]|\"[^\"]*\")*)\]")
_ATTRIBUTE = re.compile(r"([A-Za-z_]\w*)\s*(?:\(((?:[^()\"]|\"[^\"]*\")*)\))?")
_FIRST_STRING = re.compile(r'"([^"]*)"')
_HTTP = {"HttpGet": "GET", "HttpPost": "POST", "HttpPut": "PUT", "HttpPatch": "PATCH",
         "HttpDelete": "DELETE", "HttpHead": "HEAD", "HttpOptions": "OPTIONS"}  # fmt: skip
_CONTROLLER_BASES = {"Controller", "ControllerBase", "ApiController"}
_WRITE_NAME = re.compile(r"^(Create|Edit|Update|Delete|Remove|Save|Add|Import|Upload|Post|Put)")
_MINIMAL = re.compile(r"\.Map(Get|Post|Put|Patch|Delete)\s*\(\s*\"([^\"]*)\"")
_GLOBAL_AUTH = (
    re.compile(r"FallbackPolicy\b[^;]*RequireAuthenticatedUser", re.S),
    re.compile(r"new\s+AuthorizeFilter\s*\("),
    re.compile(r"MapControllers\s*\(\s*\)\s*\.RequireAuthorization\s*\("),
    re.compile(r"MapControllerRoute\s*\([^;]*\)\s*\.RequireAuthorization\s*\(", re.S),
    re.compile(r"MapDefaultControllerRoute\s*\(\s*\)\s*\.RequireAuthorization\s*\("),
)


def _is_attribute_line(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith("[") and not _ATTRIBUTE_GROUP.sub("", stripped).strip()


def _attributes(lines: list[str]) -> dict[str, str]:
    """{name: arguments} of all attributes, including combined `[A, B]` ones."""
    return {
        name: args
        for line in lines
        for group in _ATTRIBUTE_GROUP.findall(line)
        for name, args in _ATTRIBUTE.findall(group)
    }


def _route(args: str) -> str:
    match = _FIRST_STRING.search(args)
    return match.group(1) if match else ""


class DotnetExtractor:
    def __init__(self, root: Path, files: list[str]) -> None:
        self.root = root
        self.files = [f for f in files if f.lower().endswith(".cs")]
        self.notes: list[Message] = []

    def _read(self, file: str) -> str:
        try:
            raw = (self.root / file).read_text(encoding="utf-8", errors="replace")
        except OSError:
            self.notes.append(msg("authz.note.unreadable", file=file))
            return ""
        return strip_comments(raw)

    def extract(self) -> list[Endpoint]:
        sources = {file: self._read(file) for file in self.files}
        global_auth = any(p.search(text) for text in sources.values() for p in _GLOBAL_AUTH)
        endpoints: list[Endpoint] = []
        for file, text in sources.items():
            endpoints += self._controllers(file, text, global_auth)
            endpoints += self._minimal(file, text, global_auth)
        return sorted(endpoints, key=lambda e: (e.path, e.methods, e.handler))

    def _verdict(
        self, action: dict[str, str], controller: dict[str, str], global_auth: bool
    ) -> tuple[bool, Evidence]:
        if "AllowAnonymous" in action:
            return False, msg("authz.ev.net_anonymous_action")
        if "Authorize" in action:
            return True, msg("authz.ev.net_authorize_action")
        if "AllowAnonymous" in controller:
            return False, msg("authz.ev.net_anonymous_controller")
        if "Authorize" in controller:
            return True, msg("authz.ev.net_authorize_controller")
        if global_auth:
            return True, msg("authz.ev.net_global_policy")
        return False, msg("authz.ev.net_none")

    def _controllers(self, file: str, text: str, global_auth: bool) -> list[Endpoint]:
        endpoints: list[Endpoint] = []
        depth = 0
        pending: list[str] = []  # attributes accumulated before a declaration
        controller: dict[str, object] | None = None
        for number, line in enumerate(text.splitlines(), start=1):
            if _is_attribute_line(line):
                pending.append(line)
                continue
            stripped = line.strip()
            class_match = _CLASS.search(line) if "class " in line else None
            if class_match:
                attrs = _attributes([*pending, line[: class_match.start()]])
                bases = {b.strip().split("<")[0] for b in (class_match.group(2) or "").split(",")}
                name = class_match.group(1)
                is_controller = (
                    bool(bases & _CONTROLLER_BASES)
                    or name.endswith("Controller")
                    or "ApiController" in attrs
                )
                controller = (
                    {"name": name, "attrs": attrs, "depth": depth, "line": number}
                    if is_controller and "abstract" not in line
                    else None
                )
            elif controller is not None and depth == int(str(controller["depth"])) + 1:
                action_match = _ACTION.match(line)
                if action_match and action_match.group(1) != controller["name"]:
                    attrs = _attributes([*pending, line[: action_match.start(1)]])
                    endpoint = self._action(
                        file, number, action_match.group(1), attrs, controller, global_auth
                    )
                    if endpoint:
                        endpoints.append(endpoint)
            if stripped:
                pending = []
            depth += line.count("{") - line.count("}")
            if controller is not None and depth <= int(str(controller["depth"])) and "}" in line:
                controller = None
        return endpoints

    def _action(
        self,
        file: str,
        line: int,
        name: str,
        attrs: dict[str, str],
        controller: dict[str, object],
        global_auth: bool,
    ) -> Endpoint | None:
        if "NonAction" in attrs:
            return None
        class_attrs: dict[str, str] = controller["attrs"]  # type: ignore[assignment]
        class_name = str(controller["name"])
        short = class_name.removesuffix("Controller")
        verbs = [verb for attr, verb in _HTTP.items() if attr in attrs]
        template = next((_route(attrs[a]) for a in (*_HTTP, "Route") if attrs.get(a)), "")
        is_api = "ApiController" in class_attrs or "Route" in class_attrs
        if not verbs and is_api and "Route" not in attrs:
            return None  # public helper method of an API controller

        if template.startswith(("/", "~/")):
            path = join_path(template.lstrip("~"))
        elif is_api:
            path = join_path(_route(class_attrs.get("Route", "")), template)
        else:
            path = join_path(short, template or name)
        path = path.replace("[controller]", short).replace("[action]", name)

        methods = verbs or [ANY_METHOD]
        writes = bool(WRITE_METHODS.intersection(methods)) or (
            not verbs and bool(_WRITE_NAME.match(name) or "ValidateAntiForgeryToken" in attrs)
        )
        has_auth, evidence = self._verdict(attrs, class_attrs, global_auth)
        return Endpoint(
            path, methods, f"{class_name}.{name}", file, line, FRAMEWORK, has_auth, evidence,
            writes, covers=[int(str(controller["line"]))],
        )  # fmt: skip

    def _minimal(self, file: str, text: str, global_auth: bool) -> list[Endpoint]:
        endpoints = []
        for match in _MINIMAL.finditer(text):
            statement = text[match.start() : text.find(";", match.end()) + 1 or len(text)]
            verb = match.group(1).upper()
            if ".AllowAnonymous(" in statement or "[AllowAnonymous]" in statement:
                verdict = (False, msg("authz.ev.net_anonymous_route"))
            elif ".RequireAuthorization(" in statement or "[Authorize" in statement:
                verdict = (True, msg("authz.ev.net_require_route"))
            elif global_auth:
                verdict = (True, msg("authz.ev.net_global_policy"))
            else:
                verdict = (False, msg("authz.ev.net_route_none"))
            endpoints.append(
                Endpoint(
                    join_path(match.group(2)),
                    [verb],
                    f"Map{match.group(1)}",
                    file,
                    line_of(text, match.start()),
                    FRAMEWORK,
                    *verdict,
                    verb in WRITE_METHODS,
                )
            )
        return endpoints
