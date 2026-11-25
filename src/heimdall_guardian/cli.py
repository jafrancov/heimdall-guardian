"""CLI `hdl`: the same core as the desktop interface."""

from __future__ import annotations

import argparse
import getpass
import importlib.util
import json
import sys
import tarfile
import tempfile
from collections.abc import Sequence
from dataclasses import asdict
from datetime import date
from pathlib import Path
from typing import Any

from . import __version__, tool_install
from .adapters import default_adapters, updates
from .adapters.base import AdapterError, find_binary
from .adapters.opengrep import validate_rule_files
from .core.config import TEMPLATE, ConfigError, load_config
from .core.environment import maybe_app_hint
from .core.finding import BaselineStatus
from .core.locking import DatabaseLockTimeout, tools_lock
from .core.paths import bases_dir, config_path, data_dir, data_location_lines
from .core.presets import ignored_entries, reason, suggest
from .core.profiles import (
    CUSTOM_PROFILE,
    PROFILE_ALIASES,
    PROFILES,
    Module,
    canonical_profile,
    parse_modules,
    profile_name,
)
from .core.runner import Plan, ScanResult, build_plan, issue_verdict, run_scan
from .core.subprojects import find_subprojects
from .core.user_rules import check_user_rules, own_rule_ids, rule_ids_of
from .core.verdict import Thresholds
from .i18n import (
    SUPPORTED,
    Message,
    apply_language,
    get_language,
    is_message,
    label,
    normalize,
    render,
    set_override,
    t,
)
from .llm.client import KEYRING_SERVICE, LlmClient, LlmError
from .llm.destinations import DestinationError
from .llm.module import AiRunner
from .report import SBOM_SUFFIX, WRITERS, write_report
from .report import text as report_text
from .report.text import tool_status
from .storage import Store, forget_project, load_project_exclusions
from .storage.bases import export_bases, import_bases, update_bases
from .storage.store import project_identity
from .storage.thresholds import PinError, ThresholdStore

EXIT_OK = 0
EXIT_FAILURE = 1
EXIT_USAGE = 2

_FORMATS = ", ".join([*WRITERS, SBOM_SUFFIX])

# Subcommand and option names: English is the main one and Spanish keeps working as an
# alias. In the help and in messages the one of the current language comes first.
# Stored values (profiles, statuses) do not change: here only more spellings are accepted.
_COMMAND_ALIASES = {"herramientas": "tools", "bases": "databases", "reglas": "rules"}
_SUPPRESSION_STATUS = {
    "accepted": BaselineStatus.ACCEPTED,
    "aceptado": BaselineStatus.ACCEPTED,
    "false_positive": BaselineStatus.FALSE_POSITIVE,
    "false-positive": BaselineStatus.FALSE_POSITIVE,
    "falso-positivo": BaselineStatus.FALSE_POSITIVE,
    "falso_positivo": BaselineStatus.FALSE_POSITIVE,
}
_STATUS_SHOWN = {"en": ("accepted", "false_positive"), "es": ("aceptado", "falso-positivo")}
_THRESHOLD_OPTIONS = {
    "max_critical": ("--max-critical", "--max-criticos"),
    "max_secrets": ("--max-secrets", "--max-secretos"),
    "max_unauth_write_endpoints": (
        "--max-unauth-write-endpoints",
        "--max-endpoints-escritura-sin-auth",
    ),
    "max_high": ("--max-high", "--max-altos"),
    "max_patchable_critical_deps": (
        "--max-patchable-critical-deps",
        "--max-dependencias-criticas-con-parche",
    ),
    "count_ai_findings": ("--count-ai-findings", "--contar-hallazgos-ia"),
}
_YES = {"yes", "y", "si", "true"}
_NO = {"no", "n", "false"}


def _opt(english: str, spanish: str) -> tuple[str, str]:
    """The two spellings of an option or subcommand, the current language's first."""
    return (english, spanish) if get_language() == "en" else (spanish, english)


def _name(english: str, spanish: str) -> str:
    """How an option is named in a message: in the current language."""
    return _opt(english, spanish)[0]


def _threshold_options(field: str) -> tuple[str, ...]:
    default = f"--{field.replace('_', '-')}"
    return _opt(*_THRESHOLD_OPTIONS[field]) if field in _THRESHOLD_OPTIONS else (default,)


def _profile_choices() -> list[str]:
    english = [*PROFILES, CUSTOM_PROFILE]
    return english if get_language() == "en" else list(PROFILE_ALIASES)


def _profile(value: str) -> str:
    """A profile written in English or Spanish → the stored code."""
    code = canonical_profile(value)
    if code not in PROFILES and code != CUSTOM_PROFILE:
        raise argparse.ArgumentTypeError(
            t("cli.error.bad_profile", value=value, valid=", ".join(_profile_choices()))
        )
    return code


