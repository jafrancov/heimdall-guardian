"""Inventory of framework-less PHP: which `.php` files respond to a request by themselves.

It is a heuristic (rule PHP-AUTH-001 of the proposal), decided from the content of each
file and not from its folder name (legacy systems keep AJAX endpoints in `lib/`):

1. Compute the top-level code: what is inside PHP tags and outside the bodies of
   functions, closures and class-like declarations. Text outside the tags is inline HTML.
2. The file is a request handler if that code reads a superglobal or `php://input`,
   produces output, or the file has inline HTML.
3. Otherwise it is a script if the top-level code does work (a method call or a call to a
   function that is not configuration or a pure helper). Scheduled jobs left in the
   webroot are reachable over HTTP, so they are listed too.
4. Otherwise it only defines things (classes, functions, constants): not an endpoint.
5. A file is skipped when it is not reachable over HTTP: it has a command-line-only guard
   (`php_sapi_name() !== 'cli'`, `defined('STDIN')`) or `HtaccessIndex` says that an
   `.htaccess` denies the file or turns the PHP engine off for it.
6. Authentication: a session check in the file or an include of an access-looking file.
"""

from __future__ import annotations

import fnmatch
import re
from pathlib import Path, PurePosixPath

from ..core.endpoints import ANY_METHOD, Endpoint, strip_comments
from ..i18n import Message, msg

FRAMEWORK = "php"

_SESSION_CHECK = re.compile(
    r"(isset|empty|array_key_exists)\s*\([^)]*\$_SESSION|\$_SESSION\s*\[[^\]]+\]\s*(===?|!==?)|"
    r"\b(require_login|verificar_sesion|check_login|check_auth|is_logged_in|esta_autenticado|"
    r"validar_sesion|requiere_login)\s*\(|Auth::check\s*\(|"
    r"\$_SERVER\s*\[\s*['\"](?:PHP_AUTH_USER|PHP_AUTH_PW|(?:REDIRECT_)?HTTP_AUTHORIZATION)['\"]\s*\]",
    re.I,
)
_BASIC_AUTH = re.compile(
    r"\$_SERVER\s*\[\s*['\"](?:PHP_AUTH_USER|PHP_AUTH_PW|(?:REDIRECT_)?HTTP_AUTHORIZATION)['\"]\s*\]"
)
_LOCAL_FUNCTION = re.compile(r"(?<![\w$>:\\])function\s+&?\s*([A-Za-z_]\w*)\s*\(", re.I)
_INCLUDE = re.compile(r"\b(?:include|require)(?:_once)?\s*\(?\s*([^;]+);", re.I)
_AUTH_WORDS = frozenset(
    ["auth", "login", "sesion", "session", "guard", "seguridad", "security", "acceso", "access"]
)
_LITERAL = re.compile(r"['\"]([^'\"]+)['\"]")
_WORD_SPLIT = re.compile(r"[/\\._\-\s]+")
_DEFINE = re.compile(r"\bdefine\s*\(|\bconst\s+\w+\s*=", re.I)
_WRITES = re.compile(
    r"\$_(POST|FILES)\b|\b(INSERT\s+INTO|UPDATE\s+\w+\s+SET|DELETE\s+FROM)\b|"
    r"(?<![\w$>:])(?:unlink|fwrite|fputs|file_put_contents|move_uploaded_file|copy|rename|"
    r"mkdir|rmdir)\s*\(|"
    r"(?<![\w$>:])fopen\s*\([^;]*?,\s*['\"](?:[wacx]|r\+)[bt+]*['\"]|->\s*save\s*\(",
    re.I,
)

_MARK = "\x01"  # stands for a block of inline HTML inside the code
_OPEN_TAG = re.compile(r"<\?(?:php\b|=)", re.I)
_STRINGS = re.compile(
    r"<<<[ \t]*(['\"]?)(\w+)\1\r?\n.*?\n[ \t]*\2\b|\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*'", re.S
)
_DECL = re.compile(r"(?<![\w$>:\\])(function|fn|class|interface|trait|enum)\b", re.I)
_DECL_NAME = re.compile(r"\s+&?\s*[A-Za-z_]")

