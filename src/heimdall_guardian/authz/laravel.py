"""Laravel route extractor: reads `routes/*.php` following groups and middleware."""

from __future__ import annotations

import re
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
from ..i18n import Message, msg

FRAMEWORK = "laravel"

_AUTH_MIDDLEWARE = re.compile(r"^(auth($|[:.])|verified$|can:|role:|permission:|password\.confirm)")
_STRING = re.compile(r"'((?:\\.|[^'\\])*)'|\"((?:\\.|[^\"\\])*)\"")
_ROUTE_START = re.compile(r"\bRoute::(\w+)\s*\(")
_CHAINED = re.compile(r"->\s*(middleware|prefix)\s*\(")
_ARRAY_KEY = r"['\"]{}['\"]\s*=>\s*"
_CONTROLLER = re.compile(r"(\w+)::class|['\"]([\w\\]+)@(\w+)['\"]")
_VERBS = {"get": ["GET"], "post": ["POST"], "put": ["PUT"], "patch": ["PATCH"],
          "delete": ["DELETE"], "options": ["OPTIONS"], "any": [ANY_METHOD],
          "view": ["GET"], "redirect": ["GET"]}  # fmt: skip
_RESOURCE = [
    ("GET", ""), ("GET", "create"), ("POST", ""), ("GET", "{id}"), ("GET", "{id}/edit"),
    ("PUT", "{id}"), ("DELETE", "{id}"),
]  # fmt: skip
_API_RESOURCE = [r for r in _RESOURCE if not r[1].endswith(("create", "edit"))]


def _strings(text: str) -> list[str]:
    return [a or b for a, b in _STRING.findall(text)]


def _balanced(text: str, start: int, opener: str, closer: str) -> int:
    """Position of the closer matching the `opener` at `start`; ignores strings."""
    depth, index, quote = 0, start, ""
    while index < len(text):
        char = text[index]
        if quote:
            if char == "\\":
                index += 1
            elif char == quote:
                quote = ""
        elif char in "'\"":
            quote = char
        elif char == opener:
            depth += 1
        elif char == closer:
            depth -= 1
            if depth == 0:
                return index
        index += 1
    return len(text) - 1


def _statement_end(text: str, start: int) -> int:
    """End of the statement starting at `start`: the `;` outside parentheses and braces."""
    depth, index, quote = 0, start, ""
    while index < len(text):
        char = text[index]
        if quote:
            if char == "\\":
                index += 1
            elif char == quote:
                quote = ""
        elif char in "'\"":
            quote = char
        elif char in "([{":
            depth += 1
        elif char in ")]}":
            depth -= 1
        elif char == ";" and depth == 0:
            return index
        index += 1
    return len(text)


