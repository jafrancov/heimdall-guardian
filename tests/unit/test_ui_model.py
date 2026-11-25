from __future__ import annotations

import pytest

from heimdall_guardian import i18n
from heimdall_guardian.i18n import languages
from heimdall_guardian.ui import model as m


@pytest.fixture(autouse=True)
def _spanish(monkeypatch):
    monkeypatch.setattr(languages, "_current", "es")
    monkeypatch.setattr(languages, "_override", None)


def summary(critica=0, alta=0, media=0, baja=0, info=0, **states) -> dict:
    return {
        "by_severity": {
            "critical": critica,
            "high": alta,
            "medium": media,
            "low": baja,
            "info": info,
        },
        "by_status": states,
    }


@pytest.mark.parametrize(
    ("counts", "headline", "why"),
    [
        ({"critica": 3, "alta": 8}, "Todavía no está listo", "3 críticos y 8 altos"),
        ({"critica": 1}, "Todavía no está listo", "Hay 1 crítico."),
        ({"alta": 1, "media": 4}, "no hoy", "quedan 1 alto"),
        ({"media": 2, "baja": 1}, "Sin problemas graves", "3 de menor severidad"),
        ({}, "No se encontró nada", "no sustituye"),
    ],
)
def test_verdict_answers_in_plain_words(counts: dict, headline: str, why: str):
    got_headline, got_why = m.verdict(summary(**counts))
    assert headline in got_headline
    assert why in got_why


def test_comparison_with_previous_run():
    assert m.comparison(summary(), None) == "Primera corrida de este proyecto."
    text = m.comparison(summary(new=2, fixed=5, persistent=7, accepted=1), 3)
    assert text == (
        "Desde la corrida 3: 2 nuevos, 5 corregidos, 7 siguen igual, 1 aceptados o descartados."
    )


def test_strata_skip_empty_levels_and_do_not_let_volume_crush_severity():
    bands = m.strata(summary(critica=2, media=40))
    assert [band.severity for band in bands] == ["critical", "medium"]
    critical, medium = bands
    assert critical.background == "#8B1A2B"  # crimson: severity uses the usual colors
    # 20 times more findings do not give a band 20 times taller.
    assert medium.flex / critical.flex < 5
    assert m.strata(summary()) == []


def test_visible_findings_filters_and_puts_open_ones_first():
    def finding(id_, severity, status, title="t", file="a.py"):
        return {
            "id": id_,
            "severity": severity,
            "baseline_status": status,
            "title": title,
            "file": file,
            "rule_id": "R",
            "line_start": 3,
        }

    findings = [
        finding("1", "medium", "new"),
        finding("2", "critical", "accepted"),
        finding("3", "critical", "persistent", title="Inyección SQL", file="app/views.py"),
        finding("4", "high", "new"),
    ]
    assert [f["id"] for f in m.visible_findings(findings, None)] == ["3", "4", "1", "2"]
    assert [f["id"] for f in m.visible_findings(findings, "critical")] == ["3", "2"]
    assert [f["id"] for f in m.visible_findings(findings, None, "VIEWS")] == ["3"]
    assert m.location(findings[2]) == "app/views.py:3"
    assert m.location({**findings[0], "line_start": 0}) == "a.py"


def test_palette_comes_from_the_logo_and_severity_stays_conventional():
    assert (m.NIGHT, m.GOLD, m.BRONZE) == ("#02040A", "#F2B23A", "#8A5412")
    assert set(m.STRATUM_COLORS) == set(m.SEVERITIES)
    assert m.SEVERITY_COLORS["critical"][0] == "#8B1A2B"


def test_each_depth_option_says_what_it_reviews():
    assert m.profile_steps("quick") == ["Secretos", "Dependencias", "Configuración"]
    assert "Revisión con IA" in m.profile_steps("full")
    assert "Revisión con IA" not in m.profile_steps("standard")
    assert m.profile_steps("vendor")[-1] == "Dictamen"
    assert m.profile_steps("custom", {"SEC", "AI"}) == ["Secretos", "Revisión con IA"]