_READS_INPUT = re.compile(r"\$_(GET|POST|REQUEST|FILES|COOKIE)\b|php://input", re.I)
_OUTPUT = re.compile(
    r"(?<![\w$>:])(?:echo|print|printf|vprintf|print_r|var_dump|var_export|readfile|fpassthru)\b|"
    r"(?<![\w$>:])header\s*\(",
    re.I,
)
_CLI_GUARD = re.compile(
    r"(?:php_sapi_name\s*\(\s*\)|\bPHP_SAPI\b)\s*[!=]==?\s*['\"]cli['\"]|"
    r"['\"]cli['\"]\s*[!=]==?\s*(?:php_sapi_name\s*\(\s*\)|\bPHP_SAPI\b)|"
    r"\bdefined\s*\(\s*['\"]STDIN['\"]",
    re.I,
)
_NEW = re.compile(r"\bnew\s+\\?[\w\\]+", re.I)
_METHOD_CALL = re.compile(r"(?:->|::)\s*[A-Za-z_]\w*\s*\(")
_FUNC_CALL = re.compile(r"(?<![\w$>:])\\?([A-Za-z_]\w*)\s*\(")
# Calls that configure the environment or are pure helpers, plus language constructs.
_BENIGN_CALLS = frozenset(
    [
        "require",
        "require_once",
        "include",
        "include_once",
        "define",
        "defined",
        "constant",
        "dirname",
        "realpath",
        "basename",
        "ini_set",
        "ini_get",
        "error_reporting",
        "date_default_timezone_set",
        "setlocale",
        "set_include_path",
        "get_include_path",
        "spl_autoload_register",
        "set_error_handler",
        "set_exception_handler",
        "register_shutdown_function",
        "function_exists",
        "class_exists",
        "interface_exists",
        "isset",
        "empty",
        "array",
        "list",
        "is_file",
        "is_dir",
        "file_exists",
        "getenv",
        "putenv",
        "mb_internal_encoding",
        "session_start",
        "session_name",
        "implode",
        "explode",
        "str_replace",
        "sprintf",
        "strtoupper",
        "strtolower",
        "trim",
        "array_merge",
        "in_array",
        "count",
        "if",
        "elseif",
        "else",
        "foreach",
        "for",
        "while",
        "mysqli_report",
        "set_time_limit",
        "error_log",
        "http_response_code",
        "ini_restore",
        "ob_start",
        "header_remove",
        "ignore_user_abort",
        "gc_enable",
        "assert_options",
        "libxml_use_internal_errors",
        "switch",
        "return",
        "new",
        "unset",
        "declare",
        "catch",
        "use",
        "match",
        "fn",
        "function",
        "exit",
        "die",
        "echo",
        "print",
    ]
)

_BLOCK_OPEN = re.compile(r"^\s*<\s*([A-Za-z]+)\b\s*(.*?)\s*>\s*$")
_BLOCK_CLOSE = re.compile(r"^\s*</\s*([A-Za-z]+)\s*>\s*$")
_TRANSPARENT_BLOCKS = frozenset(
    {"ifmodule", "ifversion", "ifdefine", "requireall", "requireany", "limit", "limitexcept"}
)
_DENY = re.compile(r"^\s*(?:Require\s+all\s+denied|Deny\s+from\s+all)\s*$", re.I)
_GRANT = re.compile(r"^\s*(?:Require\s+all\s+granted|Allow\s+from\s+all)\s*$", re.I)
_ENGINE = re.compile(r"^\s*php_(?:admin_)?(?:flag|value)\s+engine\s+(\S+)\s*$", re.I)
_PHP_OFF_HANDLER = re.compile(
    r"^\s*(?:(?:RemoveHandler|RemoveType)\b.*\.php\b|SetHandler\s+(?:none|default-handler)\s*$)",
    re.I,
)

ACCESS_REACHABLE = "reachable"
ACCESS_DENIED = "denied"
ACCESS_NO_PHP = "no_php"


def _unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def _file_block_matcher(name: str, argument: str) -> tuple[bool, str] | None:
    """For a `<Files>` or `<FilesMatch>` opening: (is_regex, pattern); None for other blocks."""
    if name == "filesmatch":
        return True, _unquote(argument)
    if name == "files":
        if argument.startswith("~"):
            return True, _unquote(argument[1:])
        return False, _unquote(argument)
    return None