def _status(value: str) -> BaselineStatus:
    try:
        return _SUPPRESSION_STATUS[value.lower()]
    except KeyError:
        valid = ", ".join(_STATUS_SHOWN[get_language()])
        raise argparse.ArgumentTypeError(
            t("cli.error.bad_status", value=value, valid=valid)
        ) from None


def _yes_no(value: str) -> bool:
    word = value.strip().lower()
    if word in _YES:
        return True
    if word in _NO:
        return False
    raise argparse.ArgumentTypeError(t("cli.error.bad_yes_no", value=value))


def _new_parser(**kwargs: Any) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(add_help=False, **kwargs)
    parser.add_argument("-h", "--help", action="help", help=t("cli.help.help"))
    return parser


def _add(parser: argparse.ArgumentParser, english: str, spanish: str, **kwargs: Any) -> None:
    names = _opt(english, spanish)
    if kwargs.get("action") in (None, "append") and "metavar" not in kwargs:
        kwargs["metavar"] = names[0].lstrip("-").upper()  # in the option's language
    parser.add_argument(*names, **kwargs)


def _folder(sub: argparse.ArgumentParser) -> None:
    sub.add_argument("folder", type=Path, metavar=t("cli.metavar.folder"), help=t("cli.arg.folder"))


def _outputs_option(sub: argparse.ArgumentParser) -> None:
    _add(
        sub,
        "--output",
        "--salida",
        dest="output",
        type=Path,
        action="append",
        default=[],
        help=t("cli.arg.output", formats=_FORMATS),
    )


def _scan_parser(commands: Any) -> None:
    scan = commands.add_parser("scan", help=t("cli.scan.help"), add_help=False)
    scan.add_argument("-h", "--help", action="help", help=t("cli.help.help"))
    _folder(scan)
    _add(scan, "--profile", "--perfil", dest="profile", type=_profile, help=t("cli.scan.profile"))
    _add(
        scan,
        "--modules",
        "--modulos",
        dest="modules",
        help=t("cli.scan.modules", modules=", ".join(m.value for m in Module)),
    )
    _outputs_option(scan)
    scan.add_argument("--dry-run", action="store_true", help=t("cli.scan.dry_run"))
    _add(
        scan,
        "--update-databases",
        "--actualizar-bases",
        dest="update_databases",
        action="store_true",
        help=t("cli.scan.update_databases"),
    )
    folder_name = t("cli.metavar.folder_upper")
    _add(
        scan,
        "--exclude",
        "--excluir",
        dest="exclude",
        action="append",
        default=[],
        metavar=folder_name,
        help=t("cli.scan.exclude"),
    )
    _add(
        scan,
        "--exclude-gitignored",
        "--excluir-ignorados",
        dest="exclude_gitignored",
        action="store_true",
        help=t("cli.scan.exclude_gitignored"),
    )
    _add(
        scan,
        "--include",
        "--incluir",
        dest="include",
        action="append",
        default=[],
        metavar=folder_name,
        help=t("cli.scan.include"),
    )
    _add(scan, "--ai", "--ia", dest="ai", metavar=t("cli.metavar.name"), help=t("cli.scan.ai"))
    _add(scan, "--issuer", "--emite", dest="issuer", help=t("cli.scan.issuer"))
    _add(
        scan,
        "--no-baseline",
        "--sin-linea-base",
        dest="no_baseline",
        action="store_true",
        help=t("cli.scan.no_baseline"),
    )


def _project_parsers(commands: Any) -> None:
    def add(name: str, help_key: str) -> argparse.ArgumentParser:
        sub: argparse.ArgumentParser = commands.add_parser(name, help=t(help_key), add_help=False)
        sub.add_argument("-h", "--help", action="help", help=t("cli.help.help"))
        _folder(sub)
        return sub

    report = add("report", "cli.report.help")
    _add(report, "--run", "--corrida", dest="run", type=int, help=t("cli.report.run"))
    _outputs_option(report)

    add("runs", "cli.runs.help")

    forget = add("forget", "cli.forget.help")
    _add(forget, "--yes", "--si", dest="yes", action="store_true", help=t("cli.forget.yes"))

    suppress = add("suppress", "cli.suppress.help")
    suppress.add_argument("id", help=t("cli.suppress.id"))
    _add(
        suppress,
        "--status",
        "--estado",
        dest="status",
        required=True,
        type=_status,
        help=t("cli.suppress.status"),
    )
    _add(
        suppress,
        "--reason",
        "--motivo",
        dest="reason",
        required=True,
        help=t("cli.suppress.reason"),
    )
    _add(
        suppress,
        "--review",
        "--revisar",
        dest="review",
        type=date.fromisoformat,
        metavar=t("cli.metavar.date"),
        help=t("cli.suppress.review"),
    )
    _add(suppress, "--author", "--autor", dest="author", help=t("cli.suppress.author"))

    unsuppress = add("unsuppress", "cli.unsuppress.help")
    unsuppress.add_argument("id", help=t("cli.unsuppress.id"))

    add("suppressions", "cli.suppressions.help")

    baseline = add("baseline", "cli.baseline.help")
    for english, spanish, key, dest in (
        ("--export", "--exportar", "export", "export"),
        ("--import", "--importar", "import", "import_"),
    ):
        _add(
            baseline,
            english,
            spanish,
            dest=dest,
            type=Path,
            metavar=t("cli.metavar.file_json"),
            help=t(f"cli.baseline.{key}"),
        )


