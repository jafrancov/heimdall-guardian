"""H4: the endpoint inventory must match the real routes of each fixture."""

from __future__ import annotations

from pathlib import Path

from helpers import FakeAdapter, make_finding

from heimdall_guardian.adapters.base import AdapterResult
from heimdall_guardian.authz.adapter import AuthzAdapter
from heimdall_guardian.authz.django import DjangoExtractor
from heimdall_guardian.authz.dotnet import DotnetExtractor
from heimdall_guardian.authz.laravel import LaravelExtractor
from heimdall_guardian.authz.node import NodeExtractor
from heimdall_guardian.authz.php import (
    HtaccessIndex,
    PhpExtractor,
    _harmless_helpers,
    _is_script,
    top_level,
)
from heimdall_guardian.core.endpoints import Endpoint, join_path, strip_comments
from heimdall_guardian.core.files import Exclusions, scan_tree
from heimdall_guardian.core.finding import Confidence, Severity
from heimdall_guardian.core.runner import build_plan, run_scan
from heimdall_guardian.i18n import render, text_of
from heimdall_guardian.report.html import render_html

ANY = ["*"]


def inventory(extractor_class, root: Path) -> dict[tuple[str, str], tuple[bool | None, bool]]:
    """{(methods, route): (has_auth, write)} as the extractor sees it."""
    extractor = extractor_class(root, scan_tree(root, Exclusions()).files)
    endpoints: list[Endpoint] = extractor.extract()
    assert extractor.notes == []
    keys = [(",".join(e.methods), e.path) for e in endpoints]
    assert len(keys) == len(set(keys)), "duplicate endpoints"
    return {key: (e.has_auth, e.writes) for key, e in zip(keys, endpoints, strict=True)}


def test_django_inventory_matches_real_routes(project):
    assert inventory(DjangoExtractor, project("authz_django")) == {
        ("*", "/admin"): (True, True),
        ("*", "/"): (False, False),  # FBV without decorator
        ("GET", "/expedientes"): (True, False),  # mixin inherited from a local base class
        ("GET,POST", "/expedientes/nuevo"): (False, True),  # CreateView without mixin
        ("POST", "/expedientes/<int:pk>/borrar"): (False, True),  # @require_POST, no auth
        ("*", "/expedientes/<int:pk>/editar"): (True, False),  # @permission_required
        ("*", "/expedientes/exportar"): (True, False),
        ("GET", "/detalle/<int:pk>"): (False, False),
        ("*", "/reporte"): (True, False),  # login_required(...) applied in urls.py
        # DRF: without permission_classes it inherits IsAuthenticated from settings.
        ("GET,POST", "/api/predios"): (True, True),
        ("GET,PUT,PATCH,DELETE", "/api/predios/{pk}"): (True, True),
        ("GET", "/api/publico"): (False, False),  # explicit AllowAny
        ("GET", "/api/publico/{pk}"): (False, False),
        ("POST", "/api/importar"): (False, True),
        ("GET", "/api/estado"): (True, False),
    }


def test_django_drf_is_open_without_restrictive_default(project):
    root = project("authz_django")
    (root / "config" / "settings.py").write_text('ROOT_URLCONF = "config.urls"\n')
    found = inventory(DjangoExtractor, root)
    assert found[("GET,POST", "/api/predios")] == (False, True)
    assert found[("GET", "/api/estado")] == (False, False)


def test_django_login_required_middleware_protects_plain_views(project):
    root = project("authz_django")
    settings = root / "config" / "settings.py"
    settings.write_text(
        settings.read_text()
        + 'MIDDLEWARE = ["django.contrib.auth.middleware.LoginRequiredMiddleware"]\n'
    )
    found = inventory(DjangoExtractor, root)
    assert found[("*", "/")] == (True, False)
    assert found[("POST", "/expedientes/<int:pk>/borrar")] == (True, True)
    assert found[("GET", "/api/publico")] == (False, False)  # DRF decides on its own


