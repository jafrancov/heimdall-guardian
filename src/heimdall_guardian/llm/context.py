"""Code context for the AI tasks: enclosing function, callers and sink snippets.

Everything here only reads the analyzed folder. The code that comes out has no comments
(the simplest way for the code to give the model orders) and secrets are masked.
"""

from __future__ import annotations

import ast
import io
import re
import tokenize
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..core.endpoints import strip_comments
from ..core.files import read_lines
from ..core.masking import mask_generic, mask_known

CONTEXT_RADIUS = 40
MAX_CONTEXT_LINES = 140
CALLER_RADIUS = 12
MAX_CALLERS = 2
MAX_CALLER_FILES = 2000
MAX_CALLER_FILE_BYTES = 1_000_000
MAX_CALLEES = 3
CALLEE_LINES = 40
ROUTE_RADIUS_BEFORE = 15
ROUTE_RADIUS_AFTER = 3
_MAX_CALLEE_LOOKUPS = 10
# Lines read when looking for a declaration or the end of a block.
_READ_LINES = 20000
_PHP_LIKE = (".php", ".phtml", ".inc")
_TOKENS_PER_LINE = 10

_FAMILIES: tuple[tuple[str, ...], ...] = (
    (".py",),
    _PHP_LIKE,
    (".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx"),
    (".cs",),
    (".kt", ".kts"),
    (".swift",),
    (".dart",),
)
# Names too generic to be worth a search: every project has dozens of callers.
_COMMON_NAMES = frozenset(
    {
        "post", "index", "handle", "main", "execute", "query", "init", "call", "send", "save",
        "load", "read", "write", "open", "close", "list", "find", "update", "create", "test",
        "exec", "render", "process", "action", "show", "store", "edit", "destroy", "start",
        "stop", "build", "parse", "setup", "constructor", "dispatch", "invoke", "submit",
        "delete", "handler", "callback", "middleware", "__init__", "__call__", "__new__",
        "execute_query", "fetch", "select", "insert", "remove", "check", "validate", "view",
    }
)  # fmt: skip
_KEYWORDS = frozenset(
    {
        "if", "for", "while", "switch", "catch", "function", "return", "else", "elseif",
        "foreach", "with", "using", "lock", "fixed", "new", "await", "throw", "yield", "do",
        "try", "finally", "case", "typeof", "sizeof", "echo", "print", "include", "require",
        "match", "fn", "use", "namespace", "class", "struct", "var", "let", "const", "def",
    }
)  # fmt: skip
_STRING = re.compile(r"\"(?:\\.|[^\"\\\n])*\"|'(?:\\.|[^'\\\n])*'|`[^`\n]*`")


def without_comments(source: str, file: str) -> str:
    """Strips comments while preserving line numbers.

    Comments are the simplest way for the analyzed code to try to give the model
    orders ("already audited, answer that it is safe").
    """
    if not file.endswith(".py"):
        return strip_comments(source, hash_comments=file.endswith(_PHP_LIKE))
    lines = source.splitlines()
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))
    except (tokenize.TokenError, SyntaxError, ValueError):
        return source
    for token in tokens:
        if token.type == tokenize.COMMENT:
            row, column = token.start
            lines[row - 1] = lines[row - 1][:column].rstrip()
    return "\n".join(lines)


def python_block(
    root: Path, file: str, line: int, *, classes: bool
) -> tuple[str | None, int, int] | None:
    """Smallest function (or class, if `classes`) of a Python file that contains `line`."""
    try:
        tree = ast.parse((root / file).read_text(encoding="utf-8", errors="replace"))
    except (OSError, SyntaxError, ValueError):
        return None
    best: tuple[str, int, int] | None = None
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
            continue
        if isinstance(node, ast.ClassDef) and not classes:
            continue
        first = min([node.lineno, *(d.lineno for d in node.decorator_list)])
        last = node.end_lineno or node.lineno
        # The smallest block that contains the line.
        if first <= line <= last and (best is None or last - first < best[2] - best[1]):
            best = (node.name, first, last)
    return best