def _global_parsers(commands: Any) -> None:
    def add(english: str, spanish: str | None, help_key: str) -> argparse.ArgumentParser:
        names = _opt(english, spanish) if spanish else (english,)
        sub: argparse.ArgumentParser = commands.add_parser(
            names[0], aliases=list(names[1:]), help=t(help_key), add_help=False
        )
        sub.add_argument("-h", "--help", action="help", help=t("cli.help.help"))
        return sub

    tools = add("tools", "herramientas", "cli.tools.help")
    _add(tools, "--news", "--novedades", dest="news", action="store_true", help=t("cli.tools.news"))
    _add(
        tools,
        "--install",
        "--instalar",
        dest="install",
        action="store_true",
        help=t("cli.tools.install"),
    )

    version = add("version", None, "cli.version.help")
    version.add_argument("--check", action="store_true", help=t("cli.version.check"))

    rules = add("rules", "reglas", "cli.rules.help")
    _add(
        rules,
        "--check",
        "--verificar",
        dest="check",
        action="store_true",
        help=t("cli.rules.check"),
    )
    _add(
        rules,
        "--dir",
        "--carpeta",
        dest="dirs",
        action="append",
        default=[],
        metavar=t("cli.metavar.folder"),
        help=t("cli.rules.dir"),
    )

    thresholds = add("thresholds", None, "cli.thresholds.help")
    _add(
        thresholds,
        "--set-pin",
        "--definir-pin",
        dest="set_pin",
        action="store_true",
        help=t("cli.thresholds.set_pin"),
    )
    _add(
        thresholds,
        "--log",
        "--bitacora",
        dest="log",
        action="store_true",
        help=t("cli.thresholds.log"),
    )
    for name, kind in Thresholds.__annotations__.items():
        if kind == "int":
            thresholds.add_argument(
                *_threshold_options(name),
                dest=name,
                type=int,
                metavar="N",
                help=t("ui.thresholds.maximum", label=t(f"ui.thresholds.{name}")),
            )
    thresholds.add_argument(
        *_threshold_options("count_ai_findings"),
        dest="count_ai",
        type=_yes_no,
        metavar="yes|no" if get_language() == "en" else "si|no",
        help=t("cli.thresholds.count_ai"),
    )

    databases = add("databases", "bases", "cli.databases.help")
    _add(
        databases,
        "--update",
        "--actualizar",
        dest="update",
        action="store_true",
        help=t("cli.databases.update"),
    )
    for english, spanish, key, dest in (
        ("--export", "--exportar", "export", "export"),
        ("--import", "--importar", "import", "import_"),
    ):
        _add(
            databases,
            english,
            spanish,
            dest=dest,
            type=Path,
            metavar=t("cli.metavar.file_targz"),
            help=t(f"cli.databases.{key}"),
        )

    llm = add("llm", None, "cli.llm.help")
    _add(llm, "--destination", "--destino", dest="destination", help=t("cli.llm.destination"))
    _add(
        llm,
        "--save-token",
        "--guardar-token",
        dest="save_token",
        action="store_true",
        help=t("cli.llm.save_token"),
    )

    ui = add("ui", None, "cli.ui.help")
    ui.add_argument("--web", action="store_true", help=t("cli.ui.web"))
    ui.add_argument("--port", type=int, default=0, help=t("cli.ui.port"))

    config = add("config", None, "cli.config.help")
    config.add_argument("--init", action="store_true", help=t("cli.config.init"))


def _parser() -> argparse.ArgumentParser:
    """The argument parser in the active language (built once the language is already set)."""
    parser = _new_parser(prog="hdl", description=t("cli.description"))
    parser.add_argument(
        "--version", action="version", version=f"hdl {__version__}", help=t("cli.help.version")
    )
    parser.add_argument("--lang", "--idioma", choices=SUPPORTED, help=t("cli.lang.help"))
    commands = parser.add_subparsers(dest="command", required=True)
    _scan_parser(commands)
    _project_parsers(commands)
    _global_parsers(commands)
    return parser