def test_dotnet_inventory_matches_real_routes(project):
    assert inventory(DotnetExtractor, project("authz_dotnet")) == {
        ("GET", "/api/Pagos"): (True, False),  # [Authorize] on the controller
        ("GET", "/api/Pagos/{id}"): (True, False),
        ("POST", "/api/Pagos/importar"): (False, True),  # [AllowAnonymous] on the action
        ("GET", "/api/catalogos"): (False, False),
        ("DELETE", "/api/catalogos/{id}"): (True, True),  # [Authorize] on the action
        ("*", "/Home/Index"): (False, False),  # conventional MVC
        ("POST", "/Home/Guardar"): (False, True),
        ("GET", "/salud"): (False, False),  # Minimal API
        ("POST", "/webhook"): (True, True),  # .RequireAuthorization()
    }


def test_dotnet_global_policy_protects_everything_but_allow_anonymous(project):
    root = project("authz_dotnet")
    program = root / "Program.cs"
    program.write_text(
        "builder.Services.AddAuthorization(o => { o.FallbackPolicy = new "
        "AuthorizationPolicyBuilder().RequireAuthenticatedUser().Build(); });\n"
        + program.read_text()
    )
    found = inventory(DotnetExtractor, root)
    assert found[("GET", "/api/catalogos")] == (True, False)
    assert found[("*", "/Home/Index")] == (True, False)
    assert found[("POST", "/api/Pagos/importar")] == (False, True)


def test_laravel_inventory_matches_real_routes(project):
    assert inventory(LaravelExtractor, project("authz_laravel")) == {
        ("GET", "/"): (False, False),
        ("POST", "/login"): (False, True),
        ("GET", "/expedientes"): (True, False),  # group with auth middleware + prefix
        ("POST", "/expedientes"): (True, True),
        ("DELETE", "/expedientes/anexos/{id}"): (True, True),  # nested group
        ("GET", "/reportes/mensual"): (False, False),  # throttle is not authentication
        ("GET", "/reportes/anual"): (True, False),  # chained ->middleware('auth')
        ("PUT", "/perfil"): (True, True),
        ("GET", "/tablero"): (True, False),  # middleware in the controller constructor
        ("GET", "/api/predios"): (False, False),  # expanded apiResource
        ("POST", "/api/predios"): (False, True),
        ("GET", "/api/predios/{id}"): (False, False),
        ("PUT", "/api/predios/{id}"): (False, True),
        ("DELETE", "/api/predios/{id}"): (False, True),
        ("PUT,PATCH", "/api/usuarios/{id}"): (True, True),
    }


def test_plain_php_inventory_matches_public_files(project):
    assert inventory(PhpExtractor, project("authz_php")) == {
        ("*", "/index.php"): (True, False),  # checks $_SESSION
        ("*", "/login.php"): (False, True),
        ("*", "/reportes/ver.php"): (True, False),  # includes includes/auth.php
        ("*", "/reportes/borrar.php"): (False, True),
        ("*", "/consulta.php"): (False, False),
        # includes/auth.php runs header() at top level, so it is a handler that checks the session.
        ("*", "/includes/auth.php"): (True, False),
        # includes/funciones.php only defines a function: not an endpoint.
        ("*", "/lib/actions.php"): (False, True),  # AJAX handler in a "library" folder
        ("*", "/lib/upload.php"): (False, True),
        # Includes lib/verification_model.php, which resolves to a file without a session check.
        ("*", "/lib/report_ajax.php"): (False, True),
        ("*", "/api/basic.php"): (True, False),  # HTTP basic authentication
        ("*", "/tasks/build_report.php"): (False, True),  # scheduled script in the webroot
        ("*", "/public/page.php"): (False, False),  # the deny only covers *.log files
        ("*", "/gate/open.php"): (False, True),  # the only file the allowlist leaves open
        ("*", "/parent/child/page.php"): (False, False),  # inner "Require all granted" wins
        # closed/handler.php: FilesMatch denies every .php file.
        # gate/hidden.php: the allowlist denies it.
        # uploads/shell.php: the PHP engine is off, it is served as text.
        # parent/top.php: the parent denies everything.
        # models/report_model.php: a class whose methods echo is not an endpoint.
        # tasks/cli_job.php: command-line-only guard.
        # private/tool.php: .htaccess denies the whole folder.
        # config.php: only define/ini_set.
        # settings.php: only calls a helper it declares itself.
    }