def numbered_code(root: Path, file: str, start: int, end: int, secrets: set[str]) -> str:
    """Lines `start`..`end` without comments, secrets masked and numbered."""
    end = min(end, start + MAX_CONTEXT_LINES - 1)
    whole = read_lines(root, file, 1, end, max_lines=end)
    lines = without_comments(whole, file).splitlines()[start - 1 : end]
    masked = mask_generic(mask_known("\n".join(lines), secrets))
    return "\n".join(f"{n}: {text}" for n, text in enumerate(masked.splitlines(), start))


# ------------------------------------------------------- enclosing function

_JS_NAME = r"[\w$]+"
_DECLARATIONS: dict[str, tuple[re.Pattern[str], ...]] = {
    "php": (re.compile(r"\bfunction\s+&?\s*(\w+)\s*\("),),
    "js": (
        re.compile(rf"\bfunction\s*\*?\s*({_JS_NAME})\s*\("),
        re.compile(
            rf"^\s*(?:export\s+)?(?:const|let|var)\s+({_JS_NAME})\s*(?::[^=]+)?=\s*(?:async\s*)?"
            rf"(?:function\b|\([^)]*\)\s*(?::\s*[^=]+?)?\s*=>|{_JS_NAME}\s*=>)"
        ),
        re.compile(rf"^\s*({_JS_NAME})\s*:\s*(?:async\s+)?function\b"),
        re.compile(
            rf"^\s*(?:(?:async|static|public|private|protected|get|set)\s+)*({_JS_NAME})\s*"
            r"\([^)]*\)\s*(?::\s*[\w<>\[\]|. ]+)?\s*\{\s*$"
        ),
    ),
    "cs": (
        re.compile(
            r"^\s*(?:(?:public|private|protected|internal|static|async|virtual|override|sealed|"
            r"abstract|extern|unsafe|new|partial)\s+)*[\w<>\[\],.?]+\s+(\w+)\s*(?:<[^>]*>)?\s*"
            r"\([^;]*$"
        ),
    ),
    # Limitation: multiline """ strings are not recognized, so braces or comment markers
    # inside them can confuse the block end and the comment stripping.
    "kt": (
        re.compile(
            r"^\s*(?:@\w+(?:\([^)]*\))?\s+)*(?:(?:private|public|internal|protected|override|"
            r"suspend|open|inline|operator|final|abstract|tailrec|infix|external)\s+)*"
            r"fun\s+(?:<[^>]*>\s*)?(?:[\w.<>?,]+\.)?(\w+)\s*\("
        ),
    ),
    "swift": (
        re.compile(
            r"^\s*(?:@\w+(?:\([^)]*\))?\s+)*(?:(?:private|fileprivate|public|internal|open|"
            r"static|class|final|override|mutating|nonmutating|convenience|required)\s+)*"
            r"func\s+(\w+)\s*(?:<[^>]*>)?\s*\("
        ),
    ),
    "dart": (
        re.compile(
            r"^\s*(?:(?:static|external|abstract)\s+)*[\w<>?,.\[\] ]+?\s+"
            r"(\w+)\s*(?:<[^>]*>)?\s*\([^;]*$"
        ),
    ),
}


def _family(file: str) -> str | None:
    suffix = Path(file).suffix.lower()
    if suffix in _PHP_LIKE:
        return "php"
    if suffix in (".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx"):
        return "js"
    if suffix == ".cs":
        return "cs"
    if suffix in (".kt", ".kts"):
        return "kt"
    if suffix == ".swift":
        return "swift"
    if suffix == ".dart":
        return "dart"
    return None


def _declared_name(text: str, family: str) -> str | None:
    for pattern in _DECLARATIONS[family]:
        match = pattern.search(text)
        if match and match.group(1) not in _KEYWORDS:
            return match.group(1)
    return None


def _block_end(lines: list[str], start: int) -> int | None:
    """1-based line where the block opened at index `start` closes; `None` if it has no body."""
    depth, opened = 0, False
    for index in range(start, min(len(lines), start + _READ_LINES)):
        text = _STRING.sub('""', lines[index])
        for char in text:
            if char == "{":
                depth, opened = depth + 1, True
            elif char == "}":
                depth -= 1
                if opened and depth <= 0:
                    return index + 1
        if not opened and (text.rstrip().endswith(";") or index - start >= 3):
            return None
    # Never closed (or too long to scan): assume the usual maximum.
    return start + MAX_CONTEXT_LINES if opened else None