def _block_applies(name: str, argument: str, base: str) -> bool:
    """True if a block applies to the file with this base name."""
    if name in _TRANSPARENT_BLOCKS:
        return True
    matcher = _file_block_matcher(name, argument)
    if matcher is None:
        return False  # Location, Directory, VirtualHost and unknown blocks
    is_regex, pattern = matcher
    if not is_regex:
        return fnmatch.fnmatchcase(base, pattern)
    try:
        return re.search(pattern, base) is not None
    except re.error:
        return False


def _directives(directory: Path) -> list[tuple[tuple[tuple[str, str], ...], str]]:
    """The directives of a folder's `.htaccess` with the block stack that encloses each."""
    try:
        lines = (directory / ".htaccess").read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []
    stack: list[tuple[str, str]] = []
    out: list[tuple[tuple[tuple[str, str], ...], str]] = []
    for line in lines:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if opened := _BLOCK_OPEN.match(line):
            stack.append((opened.group(1).lower(), opened.group(2)))
        elif _BLOCK_CLOSE.match(line):
            if stack:
                stack.pop()
        else:
            out.append((tuple(stack), line))
    return out


class HtaccessIndex:
    """Decides whether a file can be requested over HTTP and run as PHP, from `.htaccess`.

    `access(rel_file)` returns `"reachable"`, `"denied"` (a deny applies to the file) or
    `"no_php"` (the PHP engine is off there, so a `.php` file is served as text). The
    `.htaccess` files are read from the root down to the file's folder, outer first; inner
    folders override outer ones. Within a file, directives are processed in order and the
    last applicable one wins. Blocks `IfModule`, `IfVersion`, `IfDefine`, `RequireAll`,
    `RequireAny`, `Limit` and `LimitExcept` are entered; `Files` and `FilesMatch` apply only
    if they match the file name; any other block does not apply.

    It is a heuristic: it does not evaluate `RewriteRule`, ignores server-level
    configuration and assumes `AllowOverride` lets `.htaccess` apply. Each folder's file is
    parsed once.
    """

    def __init__(self, root: Path) -> None:
        self.root = root
        self._parsed: dict[str, list[tuple[tuple[tuple[str, str], ...], str]]] = {}

    def _folder(self, key: str) -> list[tuple[tuple[tuple[str, str], ...], str]]:
        if key not in self._parsed:
            self._parsed[key] = _directives(self.root / key)
        return self._parsed[key]

    def access(self, rel_file: str) -> str:
        path = PurePosixPath(rel_file)
        base = path.name
        folders = [str(p) for p in reversed(path.parents)]  # "." (root) first
        denied = False
        engine_off = False
        for folder in folders:
            for stack, line in self._folder("" if folder == "." else folder):
                if not all(_block_applies(name, arg, base) for name, arg in stack):
                    continue
                if _DENY.match(line):
                    denied = True
                elif _GRANT.match(line):
                    denied = False
                elif engine := _ENGINE.match(line):
                    engine_off = engine.group(1).lower() in ("off", "0")
                elif _PHP_OFF_HANDLER.match(line):
                    engine_off = True
        if engine_off:
            return ACCESS_NO_PHP
        return ACCESS_DENIED if denied else ACCESS_REACHABLE


def _mask_strings(code: str) -> str:
    """Same text with the contents of string literals replaced by spaces (quotes kept)."""

    def blank(match: re.Match[str]) -> str:
        chunk = match.group(0)
        if chunk.startswith("<<<"):
            return '"' + re.sub(r"[^\n]", " ", chunk[1:-1]) + '"'
        return chunk[0] + re.sub(r"[^\n]", " ", chunk[1:-1]) + chunk[-1]

    return _STRINGS.sub(blank, code)