def test_run_facts_say_whether_ai_took_part():
    def payload(*tools, summary=None):
        return {"tools": list(tools), "ai_summary": summary}

    def tool(name, status="ran", version=None, detail=""):
        return {"name": name, "status": status, "version": version, "detail": detail}

    without = m.run_facts(payload(tool("gitleaks"), tool("osv", "skipped")))
    assert without == [
        "Se ejecutó: Secretos.",
        "No se pudo ejecutar: Dependencias (segunda fuente).",
        "Sin revisión con IA: este perfil no la incluye.",
    ]
    used = m.run_facts(
        payload(tool("llm", version="qwen", detail="28 de 28 válidas."), summary={"text": "x"})
    )
    assert used[-1] == "Revisión con IA: modelo qwen. 28 de 28 válidas. Redactó el resumen."
    down = m.run_facts(payload(tool("llm", "error", detail="sin conexión")))
    assert down[-1] == "La revisión con IA no se ejecutó: sin conexión."


def test_verdict_tone_reads_like_a_traffic_light():
    red, green = m.SEVERITY_COLORS["critical"][0], m.GOOD[0]
    assert m.verdict_tone(summary(critica=1)) == red
    assert m.verdict_tone(summary(alta=2)) not in (red, green)
    assert m.verdict_tone(summary(media=3)) == green
    assert m.verdict_tone(summary(), {"outcome": "not_approved"}) == red
    assert m.verdict_tone(summary(critica=9), {"outcome": "approved"}) == green


def test_small_strata_keep_room_for_their_number():
    flexes = [band.flex for band in m.strata(summary(critica=1, alta=400, media=30, baja=2))]
    assert min(flexes) >= 4
    assert max(flexes) <= 8


def test_accepted_findings_can_be_hidden_and_counted():
    findings = [
        {
            "id": "1",
            "severity": "high",
            "baseline_status": "new",
            "title": "t",
            "file": "a",
            "rule_id": "R",
            "line_start": 1,
        },
        {
            "id": "2",
            "severity": "high",
            "baseline_status": "accepted",
            "title": "t",
            "file": "a",
            "rule_id": "R",
            "line_start": 1,
        },
    ]
    assert [f["id"] for f in m.visible_findings(findings, None, include_suppressed=False)] == ["1"]
    assert len(m.visible_findings(findings, None)) == 2
    assert m.suppressed_count(findings) == 1


def test_watch_line_summarizes_what_is_already_guarded():
    assert m.watch_line([]) == ""
    projects = [summary(critica=2), summary(alta=1)]
    assert m.watch_line(projects) == "Vigilas 2 proyectos; 1 con problemas críticos abiertos."
    assert "ninguno" in m.watch_line([summary()])


def test_ai_opinion_reads_both_triage_and_endpoint_reviews():
    triage = {
        "task": "T1",
        "verdict": "likely_real",
        "confidence": "medium",
        "explanation": "Concatena la entrada.",
        "suggested_fix": "Usar parámetros.",
    }
    assert m.ai_opinion(triage) == [
        "Probable real (confianza media).",
        "Concatena la entrada.",
        "Corrección sugerida: Usar parámetros.",
    ]
    endpoint = {
        "task": "T2",
        "idor_risk": "high",
        "flow_risk": "none",
        "explanation": "Busca el registro solo por su id.",
    }
    assert m.ai_opinion(endpoint) == [
        "Riesgo de acceso a registros ajenos: alto; riesgo de saltar o repetir pasos: ninguno.",
        "Busca el registro solo por su id.",
    ]


def _two_destinations():
    from heimdall_guardian.core.config import LlmConfig, LlmDestination

    return LlmConfig(
        active_destination="oficina",
        destinations=(
            LlmDestination(
                name="oficina",
                url="http://localhost:11434/v1",
                requires_token=True,
                model_triage="qwen2.5-coder:14b",
                model_summary="qwen3:14b",
            ),
            LlmDestination(name="otro", url="http://localhost:11434/v1", model_triage="w"),
        ),
    )


