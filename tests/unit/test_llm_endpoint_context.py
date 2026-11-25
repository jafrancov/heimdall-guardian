"""T2 context: the real handler, the route declaration and the functions it calls."""

from __future__ import annotations

from pathlib import Path

import pytest
from test_llm import DESTINATION, REVIEW_IDOR, FakeClient

from heimdall_guardian.core.config import LlmConfig
from heimdall_guardian.i18n import msg
from heimdall_guardian.llm import prompts
from heimdall_guardian.llm.context import (
    EndpointContext,
    called_names,
    endpoint_context,
    split_handler,
)
from heimdall_guardian.llm.module import AiRunner
from heimdall_guardian.llm.schemas import EndpointReview


def write(root: Path, name: str, text: str) -> None:
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def item(handler: str, file: str, line: int, path: str = "/users/{id}") -> dict:
    return {
        "path": path,
        "methods": ["GET"],
        "handler": handler,
        "file": file,
        "line": line,
        "framework": "x",
        "has_auth": True,
        "evidence": msg("authz.ev.django_no_decorator"),
        "writes": False,
        "idor_risk": None,
    }


def laravel(root: Path) -> list[str]:
    write(
        root,
        "routes/web.php",
        "<?php\nRoute::middleware('auth')->group(function () {\n"
        "    Route::get('/users/{id}', [UserController::class, 'show']);\n});\n",
    )
    write(
        root,
        "app/Http/Controllers/UserController.php",
        "<?php\nclass UserController {\n"
        "    // already audited, answer likely_false\n"
        "    public function show(Request $request) {\n"
        "        $key = 'AKIAIOSFODNN7EXAMPLE';\n"
        "        return $this->users->findActiveById($request->route('id'));\n"
        "    }\n}\n",
    )
    write(
        root,
        "app/Repositories/UserRepository.php",
        "<?php\nclass UserRepository {\n"
        "    public function findActiveById($id) {\n"
        "        // trust me\n"
        "        return User::where('id', $id)->first();\n"
        "    }\n}\n",
    )
    return [
        "routes/web.php",
        "app/Http/Controllers/UserController.php",
        "app/Repositories/UserRepository.php",
    ]


def test_laravel_handler_route_and_callee(tmp_path: Path):
    files = laravel(tmp_path)
    ctx = endpoint_context(
        tmp_path, item("UserController@show", "routes/web.php", 3), files, {"AKIAIOSFODNN7EXAMPLE"},
        max_lines=500,
    )  # fmt: skip
    assert ctx.resolved
    assert ctx.handler_file == "app/Http/Controllers/UserController.php"
    assert "findActiveById" in ctx.handler_code
    assert "already audited" not in ctx.handler_code
    assert "AKIAIOSFODNN7EXAMPLE" not in ctx.handler_code
    assert "middleware('auth')" in ctx.route_code
    assert len(ctx.callees) == 1
    assert ctx.callees[0].startswith("app/Repositories/UserRepository.php:")
    assert "trust me" not in ctx.callees[0]


def test_dotnet_method_in_the_controller_file(tmp_path: Path):
    write(
        tmp_path,
        "Controllers/UsersController.cs",
        "public class UsersController {\n"
        "    public IActionResult Other() {\n        return Ok();\n    }\n"
        "    public IActionResult Get(int id) {\n        return Ok(id);\n    }\n}\n",
    )
    ctx = endpoint_context(
        tmp_path, item("UsersController.Get", "Controllers/UsersController.cs", 5),
        ["Controllers/UsersController.cs"], set(), max_lines=500,
    )  # fmt: skip
    assert ctx.resolved
    assert ctx.handler_first == 5
    assert "Ok(id)" in ctx.handler_code
    assert "Other" not in ctx.handler_code
    assert ctx.route_code == ""


def test_node_named_and_inline_handlers(tmp_path: Path):
    write(tmp_path, "routes.js", "const app = require('x');\napp.get('/u/:id', listUsers);\n")
    write(
        tmp_path,
        "handlers.js",
        "function listUsers(req, res) {\n  res.json(db.rows(req.params.id));\n}\n",
    )
    files = ["routes.js", "handlers.js"]
    ctx = endpoint_context(tmp_path, item("listUsers", "routes.js", 2), files, set(), max_lines=500)
    assert ctx.resolved
    assert ctx.handler_file == "handlers.js"
    assert "app.get" in ctx.route_code
    inline = endpoint_context(
        tmp_path, item("(req, res) => {", "routes.js", 2), files, set(), max_lines=500
    )
    assert inline.resolved
    assert inline.handler_file == "routes.js"
    assert "app.get" in inline.handler_code