class LaravelExtractor:
    def __init__(self, root: Path, files: list[str]) -> None:
        self.root = root
        self.files = files
        self.notes: list[Message] = []
        self._controller_auth: dict[str, bool] = {}

    def extract(self) -> list[Endpoint]:
        endpoints: list[Endpoint] = []
        for file in self.files:
            path = PurePosixPath(file)
            if path.suffix != ".php" or path.parent.name != "routes":
                continue
            try:
                raw = (self.root / file).read_text(encoding="utf-8", errors="replace")
            except OSError:
                self.notes.append(msg("authz.note.unreadable", file=file))
                continue
            text = strip_comments(raw, hash_comments=True)
            # Laravel serves routes/api.php under the /api prefix.
            prefix = "api" if path.name == "api.php" else ""
            self._parse(text, 0, len(text), file, prefix, [], endpoints)
        return sorted(endpoints, key=lambda e: (e.path, e.methods, e.handler))

    def _parse(
        self,
        text: str,
        start: int,
        end: int,
        file: str,
        prefix: str,
        middleware: list[str],
        out: list[Endpoint],
    ) -> None:
        position = start
        while True:
            match = _ROUTE_START.search(text, position, end)
            if match is None:
                return
            stop = min(_statement_end(text, match.start()), end)
            statement = text[match.start() : stop]
            group = statement.find("group(")
            # It is only a group if `group(` is in the chain, not inside a closure.
            if group != -1 and "{" not in statement[:group]:
                head = statement[:group]
                scoped_prefix, scoped_middleware = prefix, list(middleware)
                if match.group(1) == "group":
                    options = statement[group : statement.find("function", group)]
                    scoped_middleware += self._array_value(options, "middleware")
                    scoped_prefix = join_path(prefix, *self._array_value(options, "prefix"))
                for chained in _CHAINED.finditer("->" + head[len("Route::") :]):
                    open_paren = match.start() + len("Route::") - 2 + chained.end() - 1
                    values = _strings(text[open_paren : _balanced(text, open_paren, "(", ")")])
                    if chained.group(1) == "middleware":
                        scoped_middleware += values
                    else:
                        scoped_prefix = join_path(scoped_prefix, *values)
                brace = text.find("{", match.start() + group, stop)
                if brace != -1:
                    close = _balanced(text, brace, "{", "}")
                    self._parse(text, brace + 1, close, file, scoped_prefix, scoped_middleware, out)
            else:
                self._route(text, match, statement, file, prefix, middleware, out)
            position = stop + 1

    def _array_value(self, options: str, key: str) -> list[str]:
        match = re.search(_ARRAY_KEY.format(key), options)
        if match is None:
            return []
        rest = options[match.end() :].lstrip()
        if rest.startswith("["):
            return _strings(rest[: _balanced(rest, 0, "[", "]")])
        return _strings(rest)[:1]

    def _route(
        self,
        text: str,
        match: re.Match[str],
        statement: str,
        file: str,
        prefix: str,
        middleware: list[str],
        out: list[Endpoint],
    ) -> None:
        verb = match.group(1)
        open_paren = match.end() - 1
        close_paren = _balanced(text, open_paren, "(", ")")
        args = text[open_paren + 1 : close_paren]
        chain = text[close_paren + 1 : match.start() + len(statement)]
        strings = _strings(args)
        if verb == "match":
            methods = [m.upper() for m in _strings(args[: args.find("]") + 1])]
            strings = strings[len(methods) :]
        elif verb in ("resource", "apiResource"):
            methods = []
        elif verb in _VERBS:
            methods = _VERBS[verb]
        else:
            return  # Route::middleware(...) suelto, Route::pattern(...), etc.
        if not strings:
            return

        scoped = list(middleware)
        for chained in _CHAINED.finditer(chain):
            if chained.group(1) == "middleware":
                start = chained.end() - 1
                scoped += _strings(chain[start : _balanced(chain, start, "(", ")")])
        controller = _CONTROLLER.search(args)
        handler = "<closure>"
        if controller:
            handler = controller.group(1) or controller.group(2).rsplit("\\", 1)[-1]
            action = controller.group(3) or next(iter(strings[1:]), "")
            handler = f"{handler}@{action}" if action else handler

        guards = [name for name in scoped if _AUTH_MIDDLEWARE.match(name)]
        verdict: tuple[bool, Evidence]
        if guards:
            verdict = (True, f"middleware {', '.join(guards)}")
        elif controller and self._controller_has_auth(handler.split("@")[0]):
            verdict = (True, msg("authz.ev.laravel_constructor"))
        else:
            verdict = (False, msg("authz.ev.laravel_outside"))

        line = line_of(text, match.start())
        base = join_path(prefix, strings[0])
        routes = (
            [(base, methods)]
            if methods
            else [
                (join_path(base, suffix), [method])
                for method, suffix in (_API_RESOURCE if verb == "apiResource" else _RESOURCE)
            ]
        )
        for path, verbs in routes:
            writes = bool(WRITE_METHODS.intersection(verbs)) or verbs == [ANY_METHOD]
            has_auth, evidence = verdict
            out.append(
                Endpoint(path, verbs, handler, file, line, FRAMEWORK, has_auth, evidence, writes)
            )

    def _controller_has_auth(self, name: str) -> bool:
        """Does the controller constructor apply `$this->middleware('auth')`?"""
        if name not in self._controller_auth:
            found = False
            for file in self.files:
                if PurePosixPath(file).name == f"{name}.php":
                    try:
                        text = (self.root / file).read_text(encoding="utf-8", errors="replace")
                    except OSError:
                        continue
                    found = any(
                        _AUTH_MIDDLEWARE.match(value)
                        for call in re.finditer(r"->\s*middleware\s*\(([^)]*)\)", text)
                        for value in _strings(call.group(1))
                    )
            self._controller_auth[name] = found
        return self._controller_auth[name]