def _php_code(text: str) -> str:
    """Joins the PHP segments of a file; inline HTML becomes a marker."""
    parts: list[str] = []
    pos = 0
    while True:
        opening = _OPEN_TAG.search(text, pos)
        html = text[pos : opening.start() if opening else len(text)]
        if html.strip():
            parts.append(f" {_MARK} ;\n")
        if opening is None:
            break
        end = text.find("?>", opening.end())
        body = text[opening.end() : end if end >= 0 else len(text)]
        parts.append(f" echo {body} ;\n" if opening.group(0) == "<?=" else body + "\n")
        if end < 0:
            break
        pos = end + 2
    return "".join(parts)


def _balanced_end(masked: str, start: int) -> int:
    """Index just after the brace block that opens at `start` (end of text if unbalanced)."""
    depth = 0
    for i in range(start, len(masked)):
        if masked[i] == "{":
            depth += 1
        elif masked[i] == "}":
            depth -= 1
            if depth == 0:
                return i + 1
    return len(masked)


def _declaration_end(masked: str, start: int, keyword: str) -> int:
    """Index just after the declaration that begins at `start`."""
    paren = 0
    for i in range(start, len(masked)):
        char = masked[i]
        if char == "(":
            paren += 1
        elif char == ")":
            if paren == 0 and keyword == "fn":
                return i  # arrow function inside a call: stop before the closing paren
            paren -= 1
        elif paren == 0:
            if char == "{" and keyword != "fn":
                return _balanced_end(masked, i)
            if char == ";" or (char == "," and keyword == "fn"):
                return i
    return len(masked)


def top_level(text: str, *, keep_strings: bool = False) -> tuple[str, bool]:
    """Top-level PHP code of a file (comments already stripped) and whether it has inline HTML.

    Bodies of functions, closures, arrow functions and class-like declarations are dropped.
    String contents are blanked unless `keep_strings`. It is a heuristic, not a lexer.
    """
    code = _php_code(text)
    masked = _mask_strings(code)
    out = code if keep_strings else masked
    spans: list[tuple[int, int]] = []
    pos = 0
    while True:
        found = _DECL.search(masked, pos)
        if found is None:
            break
        keyword = found.group(1).lower()
        after = found.end()
        if keyword in ("class", "interface", "trait", "enum") and not _DECL_NAME.match(
            masked, after
        ):
            pos = after  # `new class {` or similar: keep it
            continue
        end = _declaration_end(masked, after, keyword)
        spans.append((found.start(), end))
        pos = max(end, after)
    for start, end in reversed(spans):
        out = out[:start] + " " + out[end:]
    return out.replace(_MARK, ""), _MARK in out


def _harmless_helpers(text: str) -> frozenset[str]:
    """Functions declared in the file whose body does no work by itself.

    Configuration files often declare a small helper (e.g. to read an environment
    variable) and call it on load; calling it is not work. A helper that calls methods or
    other functions (a scheduled script's `main()`) is work.
    """
    masked = _mask_strings(_php_code(text))
    names = []
    for found in _LOCAL_FUNCTION.finditer(masked):
        start = found.end() - 1  # the opening parenthesis of the parameters
        end = _declaration_end(masked, start, "function")
        brace = masked.find("{", start, end)
        if brace >= 0 and not _is_script(masked[brace + 1 : end - 1]):
            names.append(found.group(1).lower())
    return frozenset(names)


def _is_script(code: str, local: frozenset[str] = frozenset()) -> bool:
    """True if top-level code does work: a method call or a non-benign function call
    (calls to the harmless helpers in `local` do not count)."""
    code = _NEW.sub(" ", _drop_definitions(code))
    if _METHOD_CALL.search(code):
        return True
    return any(
        (name := m.group(1).lower()) not in _BENIGN_CALLS
        and name not in local
        and not name.startswith("mb_")
        for m in _FUNC_CALL.finditer(code)
    )


def _drop_definitions(code: str) -> str:
    """Blanks `define(...)` arguments and `const X = ...;` values: constants are not work."""
    out = code
    while found := _DEFINE.search(out):
        if found.group(0).lower().startswith("const"):
            end = out.find(";", found.end())
            end = len(out) if end < 0 else end
        else:
            depth, end = 1, len(out)
            for i in range(found.end(), len(out)):
                depth += (out[i] == "(") - (out[i] == ")")
                if depth == 0:
                    end = i + 1
                    break
        out = out[: found.start()] + " " + out[end:]
    return out