def _early_language(argv: Sequence[str] | None) -> None:
    """Sets the language before building the parser, so the help comes out in it.

    A first minimal pass looks only for `--lang`/`--idioma`; an unsupported value is
    left to the full parser, which rejects it with its usage message.
    """
    pre = argparse.ArgumentParser(prog="hdl", add_help=False, allow_abbrev=False)
    pre.add_argument("--lang", "--idioma")
    requested = pre.parse_known_args(argv)[0].lang
    requested = requested if normalize(requested) else None
    set_override(requested)
    apply_language(requested)


def _info(message: str) -> None:
    print(message, file=sys.stderr)


def _root(args: argparse.Namespace) -> Path:
    root: Path = args.folder.resolve()
    if not root.is_dir():
        raise ValueError(t("cli.error.not_folder", path=root))
    return root


def _outputs(args: argparse.Namespace, root: Path) -> list[Path]:
    outputs = [path.resolve() for path in args.output]
    for path in outputs:
        if path.is_relative_to(root):
            # P1: nothing is ever written inside the analyzed folder.
            raise ValueError(t("cli.error.output_inside", option=_name("--output", "--salida")))
        if path.suffix.lower() not in WRITERS and not path.name.lower().endswith(SBOM_SUFFIX):
            raise ValueError(t("cli.error.format", name=path.name, formats=_FORMATS))
    return outputs


def _emit(payload: dict[str, Any], outputs: list[Path]) -> None:
    if not outputs:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    for path in outputs:
        write_report(payload, path)
        _info(t("cli.report.written", path=path))


def _print_plan(plan: Plan, ignored: tuple[list[str], str] = ([], "")) -> None:
    stacks = ", ".join(hit.stack for hit in plan.stacks) or t("cli.plan.stack_none")
    modules = ", ".join(sorted(plan.modules)) or t("cli.plan.no_modules")
    _info(t("cli.plan.folder", path=plan.root))
    _info(t("cli.plan.stack", stacks=stacks))
    _info(t("cli.plan.profile", profile=profile_name(plan.profile), modules=modules))
    if plan.pending_modules:
        _info(t("cli.plan.pending", modules=", ".join(plan.pending_modules)))
    _info(t("cli.plan.files", count=len(plan.tree.analyzable)))
    if ignored[1]:
        _info(
            t(
                "cli.plan.gitignored",
                count=len(ignored[0]),
                source=t(
                    "cli.plan.gitignored_source.git"
                    if ignored[1] == "git"
                    else "cli.plan.gitignored_source.gitignore"
                ),
            )
        )
    suggestions = suggest(plan.root, plan.stacks, plan.exclusions)
    for s in suggestions:
        _info(
            t(
                "cli.plan.suggested",
                pattern=s.pattern,
                reason=render(reason(s)),
                example=s.example,
            )
        )
    if suggestions:
        _info(t("cli.plan.suggested_hint"))
    subs = find_subprojects(plan.root, plan.tree.files)
    if subs:
        names = ", ".join(f"{s.path} ({', '.join(s.stacks) or '-'})" for s in subs)
        _info(t("cli.plan.subprojects", count=len(subs), names=names))
        _info(t("cli.plan.subprojects_hint", example=str(plan.root / subs[0].path)))


def _print_summary(result: ScanResult) -> None:
    for tool in result.tools:
        line = t(
            "cli.summary.tool_line",
            name=tool.name,
            status=tool_status(tool.status),
            count=tool.findings,
        )
        _info(f"  {line}  {render(tool.detail)}".rstrip())
    summary = result.summary()
    counts = summary["by_severity"]
    _info(
        t(
            "cli.summary.open",
            counts=" · ".join(
                f"{label(name, 'severity')} {count}" for name, count in counts.items()
            ),
        )
    )
    if result.run_id is not None:
        states = summary["by_status"]
        _info(
            t(
                "cli.summary.run",
                run=result.run_id,
                counts=" · ".join(
                    f"{label(name, 'status', variant='lower')} {count}"
                    for name, count in states.items()
                ),
            )
        )
    omitted_payload = {"omitted": result.to_dict()["omitted"]}
    if report_text.has_omitted(omitted_payload):
        _info(
            t(
                "cli.summary.omitted",
                text=" ".join(
                    part
                    for part in (
                        report_text.omitted_sentence(omitted_payload),
                        report_text.omitted_findings_sentence(omitted_payload),
                    )
                    if part
                ),
            )
        )
    for limitation in result.limitations:
        _info(t("cli.summary.limitation", text=render(limitation)))
    if result.verdict:
        _info(t("cli.summary.verdict", outcome=label(result.verdict["outcome"], "outcome")))
        for criterion in result.verdict["criteria"]:
            mark = t("cli.summary.exceeded" if criterion["exceeded"] else "cli.summary.met")
            _info(
                t(
                    "cli.summary.criterion",
                    name=render(criterion["criterion"]),
                    found=criterion["found"],
                    limit=criterion["limit"],
                    mark=mark,
                )
            )