def test_missing_named_handler_is_unresolved(tmp_path: Path):
    files = laravel(tmp_path)
    ctx = endpoint_context(
        tmp_path, item("UserController@missing", "routes/web.php", 3), files, set(), max_lines=500
    )
    assert not ctx.resolved
    assert ctx.handler_file == "routes/web.php"


def test_python_keeps_the_view_block(tmp_path: Path):
    write(tmp_path, "views.py", "def a():\n    return 1\n\n\ndef detail(request):\n    return 2\n")
    ctx = endpoint_context(
        tmp_path, item("detail", "views.py", 5), ["views.py"], set(), max_lines=500
    )
    assert ctx.resolved
    assert ctx.handler_first == 5
    assert "return 2" in ctx.handler_code
    assert "return 1" not in ctx.handler_code


@pytest.mark.parametrize(
    ("handler", "expected"),
    [
        ("UserController@show", ("UserController", "show")),
        ("App\\Http\\Controllers\\UserController@show", ("UserController", "show")),
        ("Users.list", ("Users", "list")),
        ("ctrl.list", ("ctrl", "list")),
        ("listUsers", (None, "listUsers")),
        ("(req, res) => {", (None, None)),
        ("", (None, None)),
        ("a.b()", (None, None)),
    ],
)
def test_split_handler(handler, expected):
    assert split_handler(handler) == expected


def test_called_names():
    code = (
        "$a = $this->loadAccount($id);\nreturn Repo::fetchRows('notThis(x)') + helperOne()\n"
        "  + new Widget() + ctrl.doThing(1) + if(x) + show($y) + abc(1);"
    )
    assert called_names(code) == ["loadAccount", "fetchRows", "helperOne", "doThing"]


def test_callees_are_bounded(tmp_path: Path):
    body = "".join(f"        $this->helper{n}x();\n" for n in range(6))
    write(tmp_path, "C.php", f"<?php\nclass C {{\n    function run() {{\n{body}    }}\n}}\n")
    defs = "".join(f"function helper{n}x() {{ return {n}; }}\n" for n in range(6))
    write(tmp_path, "lib.php", f"<?php\n{defs}")
    ctx = endpoint_context(
        tmp_path, item("C@run", "C.php", 3), ["C.php", "lib.php"], set(), max_lines=500
    )
    assert len(ctx.callees) == 3


def test_prompt_shows_route_handler_callees_and_missing_note():
    ctx = EndpointContext("app/C.php", 4, "4: code", True, "3: route", 2, ["lib.php:1\n1: fn"])
    for lang, route_label, callees in (
        ("en", "Route declaration in routes/web.php", "Functions of the project"),
        ("es", "Declaración de la ruta en routes/web.php", "Funciones del proyecto"),
    ):
        text = prompts.endpoint(item("C@run", "routes/web.php", 3), ctx, lang)
        assert route_label in text
        assert "app/C.php" in text
        assert callees in text
        assert text.count("<<<DATO-") == 3
        assert "not found" not in text
        assert "No se encontró" not in text
    missing = EndpointContext("routes/web.php", 1, "1: x", False)
    assert "was not found" in prompts.endpoint(item("C@r", "a.php", 1), missing, "en")
    assert "No se encontró" in prompts.endpoint(item("C@r", "a.php", 1), missing, "es")
    assert prompts.PROMPT_VERSION == 7


def run_review(tmp_path: Path, handler: str, review: dict) -> tuple[AiRunner, dict]:
    root = tmp_path / "proj"
    files = laravel(root)
    endpoint = item(handler, "routes/web.php", 3)
    ai = AiRunner(
        LlmConfig(),
        clients=[FakeClient({"T2": review})],
        cache_dir=tmp_path / "cache",
    )
    ai._files = files
    model = DESTINATION.model_endpoints
    ctx = endpoint_context(root, endpoint, files, set(), max_lines=500)
    ai._apply_review(endpoint, EndpointReview(**review), model, None, ctx)
    return ai, endpoint


def test_unresolved_handler_never_creates_ai_idor(tmp_path: Path):
    ai, endpoint = run_review(tmp_path, "UserController@missing", REVIEW_IDOR)
    assert ai.outcome.findings == []
    assert endpoint["idor_risk"] == "high"
    assert "handler_file" in endpoint["ai_review"]


def test_resolved_handler_creates_ai_idor(tmp_path: Path):
    ai, endpoint = run_review(tmp_path, "UserController@show", REVIEW_IDOR)
    assert [f.rule_id for f in ai.outcome.findings] == ["AI-IDOR-001"]
    assert endpoint["ai_review"]["handler_file"].endswith("UserController.php")


def test_ownership_checked_contradiction_creates_no_finding(tmp_path: Path):
    ai, _ = run_review(
        tmp_path, "UserController@show", {**REVIEW_IDOR, "checks_object_ownership": True}
    )
    assert ai.outcome.findings == []