def _access(tmp_path: Path, htaccess: str, name: str = "a.php") -> str:
    (tmp_path / ".htaccess").write_text(htaccess)
    return HtaccessIndex(tmp_path).access(name)


def test_htaccess_files_blocks_match_by_name(tmp_path):
    rules = '<Files "a.php">\nRequire all denied\n</Files>\n'
    assert _access(tmp_path, rules, "a.php") == "denied"
    assert HtaccessIndex(tmp_path).access("b.php") == "reachable"
    assert HtaccessIndex(tmp_path).access("sub/a.php") == "denied"
    assert _access(tmp_path, '<Files ~ "\\.inc$">\nDeny from all\n</Files>', "x.inc") == "denied"
    assert HtaccessIndex(tmp_path).access("x.php") == "reachable"


def test_htaccess_invalid_regex_and_comments_are_ignored(tmp_path):
    assert _access(tmp_path, '<FilesMatch "(">\nRequire all denied\n</FilesMatch>') == "reachable"
    assert _access(tmp_path, "# Require all denied\n") == "reachable"
    assert _access(tmp_path, "<Location /x>\nRequire all denied\n</Location>") == "reachable"


def test_htaccess_engine_off_variants(tmp_path):
    for line in (
        "php_admin_flag engine off",
        "php_value engine off",
        "RemoveType .php",
        "SetHandler none",
        "SetHandler default-handler",
    ):
        assert _access(tmp_path, line) == "no_php", line
    assert _access(tmp_path, "<FilesMatch x>\nSetHandler none\n</FilesMatch>") == "reachable"
    assert _access(tmp_path, "Order allow,deny\nDeny from all\nAllow from all") == "reachable"


def test_plain_php_script_has_its_own_evidence(project):
    root = project("authz_php")
    extractor = PhpExtractor(root, scan_tree(root, Exclusions()).files)
    found = {e.path: e for e in extractor.extract()}
    assert found["/tasks/build_report.php"].evidence["code"] == "authz.ev.php_script"
    assert found["/lib/upload.php"].evidence["code"] == "authz.ev.php_none"
    assert found["/api/basic.php"].evidence["code"] == "authz.ev.php_basic_auth"


def test_php_top_level_drops_class_and_function_bodies():
    code, html = top_level("<?php\nclass A extends B { function f() { echo 1; } }\n$x = 1;\n?>\n")
    assert "echo" not in code
    assert "$x = 1" in code
    assert not html


def test_php_top_level_drops_closures_and_arrow_functions():
    code, _ = top_level("<?php $f = function ($a) use ($b) { echo $a; }; $g = fn($x) => print($x);")
    assert "echo" not in code
    assert "print" not in code
    assert "$f =" in code


def test_php_top_level_ignores_braces_inside_strings():
    code, _ = top_level("<?php function f() { $s = '}'; echo \"{\"; } echo 'after';")
    assert "echo" in code
    assert "f()" not in code


def test_php_top_level_detects_inline_html_and_ignores_trailing_close_tag():
    assert top_level("<?php $x = 1; ?>\n<p>hi</p>")[1] is True
    assert top_level("<?php $x = 1; ?>\n  \n")[1] is False
    assert top_level("<?php function f() { ?><p>x</p><?php } ?>")[1] is False
    assert "echo" in top_level("<p><?= $name ?></p>")[0]


def test_php_top_level_survives_unbalanced_braces():
    code, _ = top_level("<?php function broken() { if (1) { echo 1;")
    assert "echo" not in code


def test_each_unauthenticated_endpoint_gets_its_own_finding(project):
    root = project("authz_laravel")
    result = run_scan(build_plan(root, profile="standard"), adapters=[AuthzAdapter()])
    open_endpoints = [e for e in result.endpoints if e["has_auth"] is False]
    assert len(result.findings) == len(open_endpoints) == 8
    login = next(f for f in result.findings if text_of(f, "title").endswith("POST /login"))
    # A name suggesting a public route only lowers the confidence; it does not exempt it.
    assert (login.severity, login.confidence) == (Severity.CRITICAL, Confidence.LOW)