def _scan(args: argparse.Namespace) -> int:
    config = load_config()
    profile = canonical_profile(args.profile or config.general.default_profile)
    custom = parse_modules(args.modules) if args.modules else None
    if custom and profile != CUSTOM_PROFILE:
        raise ValueError(
            t(
                "cli.error.modules_need_custom",
                modules=_name("--modules", "--modulos"),
                profile=_name("--profile", "--perfil"),
            )
        )
    root = _root(args)
    # What the user chose for this project in the application also counts.
    saved_exclude, saved_include = load_project_exclusions(root)
    ignored: tuple[list[str], str] = ([], "")
    if args.exclude_gitignored:
        ignored = ignored_entries(root)
    plan = build_plan(
        root,
        profile=profile,
        custom_modules=custom,
        exclusions=config.exclusions.to_exclusions(
            (*saved_exclude, *args.exclude, *ignored[0]),
            (*saved_include, *args.include),
            root=root,
        ),
        extra_rule_dirs=config.rules.extra_dirs,
    )
    outputs = _outputs(args, plan.root)

    _print_plan(plan, ignored)
    if args.dry_run:
        print(json.dumps(plan.to_dict(), ensure_ascii=False, indent=2))
        return EXIT_OK

    if args.update_databases and plan.modules & {Module.DEP, Module.SBOM}:
        _info(t("bases.size_notice"))
    llm = config.llm.using(args.ai) if args.ai else config.llm
    ai = AiRunner(llm) if Module.AI in plan.modules else None
    options: dict[str, Any] = {
        "update_dbs": args.update_databases,
        "ai": ai,
        "db_alert_days": config.databases.alert_age_days,
        "on_progress": _progress,
    }
    # The verdict is only issued when receiving vendor code.
    threshold_store = ThresholdStore() if plan.profile == "vendor" else None
    thresholds = threshold_store.load() if threshold_store else None
    issuer = args.issuer or getpass.getuser()
    if args.no_baseline:
        result = run_scan(plan, **options)
        result.limitations += threshold_store.notices if threshold_store else []
        if thresholds is not None:
            issue_verdict(result, thresholds, issuer)
    else:
        # Opened before analyzing: if the data directory is unusable, it fails
        # immediately and not after a long run.
        with Store(plan.root) as store:
            result = run_scan(plan, **options)
            result.limitations += threshold_store.notices if threshold_store else []
            _progress("result", "start")
            store.record(result, thresholds=thresholds, issuer=issuer)
    _print_summary(result)
    _emit(result.to_dict(), outputs)
    return EXIT_OK


def _progress(tool: str, status: str | Message) -> None:
    """Progress on stderr; the AI's is rewritten on the same line if there is a terminal."""
    if tool == "databases":
        _info(render(status))  # waiting for another process that updates the databases
        return
    if is_message(status):
        if sys.stderr.isatty():
            line = t("cli.progress.ai", status=render(status))
            print(f"\r{line}", end="", file=sys.stderr, flush=True)
        return
    if tool == "llm" and status != "start" and sys.stderr.isatty():
        print(file=sys.stderr)
    if status == "start":
        print(f"  {tool}…", file=sys.stderr, flush=True)


def _report(args: argparse.Namespace) -> int:
    root = _root(args)
    outputs = _outputs(args, root)
    with Store(root) as store:
        payload = store.payload(args.run)
    _emit(payload, outputs)
    return EXIT_OK


def _forget(args: argparse.Namespace) -> int:
    project_id, _ = project_identity(args.folder.resolve())
    if not args.yes:
        raise ValueError(t("cli.forget.confirm", option=_name("--yes", "--si")))
    if not forget_project(project_id):
        raise LookupError(t("cli.forget.none"))
    print(t("cli.forget.done"))
    return EXIT_OK


def _runs(args: argparse.Namespace) -> int:
    with Store(_root(args)) as store:
        runs = store.runs()
    if not runs:
        print(t("cli.runs.none"))
    for run in runs:
        severities = " · ".join(
            f"{label(name, 'severity')} {count}" for name, count in run["by_severity"].items()
        )
        states = run["by_status"]
        counts = t("cli.runs.counts", new=states["new"], fixed=states["fixed"])
        print(
            f"{run['run']:>4}  {run['started'][:16].replace('T', ' ')}  "
            f"{profile_name(run['profile']):<13} {severities}  {counts}"
        )
    return EXIT_OK