def test_several_ai_configurations_can_share_a_server_with_other_models():
    llm = _two_destinations()
    forms = [m.destination_form(d) for d in llm.destinations]
    assert forms[0]["triage"] == "qwen2.5-coder:14b"
    assert forms[0]["endpoints"] == ""
    forms[0]["name"] = "gpu"  # renaming does not lose the choice or the token
    forms.append(
        {"original": "", "name": "nuevo", "url": forms[0]["url"]} | dict.fromkeys(m.AI_TASK_IDS, "")
    )
    forms[2]["triage"] = "z"

    updated = m.llm_from_forms(llm, forms, 2, 0, enabled=True)
    assert [d.name for d in updated.destinations] == ["gpu", "otro", "nuevo"]
    assert (updated.active_destination, updated.fallback_destination) == ("nuevo", "gpu")
    assert updated.destination("gpu").requires_token is True
    assert updated.destination("gpu").model("endpoints") is None
    assert updated.destination("nuevo").model("triage") == "z"
    assert m.destination_label(updated.destinations[0]) == "gpu · qwen2.5-coder:14b, qwen3:14b"

    # The fallback cannot be the same as the active one.
    assert m.llm_from_forms(llm, forms, 0, 0, enabled=True).fallback_destination == "none"


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ({"name": " "}, "Ponle nombre"),
        ({"name": "otro"}, "dos configuraciones llamadas «otro»"),
        ({"url": "http://8.8.8.8:11434/v1"}, "oficina:"),
        ({"triage": "modelo:cloud"}, "oficina:"),
    ],
)
def test_invalid_ai_configurations_are_rejected(change, message):
    llm = _two_destinations()
    forms = [m.destination_form(d) for d in llm.destinations]
    forms[0].update(change)
    with pytest.raises(ValueError, match=message):
        m.llm_from_forms(llm, forms, 0, None, enabled=True)
    with pytest.raises(ValueError, match="al menos una"):
        m.llm_from_forms(llm, [], 0, None, enabled=True)


def test_a_scan_can_use_another_ai_configuration():
    llm = _two_destinations()
    assert llm.using("otro").active_destination == "otro"
    assert llm.active_destination == "oficina"  # what is stored does not change
    with pytest.raises(LookupError, match="Hay: oficina, otro"):
        llm.using("nadie")


def _finding(**over) -> dict:
    base = {
        "rule_id": "DJ-SQL-001",
        "detected_by": ["opengrep"],
        "cwe": "CWE-89",
        "owasp": "A05:2025 Injection",
        "confidence": "high",
        "file": "app/views.py",
        "line_start": 12,
        "baseline_status": "new",
    }
    return {**base, **over}


def test_expert_facts_lists_technical_data_and_the_verification_guide():
    facts = dict(m.expert_facts(_finding()))
    assert facts["Regla"] == "DJ-SQL-001"
    assert facts["Herramienta"] == "opengrep"
    assert facts["OWASP"] == "A05:2025 Injection (Inyección)"
    assert facts["Confianza"] == "alta"
    assert facts["Ubicación"] == "app/views.py:12"
    assert "parámetros enlazados" in facts["Cómo verificarlo"]


def test_expert_facts_skips_missing_data_and_translates_old_labels():
    facts = dict(m.expert_facts(_finding(cwe=None, owasp="A03:2021 Injection", line_start=None)))
    assert "CWE" not in facts
    assert "Cómo verificarlo" not in facts
    assert facts["OWASP"].startswith("A05:2025")
    assert facts["Ubicación"] == "app/views.py"


def test_owasp_overview_without_result_has_no_counts():
    view = m.owasp_overview(None)
    assert len(view["rows"]) == 10
    assert all(row["count"] is None for row in view["rows"])
    assert "2025" in view["edition"]
    assert view["rows"][0]["title"] == "A01:2025 Control de acceso roto"