def test_helpers():
    assert join_path("", "api/", "/x/") == "/api/x"
    assert join_path("", "") == "/"
    cleaned = strip_comments('a = "// no es comentario"; // sí lo es\n/* y\nesto */ b')
    assert cleaned.split("\n")[0].rstrip() == 'a = "// no es comentario";'
    assert cleaned.count("\n") == 2
    assert cleaned.rstrip().endswith("b")


def test_scan_reports_inventory_findings_and_replaces_superseded_rules(project):
    root = project("authz_django")
    views = (root / "padron" / "views.py").read_text().splitlines()
    crear = views.index("class Crear(CreateView):") + 1
    lista = views.index("class Lista(Protegida, ListView):") + 1
    huerfana = views.index("class Protegida(LoginRequiredMixin):") + 1
    rules = FakeAdapter(
        "opengrep",
        AdapterResult(
            findings=[
                # Covered by the inventory: they are discarded (one was a false positive).
                make_finding("opengrep", "DJ-AUTH-002", "padron/views.py", "Crear", Severity.HIGH),
                make_finding("opengrep", "DJ-AUTH-002", "padron/views.py", "Lista", Severity.HIGH),
                # It is on no route: the rule's finding is kept.
                make_finding("opengrep", "DJ-AUTH-002", "padron/views.py", "Otra", Severity.HIGH),
                make_finding("opengrep", "DJ-SQL-001", "padron/views.py", "sql", Severity.HIGH),
            ]
        ),
    )
    for finding, line in zip(rules._result.findings, (crear, lista, huerfana, 1), strict=True):
        finding.line_start = finding.line_end = line

    result = run_scan(build_plan(root, profile="standard"), adapters=[rules, AuthzAdapter()])

    by_rule: dict[str, list] = {}
    for finding in result.findings:
        by_rule.setdefault(finding.rule_id, []).append(finding)
    assert [f.line_start for f in by_rule["DJ-AUTH-002"]] == [huerfana]
    assert len(by_rule["DJ-SQL-001"]) == 1
    writes = {text_of(f, "title").split(": ", 1)[1] for f in by_rule["AUTHZ-001"]}
    assert writes == {
        "GET, POST /expedientes/nuevo",
        "POST /expedientes/<int:pk>/borrar",
        "POST /api/importar",
    }
    assert all(f.severity is Severity.CRITICAL for f in by_rule["AUTHZ-001"])
    assert all(f.severity is Severity.HIGH for f in by_rule["AUTHZ-002"])
    assert len(by_rule["AUTHZ-002"]) == 4
    assert not any("parcial" in render(text) for text in result.limitations)

    payload = result.to_dict()
    assert len(payload["endpoints"]) == 15
    html = render_html(payload)
    assert "Inventario de endpoints" in html
    assert "/expedientes/&lt;int:pk&gt;/borrar" in html


def test_broken_extractor_is_reported_and_does_not_stop_the_scan(project, monkeypatch):
    def explode(self):
        raise RecursionError

    monkeypatch.setattr(DjangoExtractor, "extract", explode)
    result = run_scan(
        build_plan(project("authz_django"), profile="standard"), adapters=[AuthzAdapter()]
    )
    assert [tool.status for tool in result.tools] == ["ran"]
    assert any("Django falló (RecursionError)" in render(text) for text in result.limitations)


def node_endpoints(root: Path) -> dict[tuple[str, str], Endpoint]:
    extractor = NodeExtractor(root, scan_tree(root, Exclusions()).files)
    found = {(",".join(e.methods), e.path): e for e in extractor.extract()}
    node_endpoints.notes = extractor.notes  # type: ignore[attr-defined]
    return found