class PhpExtractor:
    def __init__(self, root: Path, files: list[str]) -> None:
        self.root = root
        self.files = [f for f in files if f.lower().endswith(".php")]
        self.notes: list[Message] = []
        self._htaccess = HtaccessIndex(root)
        self._known = set(self.files)
        self._guards: dict[str, bool] = {}

    def _resolve(self, target: str, file: str) -> str | None:
        """Maps an include expression to a known file of the analyzed tree, if unambiguous."""
        literals = _LITERAL.findall(target)
        if not literals:
            return None
        wanted = literals[-1].replace("\\", "/")
        folder = PurePosixPath(file).parent
        for base in (folder, PurePosixPath(".")):
            parts: list[str] = []
            for part in (base / wanted.lstrip("/")).parts:
                if part == "..":
                    if parts:
                        parts.pop()
                elif part != ".":
                    parts.append(part)
            candidate = "/".join(parts)
            if candidate in self._known:
                return candidate
        suffix = "/" + wanted.lstrip("./").lstrip("/")
        matches = [f for f in self._known if ("/" + f).endswith(suffix)]
        return matches[0] if len(matches) == 1 else None

    def _checks_session(
        self, file: str, depth: int = 2, seen: frozenset[str] = frozenset()
    ) -> bool:
        """True if `file` checks the session (following includes)."""
        if file in seen:
            return False
        if depth == 2 and file in self._guards:
            return self._guards[file]
        try:
            raw = (self.root / file).read_text(encoding="utf-8", errors="replace")
        except OSError:
            return False
        # The whole file counts, not only its top level: access helpers usually keep the
        # session check inside a function that the including file calls.
        code = strip_comments(raw, hash_comments=True)
        found = bool(_SESSION_CHECK.search(code))
        if not found and depth > 1:
            for target in _INCLUDE.findall(code):
                inner = self._resolve(target, file)
                if inner and self._checks_session(inner, depth - 1, seen | {file}):
                    found = True
                    break
        if depth == 2:
            self._guards[file] = found
        return found

    def _guard_of(self, text: str, file: str) -> str | None:
        """The include that guards access: a resolved file that checks the session, or,
        if it cannot be resolved, one whose name is an access-looking word."""
        for target in (t.strip() for t in _INCLUDE.findall(text)):
            resolved = self._resolve(target, file)
            if resolved is not None:
                if resolved != file and self._checks_session(resolved):
                    return resolved
                continue
            literals = _LITERAL.findall(target)
            name: str = literals[-1] if literals else target
            if _AUTH_WORDS.intersection(_WORD_SPLIT.split(name.lower())):
                return name[:60]
        return None

    def extract(self) -> list[Endpoint]:
        endpoints = []
        for file in self.files:
            try:
                raw = (self.root / file).read_text(encoding="utf-8", errors="replace")
            except OSError:
                self.notes.append(msg("authz.note.unreadable", file=file))
                continue
            text = strip_comments(raw, hash_comments=True)
            code, inline_html = top_level(text)
            kept, _ = top_level(text, keep_strings=True)
            handler = bool(inline_html or _READS_INPUT.search(kept) or _OUTPUT.search(code))
            if not handler and not _is_script(code, _harmless_helpers(text)):
                continue  # only defines classes, functions or configuration
            if _CLI_GUARD.search(kept) or self._htaccess.access(file) != ACCESS_REACHABLE:
                continue
            if found := _SESSION_CHECK.search(text):
                basic = _BASIC_AUTH.match(found.group(0))
                verdict = (
                    True,
                    msg("authz.ev.php_basic_auth" if basic else "authz.ev.php_session"),
                )
            else:
                guard = self._guard_of(text, file)
                if guard:
                    verdict = (True, msg("authz.ev.php_includes", file=guard))
                elif handler:
                    verdict = (False, msg("authz.ev.php_none"))
                else:
                    verdict = (False, msg("authz.ev.php_script"))
            endpoints.append(
                Endpoint("/" + file, [ANY_METHOD], PurePosixPath(file).name, file, 1, FRAMEWORK,
                         *verdict, bool(_WRITES.search(text)))
            )  # fmt: skip
        return sorted(endpoints, key=lambda e: e.path)