def _suppress(args: argparse.Namespace) -> int:
    with Store(_root(args)) as store:
        store.suppress(
            args.id,
            args.status,
            args.reason,
            args.author or getpass.getuser(),
            args.review,
        )
    shown = label(args.status.value, "status", variant="lower")
    print(t("cli.suppress.done", id=args.id.upper(), status=shown))
    return EXIT_OK


def _unsuppress(args: argparse.Namespace) -> int:
    with Store(_root(args)) as store:
        removed = store.unsuppress(args.id)
    print(t("cli.unsuppress.done" if removed else "cli.unsuppress.none", id=args.id.upper()))
    return EXIT_OK


def _suppressions(args: argparse.Namespace) -> int:
    with Store(_root(args)) as store:
        items = store.suppressions()
    if not items:
        print(t("cli.suppressions.none"))
    for item in items:
        review = (
            t("cli.suppressions.review", date=item["review_date"]) if item["review_date"] else ""
        )
        status = label(item["status"], "status", variant="lower")
        print(f"{item['id']}  {status:<15} {item['rule']}  {item['file']}")
        print(f"    {item['justification']} ({item['author']}, {item['created'][:10]}{review})")
    return EXIT_OK


def _size(count: int) -> str:
    """Human-readable size for the install report."""
    return f"{count / 1_048_576:.1f} MB"


def _install_tools() -> int:
    """`hdl tools --install`: pinned binaries, verified by SHA-256, into the data directory."""
    manifest = tool_install.load_manifest()
    if manifest is None:
        print(t("cli.tools.install_no_manifest"), file=sys.stderr)
        return EXIT_FAILURE
    target = tool_install.current_platform()
    if not tool_install.pinned_tools(manifest, target):
        print(t("cli.tools.install_no_platform", platform=target), file=sys.stderr)
        return EXIT_FAILURE
    folder = tool_install.tools_folder(manifest, target)
    print(t("cli.tools.install_start", path=folder))

    def show(record: tool_install.InstallRecord) -> None:
        if record.downloaded:
            print(
                t(
                    "cli.tools.install_downloaded",
                    name=record.name,
                    version=record.version,
                    transferred=_size(record.transferred),
                    size=_size(record.size),
                )
            )
        else:
            print(
                t(
                    "cli.tools.install_present",
                    name=record.name,
                    version=record.version,
                    size=_size(record.size),
                )
            )

    try:
        with tools_lock(_info):
            records = tool_install.install_tools(manifest, target, show)
    except (tool_install.ToolInstallError, DatabaseLockTimeout, OSError) as exc:
        print(t("cli.tools.install_failed", error=exc, path=folder), file=sys.stderr)
        return EXIT_FAILURE
    downloaded = sum(1 for record in records if record.downloaded)
    print(t("cli.tools.install_done", count=downloaded, total=len(records), path=folder))
    return EXIT_OK


def _tools(args: argparse.Namespace) -> int:
    if args.install:
        return _install_tools()
    installed: dict[str, str | None] = {}
    for adapter in default_adapters():
        if adapter.is_available():
            installed[adapter.name] = adapter.version()
            db = adapter.db_updated_at()
            suffix = t("cli.tools.database", date=db[:10]) if db else ""
            version = adapter.version() or t("cli.tools.unknown_version")
            print(f"{adapter.name:<9} {version}{suffix}")
        else:
            installed[adapter.name] = None
            print(f"{adapter.name:<9} {t('cli.tools.not_installed')}")
    for line in data_location_lines():
        print(line)
    manifest = tool_install.load_manifest()
    pinned = (
        tool_install.pinned_tools(manifest, tool_install.current_platform()) if manifest else {}
    )
    missing = [name for name in pinned if find_binary(name) is None]
    if missing:
        print(t("cli.tools.missing", names=", ".join(missing)))
    if args.news:
        _news(installed)
    return EXIT_OK


def _rules(args: argparse.Namespace) -> int:
    """Checks the user's own rule files: structure first, then the engine's own validation."""
    dirs = list(args.dirs) or list(load_config().rules.extra_dirs)
    if not dirs:
        print(t("cli.rules.none"))
        return EXIT_OK
    checked = check_user_rules(dirs, analyzed_root=None, own_ids=own_rule_ids())
    failed: set[str] = set()
    for problem in checked.problems:
        failed.add(problem.file)
        print(f"{t('cli.rules.invalid')}  {problem.file}: {render(problem.message)}")
    engine: dict[Path, str] = {}
    if checked.files:
        try:
            with tempfile.TemporaryDirectory(prefix="heimdall-") as tmp:
                engine = validate_rule_files(checked.files, Path(tmp))
        except AdapterError as exc:
            _info(t("cli.rules.no_engine", error=render(exc.message)))
    for path in checked.files:
        if path in engine:
            failed.add(str(path))
            print(f"{t('cli.rules.invalid')}  {path}: {engine[path]}")
        else:
            print(f"{t('cli.rules.ok')}  {path}: {', '.join(rule_ids_of(path))}")
    return 1 if failed else EXIT_OK