def test_node_inventory_matches_real_routes(project):
    assert inventory(NodeExtractor, project("authz_node")) == {
        # Express: server.js (routes before and after `app.use(authenticate)`).
        ("GET", "/health"): (False, False),
        ("POST", "/login"): (False, True),  # passport.authenticate('local') is the login
        ("POST", "/importar"): (False, True),  # multer does not authenticate
        ("GET", "/perfil"): (True, False),  # ensureLoggedIn() on the route
        ("DELETE", "/cuentas/:id"): (None, True),  # checkPermissions: unknown middleware
        ("GET", "/tarde"): (True, False),  # declared after app.use(authenticate)
        ("PUT", "/ajustes"): (True, True),
        # Router from another file with `router.use(requireAuth)` midway through the file.
        ("GET", "/api/users/directorio"): (False, False),  # before the use
        ("GET", "/api/users"): (True, False),
        ("POST", "/api/users"): (True, True),
        ("GET", "/api/users/:id"): (True, False),  # chained router.route()
        ("PUT", "/api/users/:id"): (True, True),
        ("DELETE", "/api/users/:id"): (True, True),
        # Authentication at mount time (app.use('/api/reports', authenticate, router)).
        ("GET", "/api/reports/mensual"): (True, False),
        ("POST", "/api/reports/regenerar"): (True, True),  # rateLimit is harmless
        ("GET", "/public/estado"): (False, False),
        ("POST", "/public/contacto"): (False, True),
        ("GET", "/api/admin/bitacora"): (None, False),  # router.use(checkRole(...))
        ("POST", "/api/admin/purgar"): (None, True),
        # NestJS: global guard (APP_GUARD) and global prefix v1.
        ("POST", "/v1/auth/login"): (False, True),  # @Public()
        ("POST", "/v1/auth/refresh"): (True, True),
        ("GET", "/v1/auth/me"): (True, False),
        ("GET", "/v1/cases"): (True, False),  # @UseGuards on the class
        ("GET", "/v1/cases/:id"): (True, False),
        ("POST", "/v1/cases"): (True, True),
        ("DELETE", "/v1/cases/:id"): (True, True),
        ("POST", "/v1/billing/charge"): (True, True),  # @UseGuards on the method
        ("GET", "/v1/billing/plans"): (True, False),
        ("GET", "/v1/billing/webhook-status"): (False, False),
        ("GET", "/v1/health"): (False, False),  # @SkipAuth() on the class
    }


def test_node_handlers_lines_and_files(project):
    found = node_endpoints(project("authz_node"))
    assert node_endpoints.notes == []  # type: ignore[attr-defined]
    users = found[("GET", "/api/users")]
    assert (users.handler, users.file, users.framework) == ("ctrl.list", "routes/users.js", "node")
    assert found[("GET", "/api/admin/bitacora")].handler == "<anonymous>"
    assert found[("PUT", "/ajustes")].handler == "guardarAjustes"  # asyncHandler(...) is unwrapped
    assert "requireAuth" in str(users.evidence)
    nest = found[("DELETE", "/v1/cases/:id")]
    assert (nest.handler, nest.framework, nest.file) == (
        "CasesController.remove",
        "nestjs",
        "src/cases/cases.controller.ts",
    )
    assert nest.line == 25  # method line
    assert nest.covers == [6]  # and the class is covered for the rules


def test_node_mount_prefixes_nest_and_resolve_across_files(tmp_path):
    (tmp_path / "routes").mkdir()
    (tmp_path / "package.json").write_text("{}")
    (tmp_path / "routes" / "index.js").write_text(
        "const router = require('express').Router();\n"
        "router.use('/v2', require('./items'));\n"
        "module.exports = router;\n"
    )
    (tmp_path / "routes" / "items.ts").write_text(
        "import { Router } from 'express';\nexport const items = Router();\n"
        "items.get('/', list);\nexport default items;\n"
    )
    (tmp_path / "app.js").write_text(
        "const express = require('express');\nconst api = require('./routes');\n"
        "const app = express();\napp.use('/api', api);\n"
    )
    found = node_endpoints(tmp_path)
    assert list(found) == [("GET", "/api/v2")]
    assert node_endpoints.notes == []  # type: ignore[attr-defined]


def test_node_unresolved_router_keeps_routes_without_prefix_and_notes(tmp_path):
    (tmp_path / "app.js").write_text(
        "const express = require('express');\nconst app = express();\n"
        "const remote = require('some-package');\napp.use('/ext', remoteRouter);\n"
    )
    (tmp_path / "orphan.js").write_text(
        "const router = require('express').Router();\nrouter.post('/huerfana', run);\n"
    )
    found = node_endpoints(tmp_path)
    assert found[("POST", "/huerfana")].has_auth is False
    notes = " ".join(render(n) for n in node_endpoints.notes)  # type: ignore[attr-defined]
    assert "orphan.js" in notes
    assert "remoteRouter" in notes
    assert "/ext" in notes