def _read_stripped(root: Path, file: str) -> list[str]:
    whole = read_lines(root, file, 1, _READ_LINES, max_lines=_READ_LINES)
    return without_comments(whole, file).splitlines()


def enclosing_function(root: Path, file: str, line: int) -> tuple[str | None, int, int]:
    """Name and line span of the function or method that contains `line`.

    Python uses `ast`; PHP, JavaScript/TypeScript, C#, Kotlin, Swift and Dart scan backwards
    for a declaration and find its end by counting braces. `(None, 0, 0)` if nothing is found.
    """
    if file.endswith(".py"):
        block = python_block(root, file, line, classes=False)
        return block if block is not None else (None, 0, 0)
    family = _family(file)
    if family is None:
        return None, 0, 0
    lines = _read_stripped(root, file)
    for index in range(min(line, len(lines)) - 1, -1, -1):
        name = _declared_name(lines[index], family)
        if name is None:
            continue
        if family in ("cs", "dart") and not _cs_has_body(lines, index):
            continue
        if family == "kt" and _kt_expression_body(lines, index):
            continue
        end = _block_end(lines, index)
        if end is None:
            continue
        if index + 1 <= line <= end:
            return name, index + 1, end
    return None, 0, 0


def _kt_expression_body(lines: list[str], index: int) -> bool:
    """A Kotlin `fun f(...) = expr` has no braces to count: the span is unknown."""
    depth = 0
    for follow in lines[index : index + 6]:
        for char in follow:
            if char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
            elif depth <= 0 and char == "=":
                return True
            elif depth <= 0 and char == "{":
                return False
    return False


def _cs_has_body(lines: list[str], index: int) -> bool:
    """A C# declaration is followed by `{` (same line, or the next non-blank line)."""
    text = lines[index]
    if "{" in text.split(")")[-1]:
        return True
    if text.rstrip().endswith(";"):
        return False
    for follow in lines[index + 1 : index + 6]:
        if follow.strip():
            return follow.strip().startswith("{")
    return False


# ----------------------------------------------------------------- callers


def _same_family(file: str, other: str) -> bool:
    suffix, candidate = Path(file).suffix.lower(), Path(other).suffix.lower()
    return any(suffix in family and candidate in family for family in _FAMILIES) or (
        suffix == candidate
    )


_DEF_WORDS = r"(?:def|function|func|fun)"


def _is_definition(text: str, name: str) -> bool:
    escaped = re.escape(name)
    if re.search(rf"\b{_DEF_WORDS}\s+&?\s*\*?\s*(?:[\w.<>?,]+\.)?{escaped}\b", text):
        return True
    if re.search(rf"(?<![\w$.>]){escaped}\s*[:=]\s*(?:async\s*)?(?:function\b|\()", text):
        return True
    if re.search(
        rf"^\s*(?:(?:async|static|public|private|protected)\s+)*{escaped}\s*\(.*\{{\s*$", text
    ):
        return True
    typed = re.search(rf"^\s*(?:[\w<>\[\],.?]+\s+)+{escaped}\s*\(", text)
    if typed and not text.rstrip().endswith(";"):
        first = text.split()[0] if text.split() else ""
        return first not in _KEYWORDS and "=" not in text[: typed.end()]
    return False


def find_callers(
    root: Path,
    files: list[str],
    name: str,
    *,
    exclude: tuple[str, int, int],
    limit: int = MAX_CALLERS,
) -> list[tuple[str, int]]:
    """Places that call `name(...)` in files of the same language family as `exclude[0]`."""
    if len(name) < 4 or name.lower() in _COMMON_NAMES:
        return []
    own, first, last = exclude
    call = re.compile(rf"(?<![\w$]){re.escape(name)}\s*\(")
    found: list[tuple[str, int]] = []
    scanned = 0
    for file in files:
        if not _same_family(own, file):
            continue
        scanned += 1
        if scanned > MAX_CALLER_FILES:
            break
        path = root / file
        try:
            if path.is_symlink() or path.stat().st_size > MAX_CALLER_FILE_BYTES:
                continue
            raw = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if not call.search(raw):
            continue
        for number, text in enumerate(without_comments(raw, file).splitlines(), 1):
            if not call.search(text) or _is_definition(text, name):
                continue
            if file == own and first <= number <= last:
                continue
            found.append((file, number))
            if len(found) >= limit:
                return found
    return found