def test_owasp_overview_counts_only_open_findings():
    payload = {
        "findings": [
            _finding(),
            _finding(owasp="A03:2021 Injection"),
            _finding(baseline_status="accepted"),
        ]
    }
    rows = {row["title"].split()[0]: row for row in m.owasp_overview(payload)["rows"]}
    assert rows["A05:2025"]["count"] == 2
    assert rows["A01:2025"]["count"] == 0
    assert rows["A09:2025"]["coverage"] == "No"
    assert rows["A01:2025"]["background"] != rows["A09:2025"]["background"]


# ------------------------------------------------------------------ language


def test_nothing_visible_is_frozen_at_import():
    spanish = (
        m.profiles(),
        m.module_names(),
        m.tool_name("gitleaks"),
        m.ai_tasks(),
        m.ai_time_warning(),
        m.tagline(),
        m.motto(),
        m.profile_steps("quick"),
        m.verdict(summary(critica=3, alta=8)),
        m.comparison(summary(new=1), 2),
        m.watch_line([summary(critica=1)]),
    )
    i18n.set_language("en")
    english = (
        m.profiles(),
        m.module_names(),
        m.tool_name("gitleaks"),
        m.ai_tasks(),
        m.ai_time_warning(),
        m.tagline(),
        m.motto(),
        m.profile_steps("quick"),
        m.verdict(summary(critica=3, alta=8)),
        m.comparison(summary(new=1), 2),
        m.watch_line([summary(critica=1)]),
    )
    for before, after in zip(spanish, english, strict=True):
        assert before != after
    assert m.profile_steps("quick") == ["Secrets", "Dependencies", "Configuration"]
    assert m.profile_steps("vendor")[-1] == "Verdict"
    assert m.verdict(summary(critica=3, alta=8)) == (
        "It is not ready to be released yet.",
        "Open: 3 critical and 8 high.",
    )
    assert m.watch_line([summary(critica=1)]) == (
        "You watch 1 project; 1 with open critical problems."
    )
    assert m.comparison(summary(new=1), 2).startswith("Since run 2: 1 new")
    i18n.set_language("es")
    assert m.profile_steps("quick") == ["Secretos", "Dependencias", "Configuración"]


def test_profiles_and_ai_tasks_cover_every_key_in_both_languages():
    for lang in ("es", "en"):
        i18n.set_language(lang)
        profiles = m.profiles()
        assert [key for key, _, _ in profiles] == [
            "quick",
            "standard",
            "full",
            "vendor",
            "custom",
        ]
        assert all(name and desc and name != desc for _, name, desc in profiles)
        assert [task for task, _ in m.ai_tasks()] == list(m.AI_TASK_IDS)
        assert m.profile_name("standard") == profiles[1][1]
        assert m.profile_name("otro") == "otro"


def test_run_facts_and_ai_opinion_in_english():
    i18n.set_language("en")
    facts = m.run_facts(
        {
            "tools": [
                {"name": "gitleaks", "status": "ran", "version": None, "detail": ""},
                {"name": "osv", "status": "skipped", "version": None, "detail": ""},
            ],
            "ai_summary": None,
        }
    )
    assert facts == [
        "Ran: Secrets.",
        "Could not run: Dependencies (second source).",
        "No AI review: this profile does not include it.",
    ]
    opinion = m.ai_opinion(
        {
            "verdict": "likely_real",
            "confidence": "medium",
            "idor_risk": "high",
            "explanation": "x",
        }
    )
    assert opinion == [
        "Probably real (confidence medium).",
        "Risk of access to other people's records: high.",
        "x",
    ]


def test_severity_counts_pluralize():
    assert m.count_label(1, "critical") == "1 crítico"
    assert m.count_label(3, "info") == "3 informativos"
    i18n.set_language("en")
    assert m.count_label(3, "critical") == "3 critical"
    assert (
        m.watch_line([summary()] * 2) == "You watch 2 projects; none with open critical problems."
    )


def test_nav_context() -> None:
    assert m.nav_context("project", "Configuración") == "Configuración"
    assert m.nav_context("project", None) == "project"
    assert m.nav_context(None, None) == "Heimdall Guardian"