def test_node_nest_without_global_guard_and_conflicting_public(project):
    root = project("authz_node")
    module = root / "src" / "app.module.ts"
    module.write_text(
        module.read_text().replace("{ provide: APP_GUARD, useClass: JwtAuthGuard }", "")
    )
    found = node_endpoints(root)
    assert found[("POST", "/v1/auth/refresh")].has_auth is False
    assert found[("GET", "/v1/auth/me")].has_auth is False
    assert found[("GET", "/v1/cases")].has_auth is True  # the class guard applies
    assert found[("POST", "/v1/billing/charge")].has_auth is True
    assert found[("GET", "/v1/billing/plans")].has_auth is False
    # @SkipAuth() with no contradicting guards: public.
    assert found[("GET", "/v1/health")].has_auth is False
    cases = root / "src" / "cases" / "cases.controller.ts"
    cases.write_text(cases.read_text().replace("  @Get()\n", "  @Public()\n  @Get()\n"))
    assert node_endpoints(root)[("GET", "/v1/cases")].has_auth is None  # @Public vs guard


def test_node_unknown_middleware_gives_none_and_odd_files_do_not_raise(tmp_path):
    (tmp_path / "app.js").write_text(
        "const app = require('express')();\n"
        "app.get('/a', miSeguridad, h);\napp.get('/b', h);\napp.get(RUTA, h);\n"
        "app.use('/c', verificador);\napp.get('/c/x', h);\n"
    )
    (tmp_path / "bundle.min.js").write_text("!function(e){" + "a(" * 500 + "}")
    (tmp_path / "roto.ts").write_text("@Controller('x') export class { @Get( ")
    (tmp_path / "tipos.d.ts").write_text("declare const router: Router; router.get('/z', h);")
    found = node_endpoints(tmp_path)
    assert {key: e.has_auth for key, e in found.items()} == {
        ("GET", "/a"): None,
        ("GET", "/b"): False,
        ("GET", "/c/x"): None,  # use('/c', unknown) covers /c/x
    }
    assert any(
        "ruta no literal" in render(note)
        for note in node_endpoints.notes  # type: ignore[attr-defined]
    )


def test_scan_of_node_fixture_reports_unauthenticated_routes(project):
    root = project("authz_node")
    result = run_scan(build_plan(root, profile="standard"), adapters=[AuthzAdapter()])
    titles = {text_of(f, "title") for f in result.findings}
    assert "Endpoint de escritura sin autenticación: POST /importar" in titles
    assert "Endpoint de lectura sin autenticación: GET /api/users/directorio" in titles
    assert not any("/v1/cases" in title for title in titles)
    assert all(f.rule_id in ("AUTHZ-001", "AUTHZ-002") for f in result.findings)
    # Routes with unknown auth (None) produce no finding; those public by decorator do.
    assert len(result.findings) == 9


def test_plain_php_include_guard_is_the_resolved_file(project):
    root = project("authz_php")
    extractor = PhpExtractor(root, scan_tree(root, Exclusions()).files)
    found = {e.path: e for e in extractor.extract()}
    assert found["/reportes/ver.php"].evidence["params"]["file"] == "includes/auth.php"
    assert found["/lib/report_ajax.php"].evidence["code"] == "authz.ev.php_none"


def test_php_calls_inside_define_are_not_work():
    from heimdall_guardian.authz.php import _is_script

    assert not _is_script("define('A', getenv_x('A')); const B = f();")
    assert _is_script("$x = do_it();")


def test_php_script_calling_its_own_main_function_is_work():
    text = "<?php\nrun();\nfunction run() { $m = new Model(); $m->send(); }\n"
    assert _is_script(top_level(text)[0], _harmless_helpers(text))
    config = "<?php\nfunction env_or($n, $d) { return getenv($n) ?: $d; }\n$t = env_or('X', 1);\n"
    assert not _is_script(top_level(config)[0], _harmless_helpers(config))
