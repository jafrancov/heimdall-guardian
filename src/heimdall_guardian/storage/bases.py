"""Local vulnerability databases: status and transfer to machines without internet (P4)."""

from __future__ import annotations

import tarfile
import tempfile
import time
from collections.abc import Callable
from pathlib import Path

from ..adapters.base import (
    DOWNLOAD_TIMEOUT_SECONDS,
    AdapterError,
    anonymous_registry_env,
    find_binary,
    run,
    stderr_tail,
)
from ..core.locking import database_lock
from ..core.paths import bases_dir
from ..i18n import Message, msg, t

_ROOT = "bases"

# How each database download ends. They are messages (shown in the current language).
UPDATED = msg("bases.state.updated")
NOT_INSTALLED = msg("bases.state.not_installed")


def export_bases(target: Path) -> int:
    """Packs the databases into a `.tar.gz`; returns how many files it included."""
    source = bases_dir()
    files = [p for p in source.rglob("*") if p.is_file()]
    if not files:
        raise LookupError(t("bases.error.nothing_to_export"))
    with tarfile.open(target, "w:gz") as archive:
        for path in files:
            archive.add(path, arcname=f"{_ROOT}/{path.relative_to(source).as_posix()}")
    return len(files)


def import_bases(source: Path, on_progress: Callable[[str], None] | None = None) -> int:
    """Installs the databases from an exported file; rejects any other content.

    It writes into the databases folder, so it holds the update lock meanwhile.
    """
    with database_lock(on_progress):
        return _import_bases(source)


def _import_bases(source: Path) -> int:
    destination = bases_dir()
    with tarfile.open(source, "r:gz") as archive:
        members = archive.getmembers()
        for member in members:
            inside = member.name == _ROOT or member.name.startswith(f"{_ROOT}/")
            if not inside or not (member.isfile() or member.isdir()):
                raise ValueError(t("bases.error.bad_package", name=member.name))
        destination.parent.mkdir(parents=True, exist_ok=True)
        # filter="data" prevents absolute paths, `..`, links and special permissions.
        archive.extractall(destination.parent, filter="data")
    return sum(1 for member in members if member.isfile())