def test_tour_steps_and_language():
    es = [m.tour_step(i) for i in range(3)]
    assert es[0]["indicator"] == "Paso 1 de 3"
    assert es[2]["title"] == "Cómo leer el resultado"
    i18n.set_language("en")
    assert m.tour_step(0)["indicator"] == "Step 1 of 3"
    assert m.tour_step(99)["title"] == "How to read the result"
    assert all(m.tour_step(i)["body"] for i in range(3))


def test_tour_seen_is_persisted(tmp_path, monkeypatch):
    from heimdall_guardian.core.config import Config, load_config

    path = tmp_path / "config.toml"
    monkeypatch.setenv("HDL_CONFIG", str(path))
    config = Config()
    assert m.tour_pending(config)
    updated = m.mark_tour_seen(config)
    assert not m.tour_pending(updated)
    assert not m.tour_pending(load_config(path))
    assert m.tour_pending(load_config(tmp_path / "other.toml"))


def _project(name: str, started: str = "2026-01-02T10:00:00", **counts) -> dict:
    return {"path": f"/p/{name}", "name": name, "started": started, **summary(**counts)}


def test_recent_projects_limit_and_order():
    projects = [_project(f"p{i}") for i in range(8)]
    result = m.recent_projects(projects, None)
    assert [r["name"] for r in result] == ["p0", "p1", "p2", "p3", "p4"]
    assert len(m.recent_projects(projects, None, limit=2)) == 2


def test_recent_projects_active_date_and_tone():
    projects = [_project("a", critica=1), _project("b")]
    result = m.recent_projects(projects, "/p/b")
    assert [r["active"] for r in result] == [False, True]
    assert result[0]["date"] == "2026-01-02"
    assert result[0]["tone"] == m.verdict_tone(projects[0])
    assert result[0]["path"] == "/p/a"


def test_suggestion_defaults_leave_tool_folders_unchecked_for_vendor():
    from heimdall_guardian.core.presets import Suggestion

    found = [
        Suggestion(".next", "web/.next", "stack", "node"),
        Suggestion(".claude", ".claude", "tool"),
    ]
    assert m.suggestion_defaults(found, "standard") == {".next": True, ".claude": True}
    assert m.suggestion_defaults(found, "vendor") == {".next": True, ".claude": False}


def test_suggestion_defaults_leave_gitignore_folders_unchecked_for_vendor():
    from heimdall_guardian.core.presets import Suggestion

    found = [
        Suggestion(".next", "web/.next", "stack", "node"),
        Suggestion("tmp", "tmp", "gitignore"),
    ]
    assert m.suggestion_defaults(found, "standard") == {".next": True, "tmp": True}
    assert m.suggestion_defaults(found, "vendor") == {".next": True, "tmp": False}


def test_saving_folders_keeps_saved_patterns_the_dialog_does_not_show():
    saved = [".next", "legacy", "*.spec.ts"]
    # `.next` only lives in apps/web/.next (not shown); nothing unticked touches it.
    assert m.kept_folder_entries(saved, unchecked=["src"]) == [".next", "legacy"]
    # Unticking a folder that a saved entry skips drops that entry.
    assert m.kept_folder_entries(saved, unchecked=["legacy"]) == [".next"]


def test_subproject_rows():
    from heimdall_guardian.core.subprojects import SubProject

    rows = m.subproject_rows([SubProject("api", ("node", "typescript")), SubProject("misc", ())])
    assert rows == [
        {"path": "api", "name": "api", "stacks": "node, typescript"},
        {"path": "misc", "name": "misc", "stacks": "—"},
    ]


def test_tool_name_opengrep_lists_the_reviewed_stacks():
    stacks = ["php", "laravel", "node"]
    assert m.tool_name("opengrep", stacks) == "Código PHP, Laravel y Node.js (reglas propias)"
    i18n.set_language("en")
    assert m.tool_name("opengrep", stacks) == "PHP, Laravel and Node.js code (built-in rules)"
    assert m.tool_name("opengrep") == "Built-in code rules"
    assert m.tool_name("opengrep", ["go", "git"]) == "Built-in code rules"