def _installed_by_script() -> bool:
    """True when this process runs from the venv that `install_hdl.py` creates."""
    venv = (data_dir() / "cli" / "venv").resolve()
    return Path(sys.prefix).resolve() == venv


def _self_update_lines(result: updates.SelfUpdate) -> list[str]:
    lines = [t("cli.version.latest", latest=result.latest or "-", status=result.status)]
    if result.outdated:
        lines.append(t("cli.version.page", page=result.page))
        if _installed_by_script():
            wheel = f"heimdall_guardian-{result.latest}-py3-none-any.whl"
            lines.append(t("cli.version.update", wheel=wheel, latest=result.latest))
    return lines


def _version(args: argparse.Namespace) -> int:
    print(f"hdl {__version__}")
    if args.check:
        for line in _self_update_lines(updates.check_self()):
            print(line)
    return EXIT_OK


def _news(installed: dict[str, str | None]) -> None:
    print(t("cli.tools.news_header"))
    results = updates.check(installed)
    for item in results:
        print(f"{item.tool:<9} {item.installed or '-':<9} {item.status}")
    own = updates.check_self()
    print(f"{'heimdall':<9} {own.installed:<9} {own.status}")
    outdated = [item for item in results if item.outdated]
    if not outdated and not own.outdated:
        return
    print(t("cli.tools.news_notes"))
    if own.outdated:
        print(f"  heimdall: {own.page}")
    for item in outdated:
        print(f"  {item.tool}: {item.page}")
    if outdated:
        print(t("cli.tools.news_pinned"))


def _llm(args: argparse.Namespace) -> int:
    """ "Test connection": available models and a test query."""
    config = load_config().llm
    name = args.destination or config.active_destination
    destination = config.destination(name)
    if destination is None:
        raise LookupError(t("cli.llm.no_destination", name=repr(name)))
    if args.save_token:
        import keyring

        keyring.set_password(
            KEYRING_SERVICE, name, getpass.getpass(t("cli.llm.token_prompt", name=name))
        )
        print(t("cli.llm.token_saved", name=name))
        return EXIT_OK
    print(
        t("cli.llm.destination_line", name=name, runtime=destination.runtime, url=destination.url)
    )
    try:
        client = LlmClient(destination, config)
        models = client.models()
    except (DestinationError, LlmError) as exc:
        print(t("cli.llm.state_offline", error=exc))
        return EXIT_USAGE
    print(t("cli.llm.state_online", count=len(models)))
    for available in models:
        print(f"  - {available}")
    for task in ("triage", "endpoints", "summary"):
        model = destination.model(task)
        note = t("cli.llm.model_unset") if model is None else model
        if model is not None and model not in models:
            note += t("cli.llm.model_missing")
        print(t("cli.llm.model_line", task=task, note=note))
    test_model = destination.model("triage")
    if test_model is not None and test_model in models:
        try:
            reply = client.chat(test_model, t("cli.llm.test_system"), t("cli.llm.test_user"))
        except (DestinationError, LlmError) as exc:
            print(t("cli.llm.test_failed", error=exc))
            return EXIT_USAGE
        print(
            t(
                "cli.llm.test_ok",
                text=repr(reply.text.strip()[:80]),
                seconds=reply.seconds,
                speed=reply.tokens_per_second,
            )
        )
    return EXIT_OK


def _config(args: argparse.Namespace) -> int:
    path = config_path()
    if args.init and not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        path.write_text(TEMPLATE, encoding="utf-8")
        print(t("cli.config.created", path=path))
    else:
        print(t("cli.config.exists" if path.exists() else "cli.config.missing", path=path))
    return EXIT_OK


def _threshold_name(field: str) -> str:
    """The name under which a threshold is shown: its option's, without the leading dashes."""
    return _threshold_options(field)[0].removeprefix("--")


def _thresholds_log(store: ThresholdStore) -> None:
    for entry in store.history():
        print(
            f"{entry['date'][:16].replace('T', ' ')}  {entry['author']}: {render(entry['change'])}"
        )
        if "after" in entry:
            changed = {
                _threshold_name(k): v for k, v in entry["after"].items() if entry["before"][k] != v
            }
            print(f"    {changed}")