def bases_age_days() -> int | None:
    """Days since the Trivy database was last updated; `None` if it does not exist."""
    database = bases_dir() / "trivy" / "db" / "trivy.db"
    try:
        modified = database.stat().st_mtime
    except OSError:
        return None
    return int((time.time() - modified) // 86400)


# A minimal manifest per supported ecosystem: OSV-Scanner downloads the database of
# each ecosystem it finds, so with this probe folder it fetches them all.
_PROBE_FILES = {
    "requirements.txt": "requests==2.19.0\n",
    "package-lock.json": (
        '{"name":"probe","lockfileVersion":3,"packages":{"":{"name":"probe"},'
        '"node_modules/lodash":{"version":"4.17.20"}}}\n'
    ),
    "composer.lock": '{"packages":[{"name":"monolog/monolog","version":"1.0.0"}],'
    '"packages-dev":[]}\n',
    "packages.lock.json": (
        '{"version":1,"dependencies":{"net8.0":{"Newtonsoft.Json":'
        '{"type":"Direct","resolved":"12.0.1"}}}}\n'
    ),
    "go.mod": "module probe\n\ngo 1.20\n\nrequire golang.org/x/text v0.3.0\n",
    "Cargo.lock": (
        'version = 3\n\n[[package]]\nname = "time"\nversion = "0.1.43"\n'
        'source = "registry+https://github.com/rust-lang/crates.io-index"\n'
    ),
    "Gemfile.lock": (
        "GEM\n  remote: https://rubygems.org/\n  specs:\n    rack (2.0.0)\n\n"
        "PLATFORMS\n  ruby\n\nDEPENDENCIES\n  rack\n"
    ),
    "pubspec.lock": (
        'packages:\n  http:\n    dependency: "direct main"\n    description:\n'
        '      name: http\n      url: "https://pub.dev"\n    source: hosted\n'
        '    version: "0.12.0"\nsdks:\n  dart: ">=2.12.0 <3.0.0"\n'
    ),
    "gradle.lockfile": (
        "# Gradle lockfile\n"
        "org.apache.logging.log4j:log4j-core:2.14.1=compileClasspath,runtimeClasspath\n"
    ),
    "Package.resolved": (
        '{"pins":[{"identity":"swift-nio","kind":"remoteSourceControl",'
        '"location":"https://github.com/apple/swift-nio.git",'
        '"state":{"revision":"0000000000000000000000000000000000000000","version":"2.0.0"}}],'
        '"version":2}\n'
    ),
}
_OSV_OK = (0, 1)  # 1 = it found vulnerabilities in the probe, which is expected


def elapsed_text(seconds: int) -> str:
    """`3 min 05 s` or `40 s`, in the current language."""
    minutes, rest = divmod(max(seconds, 0), 60)
    if minutes:
        return t("bases.elapsed.minutes", minutes=minutes, seconds=f"{rest:02d}")
    return t("bases.elapsed.seconds", seconds=rest)


def update_bases(
    on_progress: Callable[[str], None] | None = None,
    on_wait: Callable[[str], None] | None = None,
) -> dict[str, Message]:
    """Downloads or updates the Trivy and OSV databases without analyzing any project.

    `on_progress` receives one line per step (the size notice, then each database);
    `on_wait`, every few seconds while a database downloads, a line with the time
    elapsed, so a slow link does not look like a frozen program.
    Returns, per tool, `UPDATED` or the reason it could not be done.
    Together with `--actualizar-bases`, it is the only operation that uses the internet.
    It holds the update lock, so the app and the command never download at once.
    """
    with database_lock(on_progress):
        return _update_bases(on_progress, on_wait)


def _update_bases(
    on_progress: Callable[[str], None] | None,
    on_wait: Callable[[str], None] | None = None,
) -> dict[str, Message]:

    def say(message: str) -> None:
        if on_progress is not None:
            on_progress(message)

    outcome: dict[str, Message] = {}
    with tempfile.TemporaryDirectory(prefix="heimdall-bases-") as tmp:
        work = Path(tmp)
        probe = work / "probe"
        probe.mkdir()
        for name, content in _PROBE_FILES.items():
            (probe / name).write_text(content, encoding="utf-8")
        (work / "osv-scanner.toml").write_text("", encoding="utf-8")

        steps: list[tuple[str, str, list[str], dict[str, str], tuple[int, ...]]] = [
            (
                "trivy",
                "trivy",
                [
                    "fs",
                    "--download-db-only",
                    "--cache-dir",
                    str(bases_dir() / "trivy"),
                    "--quiet",
                    "--disable-telemetry",
                    "--skip-version-check",
                    str(probe),
                ],
                anonymous_registry_env(work),
                (0,),
            ),
            (
                "osv",
                "osv-scanner",
                [
                    "scan",
                    "source",
                    "--recursive",
                    "--format",
                    "json",
                    "--config",
                    str(work / "osv-scanner.toml"),
                    "--no-ignore",
                    "--allow-no-lockfiles",
                    "--no-resolve",
                    "--no-call-analysis=all",
                    "--offline-vulnerabilities",
                    "--download-offline-databases",
                    str(probe),
                ],
                {"OSV_SCANNER_LOCAL_DB_CACHE_DIRECTORY": str(bases_dir() / "osv")},
                _OSV_OK,
            ),
        ]
        found = [(step, find_binary(step[1])) for step in steps]
        total = sum(1 for _, path in found if path is not None)
        if total:
            say(t("bases.size_notice"))
        number = 0
        for (name, _binary, args, env, accepted), path in found:
            if path is None:
                outcome[name] = NOT_INSTALLED
                continue
            number += 1
            line = t("bases.downloading", name=name, step=number, total=total)
            say(line)
            (bases_dir() / name).mkdir(parents=True, exist_ok=True)

            def tick(seconds: int, line: str = line) -> None:
                if on_wait is not None:
                    on_wait(t("bases.still_downloading", step=line, elapsed=elapsed_text(seconds)))

            try:
                proc = run(
                    [path, *args],
                    cwd=work,
                    env=env,
                    timeout=DOWNLOAD_TIMEOUT_SECONDS,
                    heartbeat=tick,
                )
            except AdapterError as exc:
                outcome[name] = exc.message
                continue
            outcome[name] = (
                UPDATED
                if proc.returncode in accepted
                else msg("bases.state.failed", detail=stderr_tail(proc, 200))
            )
    return outcome