def test_tool_name_summary_and_result_resolve():
    assert m.tool_name("summary") == "Resumen ejecutivo con IA"
    assert m.tool_name("result") == "Guardando el resultado"


def _rules(tmp_path, problems=0):
    from heimdall_guardian.core.user_rules import RuleProblem, UserRules
    from heimdall_guardian.i18n import msg

    files = (tmp_path / "a.yaml", tmp_path / "b.yaml")
    found = tuple(
        RuleProblem(f"bad{i}.yaml", msg("core.user_rules.no_rules")) for i in range(problems)
    )
    return UserRules(files=files, problems=found, ids=("ACME-SQL-001", "ACME-SQL-002"))


def test_user_rules_summary_without_folders():
    from heimdall_guardian.core.user_rules import UserRules

    assert m.user_rules_summary(UserRules((), (), ()), None) == ["No hay carpetas de reglas."]
    i18n.set_language("en")
    assert m.user_rules_summary(UserRules((), (), ()), None) == ["No rule folders."]


def test_user_rules_summary_ready(tmp_path):
    assert m.user_rules_summary(_rules(tmp_path), None) == ["2 reglas listas en 2 archivos"]
    i18n.set_language("en")
    assert m.user_rules_summary(_rules(tmp_path), None) == ["2 rules ready in 2 files"]


def test_user_rules_summary_lists_problems_and_engine_failures(tmp_path):
    user = _rules(tmp_path, problems=1)
    lines = m.user_rules_summary(user, {tmp_path / "b.yaml": "bad syntax"})
    assert lines[0].startswith("0 reglas") or lines[0].startswith("2 reglas")
    assert lines[1].startswith("bad0.yaml: ")
    assert lines[2] == f"{tmp_path / 'b.yaml'}: bad syntax"
    i18n.set_language("en")
    assert m.user_rules_summary(user, None)[1].startswith("bad0.yaml: ")


def test_user_rules_summary_caps_lines(tmp_path):
    lines = m.user_rules_summary(_rules(tmp_path, problems=11), None)
    assert len(lines) == 1 + 8 + 1
    assert lines[-1] == "y 3 más"
    i18n.set_language("en")
    assert m.user_rules_summary(_rules(tmp_path, problems=11), None)[-1] == "and 3 more"


def test_ai_opinion_for_a_risk_point_says_reachability_and_input():
    sink = {
        "task": "T4",
        "reachable": "yes",
        "source": "parámetro id",
        "risk": "high",
        "explanation": "Llega sin validar.",
        "suggested_fix": "Usar parámetros.",
    }
    assert m.ai_opinion(sink) == [
        "Alcanzable desde la entrada del usuario: sí",
        "Entrada: parámetro id",
        "Riesgo de un ataque a través de esta operación: alto.",
        "Llega sin validar.",
        "Corrección sugerida: Usar parámetros.",
    ]
    from heimdall_guardian import i18n

    i18n.set_language("en")
    try:
        assert m.ai_opinion({"reachable": "unclear"}) == ["Reachable from user input: unclear"]
    finally:
        i18n.set_language("es")


def test_run_facts_report_what_the_sink_review_added():
    def payload(findings, stats):
        llm = {"name": "llm", "status": "ran", "version": "q", "detail": "", "stats": stats}
        return {"tools": [llm], "ai_summary": None, "findings": findings}

    t4 = {"origin": "ai", "llm_assessment": {"task": "T4"}}
    t2 = {"origin": "ai", "llm_assessment": {"task": "T2"}}
    found = m.run_facts(payload([t4, t2], {"sinks_reviewed": 3, "sinks_found": 1}))
    assert "La IA encontró 1 posible problema" in found[-1]
    found = m.run_facts(payload([t4, t4], None))
    assert "2 posibles problemas" in found[-1]
    clear = m.run_facts(payload([t2], {"sinks_reviewed": 4, "sinks_found": 0}))
    assert clear[-1] == "La IA revisó 4 puntos de riesgo y no encontró nada que añadir."
    assert "La IA" not in " ".join(m.run_facts(payload([], None))[1:])