def _thresholds(args: argparse.Namespace) -> int:
    store = ThresholdStore()
    author = getpass.getuser()
    for notice in store.notices:
        _info(render(notice))
    if args.log:
        _thresholds_log(store)
        return EXIT_OK
    if args.set_pin:
        current = getpass.getpass(t("cli.thresholds.pin_current")) if store.has_pin() else None
        new_pin = getpass.getpass(t("cli.thresholds.pin_new"))
        if new_pin != getpass.getpass(t("cli.thresholds.pin_repeat")):
            raise PinError(t("ui.thresholds.pin_mismatch"))
        store.set_pin(new_pin, author, current)
        print(t("cli.thresholds.pin_saved"))
        return EXIT_OK

    current_values = asdict(store.load())
    changes = {
        name: getattr(args, name)
        for name in current_values
        if name != "count_ai_findings" and getattr(args, name) is not None
    }
    if args.count_ai is not None:
        changes["count_ai_findings"] = args.count_ai
    if changes:
        updated = Thresholds.from_dict({**current_values, **changes})
        store.save(updated, getpass.getpass(t("cli.thresholds.pin_prompt")), author)
        current_values = asdict(updated)
        print(t("cli.thresholds.updated"))
    default = asdict(Thresholds())
    for name, value in current_values.items():
        note = "" if value == default[name] else t("cli.thresholds.default", value=default[name])
        print(f"{_threshold_name(name)} = {value}{note}")
    return EXIT_OK


def _baseline(args: argparse.Namespace) -> int:
    root = _root(args)
    if not args.export and not args.import_:
        raise ValueError(
            t(
                "cli.baseline.need_option",
                export=_name("--export", "--exportar"),
                import_=_name("--import", "--importar"),
            )
        )
    with Store(root) as store:
        if args.import_:
            findings, suppressions = store.import_baseline(args.import_)
            print(t("cli.baseline.imported", findings=findings, suppressions=suppressions))
        if args.export:
            target = args.export.resolve()
            if target.is_relative_to(root):
                raise ValueError(t("cli.baseline.inside"))
            print(t("cli.baseline.exported", count=store.export_baseline(target), path=target))
    return EXIT_OK


def _waiting(line: str) -> None:
    """Elapsed time of a download, rewritten on the same line; only on a terminal."""
    if sys.stderr.isatty():
        print(f"\r{line}", end="", file=sys.stderr, flush=True)


def _info_line(message: str) -> None:
    """A progress line; it first closes the elapsed-time line if one is open."""
    if sys.stderr.isatty():
        print("\r\033[K", end="", file=sys.stderr)
    _info(message)


def _bases(args: argparse.Namespace) -> int:
    if args.update:
        outcome = update_bases(_info_line, on_wait=_waiting)
        if sys.stderr.isatty():
            print("\r\033[K", end="", file=sys.stderr, flush=True)
        for name, state in outcome.items():
            print(f"{name:<9} {render(state)}")
    if args.import_:
        print(t("cli.databases.imported", count=import_bases(args.import_, _info)))
    if args.export:
        print(t("cli.databases.exported", path=args.export, count=export_bases(args.export)))
    print(t("cli.databases.location", path=bases_dir()))
    if not (args.update or args.import_ or args.export):
        for line in data_location_lines():
            print(line)
    for adapter in default_adapters():
        updated = adapter.db_updated_at() if adapter.is_available() else None
        if updated:
            print(t("cli.databases.dated", name=adapter.name, date=updated[:10]))
    return EXIT_OK


def _ui(args: argparse.Namespace) -> int:
    # Deferred import: the CLI must not load Flet to analyze, and Flet is optional.
    if importlib.util.find_spec("flet") is None:
        print(t("cli.ui.no_flet"), file=sys.stderr)
        return EXIT_FAILURE
    from .ui.app import run

    run(web=args.web, port=args.port)
    return EXIT_OK


_COMMANDS = {
    "scan": _scan,
    "report": _report,
    "runs": _runs,
    "forget": _forget,
    "suppress": _suppress,
    "unsuppress": _unsuppress,
    "suppressions": _suppressions,
    "tools": _tools,
    "version": _version,
    "rules": _rules,
    "llm": _llm,
    "config": _config,
    "ui": _ui,
    "databases": _bases,
    "baseline": _baseline,
    "thresholds": _thresholds,
}


def main(argv: Sequence[str] | None = None) -> int:
    # The language is decided before building the parser: the help comes out in it.
    _early_language(argv)
    args = _parser().parse_args(argv)
    hint = maybe_app_hint(tty=sys.stderr.isatty())
    if hint:
        _info(hint)
    command = _COMMAND_ALIASES.get(args.command, args.command)
    try:
        return _COMMANDS[command](args)
    except (
        ValueError,
        LookupError,
        ConfigError,
        OSError,
        tarfile.TarError,
    ) as exc:  # PinError es un ValueError
        _info(t("cli.error", error=exc))
        return EXIT_USAGE


if __name__ == "__main__":
    sys.exit(main())