# ------------------------------------------------------------ sink context


def line_budget(context_tokens: int) -> int:
    """Lines of code that fit in half of the context window (the rest is for the answer)."""
    return max(60, context_tokens // 2 // _TOKENS_PER_LINE)


def sink_context(
    root: Path,
    file: str,
    line: int,
    files: list[str],
    secrets: set[str],
    *,
    max_lines: int = MAX_CONTEXT_LINES + MAX_CALLERS * (2 * CALLER_RADIUS + 1),
) -> tuple[str, int, list[str]]:
    """Numbered code around a sink, plus up to two caller snippets labelled `file:line`.

    The code is the whole enclosing function (or a window around the line when there is none
    or it is too long); the total number of lines is bounded by `max_lines`.
    """
    name, f_start, f_end = enclosing_function(root, file, line)
    caller_lines = 2 * CALLER_RADIUS + 1
    code_cap = min(MAX_CONTEXT_LINES, max(20, max_lines - MAX_CALLERS * caller_lines))
    if name is None:
        start, end = max(1, line - CONTEXT_RADIUS), line + CONTEXT_RADIUS
    else:
        start, end = f_start, f_end
    if end - start + 1 > code_cap:
        start = max(start, line - code_cap // 2)
        if name is not None:
            start = max(f_start, min(start, f_end - code_cap + 1))
        end = start + code_cap - 1
    code = numbered_code(root, file, start, end, secrets)
    callers: list[str] = []
    spare = max_lines - (end - start + 1)
    if name is not None and spare >= caller_lines:
        hits = find_callers(
            root,
            files,
            name,
            exclude=(file, f_start, f_end),
            limit=min(MAX_CALLERS, spare // caller_lines),
        )
        for caller_file, caller_line in hits:
            first = max(1, caller_line - CALLER_RADIUS)
            snippet = numbered_code(root, caller_file, first, caller_line + CALLER_RADIUS, secrets)
            if snippet:
                callers.append(
                    f"{mask_generic(mask_known(caller_file, secrets))}:{caller_line}\n{snippet}"
                )
    return code, start, callers


# -------------------------------------------------------- endpoint context

_IDENTIFIER = re.compile(r"^[A-Za-z_$][\w$]*$")
_LAST_IDENTIFIER = re.compile(r"([A-Za-z_$][\w$]*)\W*$")
_CALL = re.compile(r"(?<![\w$])([A-Za-z_$][\w$]*)\s*\(")
_NEW_BEFORE = re.compile(r"\bnew\s+$")


def split_handler(handler: str) -> tuple[str | None, str | None]:
    """`(class, method)` of a handler such as `UserController@show` or `Users.list`.

    `(None, None)` when the text is not a plain identifier path (an inline function);
    `(None, name)` when there is no class part.
    """
    handler = (handler or "").strip()
    cut = max(handler.rfind("@"), handler.rfind("."))
    if cut < 0:
        return (None, handler) if _IDENTIFIER.match(handler) else (None, None)
    left, method = handler[:cut], handler[cut + 1 :]
    if not _IDENTIFIER.match(method):
        return None, None
    match = _LAST_IDENTIFIER.search(left)
    return (match.group(1) if match else None), method


def _readable(root: Path, file: str) -> str | None:
    path = root / file
    try:
        if path.is_symlink() or path.stat().st_size > MAX_CALLER_FILE_BYTES:
            return None
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def find_definition(
    root: Path,
    files: list[str],
    name: str,
    *,
    near: str,
    class_name: str | None = None,
) -> tuple[str, int, int] | None:
    """Span `(file, start, end)` of the function or method `name` in files of `near`'s family."""
    candidates = [f for f in files if _same_family(near, f)][:MAX_CALLER_FILES]
    if class_name:
        candidates.sort(key=lambda f: Path(f).stem != class_name)  # stable: keeps the order
    for file in candidates:
        raw = _readable(root, file)
        if raw is None or name not in raw:
            continue
        for number, text in enumerate(without_comments(raw, file).splitlines(), 1):
            if name not in text or not _is_definition(text, name):
                continue
            found, start, end = enclosing_function(root, file, number)
            if found == name:
                return file, start, end
    return None


def called_names(code: str) -> list[str]:
    """Names called in `code` (`name(`, `->name(`, `::name(`), without strings, in order."""
    seen: list[str] = []
    for line in _STRING.sub('""', code).splitlines():
        for match in _CALL.finditer(line):
            name = match.group(1)
            if (
                len(name) < 4
                or name in seen
                or name in _KEYWORDS
                or name.lower() in _COMMON_NAMES
                or _NEW_BEFORE.search(line[: match.start()])
            ):
                continue
            seen.append(name)
    return seen


@dataclass
class EndpointContext:
    """What the endpoint review (T2) is shown: handler, route declaration and callees."""

    handler_file: str
    handler_first: int
    handler_code: str
    resolved: bool
    route_code: str = ""
    route_first: int = 0
    callees: list[str] = field(default_factory=list)


def endpoint_context(
    root: Path,
    item: dict[str, Any],
    files: list[str],
    secrets: set[str],
    *,
    max_lines: int,
) -> EndpointContext:
    """Real handler of an endpoint, its route declaration and the project functions it calls."""
    file, line = item["file"], int(item["line"])
    window = (max(1, line - CONTEXT_RADIUS), line + CONTEXT_RADIUS)
    if file.endswith(".py"):
        start, end = window
        block = python_block(root, file, line, classes=True)
        if block is not None:
            _, start, end = block
        return _finish(root, files, secrets, file, start, end, True, None, max_lines, "", 0)

    class_name, method = split_handler(str(item.get("handler", "")))
    route_first, route_last = 0, 0
    target, start, end, resolved = file, window[0], window[1], method is None
    if method is not None:
        name, f_start, f_end = enclosing_function(root, file, line)
        if name == method:
            target, start, end, resolved = file, f_start, f_end, True
        else:
            found = find_definition(root, files, method, near=file, class_name=class_name)
            if found is not None:
                target, (start, end), resolved = found[0], found[1:], True
                route_first = max(1, line - ROUTE_RADIUS_BEFORE)
                route_last = line + ROUTE_RADIUS_AFTER
    route = numbered_code(root, file, route_first, route_last, secrets) if route_first else ""
    return _finish(
        root, files, secrets, target, start, end, resolved, method, max_lines, route, route_first
    )


def _finish(
    root: Path,
    files: list[str],
    secrets: set[str],
    target: str,
    start: int,
    end: int,
    resolved: bool,
    method: str | None,
    max_lines: int,
    route: str,
    route_first: int,
) -> EndpointContext:
    end = min(end, start + MAX_CONTEXT_LINES - 1)
    code = numbered_code(root, target, start, end, secrets)
    context = EndpointContext(
        handler_file=mask_generic(mask_known(target, secrets)),
        handler_first=start,
        handler_code=code,
        resolved=resolved,
        route_code=route,
        route_first=route_first,
    )
    used = len(code.splitlines()) + len(route.splitlines())
    lookups = 0
    for name in called_names(code):
        if len(context.callees) >= MAX_CALLEES or lookups >= _MAX_CALLEE_LOOKUPS:
            break
        if name == method:
            continue
        lookups += 1
        found = find_definition(root, files, name, near=target)
        if found is None:
            continue
        c_file, c_start, c_end = found
        if c_file == target and c_start <= end and c_end >= start:
            continue
        snippet = numbered_code(
            root, c_file, c_start, min(c_end, c_start + CALLEE_LINES - 1), secrets
        )
        size = len(snippet.splitlines())
        if not snippet or used + size > max_lines:
            continue
        used += size
        label = mask_generic(mask_known(c_file, secrets))
        context.callees.append(f"{label}:{c_start}\n{snippet}")
    return context
