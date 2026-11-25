"""Common contract of the tool adapters (`invoke()` + `is_available()`)."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, ClassVar

from ..core.detector import Stack
from ..core.endpoints import Endpoint
from ..core.files import Exclusions
from ..core.finding import Finding
from ..core.masking import mask_generic
from ..core.paths import bases_dir, data_dir
from ..core.processes import no_window
from ..core.profiles import Module
from ..core.vendored import VendoredLibrary
from ..i18n import Message, msg
from ..tool_install import installed_tools_dir

DEFAULT_TIMEOUT_SECONDS = 30 * 60
# Downloading the vulnerability databases (about 2 GB) on a slow link takes far longer.
DOWNLOAD_TIMEOUT_SECONDS = 4 * 60 * 60
HEARTBEAT_SECONDS = 5
_VERSION = re.compile(r"\d+\.\d+\.\d+")

# The analyzed repository may be hostile: its git configuration must not be able
# to launch programs (fsmonitor, hooks, external diff, textconv) or open the network.
# Automatic gc and maintenance are off too: a read-only query must never write into the
# analyzed `.git` (P1).
SAFE_GIT_ENV = {
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_TERMINAL_PROMPT": "0",
    "GIT_NO_LAZY_FETCH": "1",
    "GIT_CONFIG_COUNT": "4",
    "GIT_CONFIG_KEY_0": "core.fsmonitor",
    "GIT_CONFIG_VALUE_0": "false",
    "GIT_CONFIG_KEY_1": "core.hooksPath",
    "GIT_CONFIG_VALUE_1": "/dev/null",
    "GIT_CONFIG_KEY_2": "maintenance.auto",
    "GIT_CONFIG_VALUE_2": "false",
    "GIT_CONFIG_KEY_3": "gc.auto",
    "GIT_CONFIG_VALUE_3": "0",
}


def _git_env() -> dict[str, str]:
    """Environment for read-only git calls on the analyzed folder.

    Inherited `GIT_*` variables are dropped (a `GIT_DIR` would redirect the query), then the
    safe settings apply.
    """
    inherited = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    return {**inherited, **SAFE_GIT_ENV}


def _git_list(root: Path, *args: str) -> list[str] | None:
    """Output of a read-only `git ls-files` on `root` as NUL-separated entries, or None.

    None means "not a usable git work tree" (no repository, git missing, git refused). It runs
    with `-C root` from a temporary directory outside the analyzed folder (P1) and with
    `SAFE_GIT_ENV` (P2: no hooks, fsmonitor, external diff or textconv).
    """
    with tempfile.TemporaryDirectory(prefix="heimdall-git-") as tmp:
        try:
            proc = subprocess.run(
                ["git", "-C", str(root), "ls-files", "-z", *args],
                cwd=tmp,
                env=_git_env(),
                capture_output=True,
                check=False,
                timeout=60,
                **no_window(),
            )
        except (OSError, subprocess.SubprocessError):
            return None
    if proc.returncode != 0:
        return None
    return [e.decode("utf-8", errors="replace") for e in proc.stdout.split(b"\0") if e]


@dataclass(frozen=True)
class GitTracked:
    """Paths git tracks under the analyzed folder (relative, posix)."""

    files: frozenset[str]
    gitlinks: tuple[str, ...] = ()  # submodule folders: their content is not listed

    def tracks(self, relative: str) -> bool:
        return relative in self.files or any(
            relative.startswith(link + "/") for link in self.gitlinks
        )


def git_tracked(root: Path) -> GitTracked | None:
    """Files tracked by git under `root`, or None when it is not inside a git work tree."""
    entries = _git_list(root, "--stage")
    if entries is None:
        return None
    files: set[str] = set()
    links: list[str] = []
    for entry in entries:
        meta, _, path = entry.partition("\t")
        files.add(path)
        if meta.startswith("160000"):
            links.append(path)
    return GitTracked(frozenset(files), tuple(links))


def git_ignored(root: Path) -> list[str] | None:
    """What git ignores under `root` (folders end with "/"), or None outside a work tree."""
    return _git_list(root, "--others", "--ignored", "--exclude-standard", "--directory")


def examples_message(paths: list[str], limit: int = 3) -> Message:
    """Stored "e.g. a, b, c" message; the paths are data, not text."""
    code = "core.examples.many" if len(paths) > limit else "core.examples.few"
    return msg(code, paths=paths[:limit])


def anonymous_registry_env(workdir: Path) -> dict[str, str]:
    """Environment for Trivy to download its database without using Docker credentials.

    The database is public. If Trivy reads `~/.docker/config.json`, it tries to call
    Docker Desktop's credential helper; a desktop application does not have it on its
    PATH and the download fails. Pointing it at an empty folder avoids that and,
    incidentally, no credentials that are not needed get touched.
    """
    empty = workdir / "docker-config"
    empty.mkdir(exist_ok=True)
    return {"DOCKER_CONFIG": str(empty)}


class AdapterError(Exception):
    """The tool failed; the run continues and declares it as a limitation.

    It carries a structured message (`message`, catalog key + data) so that the
    run stores it and it is shown in whichever language applies; `str(error)` is that
    same text in the current language.
    """

    def __init__(self, code: str, /, **params: object) -> None:
        self.message: Message = msg(code, **params)
        super().__init__(str(self.message))


class MissingDatabaseError(AdapterError):
    """The local vulnerability database is missing: this is not a failure, it has to be downloaded.

    `partial` means only one ecosystem's database is missing and the message already explains it.
    """

    def __init__(
        self, code: str = "adapter.db.missing_short", /, *, partial: bool = False, **params: object
    ) -> None:
        super().__init__(code, **params)
        self.partial = partial


def bases_location() -> dict[str, object]:
    """Params for the missing-database texts: where it looked and, if isolated, why."""
    isolated = bool(os.environ.get("HDL_DATA_DIR")) and not os.environ.get("HDL_BASES_DIR")
    return {
        "path": str(bases_dir()),
        "hint": msg("adapter.db.isolated_hint") if isolated else "",
    }


def missing_database() -> Message:
    """The limitation for missing databases; read at call time because the path can change."""
    return msg("adapter.db.missing", **bases_location())


@dataclass(frozen=True)
class ScanContext:
    root: Path  # analyzed folder: read-only
    files: list[str]  # rutas relativas analizables
    modules: frozenset[Module]
    stacks: frozenset[Stack]
    exclusions: Exclusions
    workdir: Path  # temporary directory of the run, outside `root`
    update_dbs: bool = False  # databases are only updated on demand (P4)
    # The user's own rule files, already checked structurally (`core/user_rules.py`).
    user_rules: tuple[Path, ...] = ()
    # Libraries copied into the tree and recognized by their version header.
    vendored: tuple[VendoredLibrary, ...] = ()


@dataclass
class AdapterResult:
    findings: list[Finding] = field(default_factory=list)
    # Broad pattern-only matches (rules tagged CAND): never reported, only handed to the AI.
    candidates: list[Finding] = field(default_factory=list)
    limitations: list[Message] = field(default_factory=list)
    # Plaintext secrets, in memory only, so they are also masked in the snippets
    # of the other tools. They are never serialized.
    secrets: set[str] = field(default_factory=set, repr=False)
    # Endpoint inventory; only the AUTHZ module fills it in.
    endpoints: list[Endpoint] = field(default_factory=list)
    # Component inventory in CycloneDX; only the SBOM module fills it in.
    sbom: dict[str, Any] | None = None
    # User rule files the engine accepted; only the Opengrep adapter fills it in.
    rule_files: list[Path] = field(default_factory=list)


class Adapter(ABC):
    name: ClassVar[str]
    modules: ClassVar[frozenset[Module]]

    def applies(self, ctx: ScanContext) -> bool:
        return bool(self.modules & ctx.modules)

    @abstractmethod
    def is_available(self) -> bool: ...

    @abstractmethod
    def version(self) -> str | None: ...

    @abstractmethod
    def invoke(self, ctx: ScanContext) -> AdapterResult: ...

    def db_updated_at(self) -> str | None:
        """Date of the vulnerability database, if the tool uses one (P6)."""
        return None


_PACKAGE = Path(__file__).resolve().parents[1]
_REPO = _PACKAGE.parents[1]
_BUNDLE = _PACKAGE / "_bundle"


def rules_dirs() -> list[Path]:
    """Own rules: the repository's (development) and the packaged ones (installation)."""
    return [_REPO / "rules" / "heimdall", _BUNDLE / "rules"]


def _extracted_tools() -> Path | None:
    """Binaries of the installed application, extracted once into the data directory.

    They ship compressed in `_bundle/tools.tar.gz`: as loose executables, the macOS
    packager tries to process them and fails. The folder carries the package
    fingerprint, so a new version does not reuse old binaries.
    """
    archive, key_file = _BUNDLE / "tools.tar.gz", _BUNDLE / "tools.key"
    if not archive.is_file() or not key_file.is_file():
        return None
    target = data_dir() / "tools" / key_file.read_text(encoding="utf-8").strip()
    if not (target / ".completo").is_file():
        target.mkdir(parents=True, exist_ok=True, mode=0o700)
        with tarfile.open(archive, "r:gz") as tar:
            tar.extractall(target, filter="data")
        for binary in target.iterdir():
            binary.chmod(0o755)
        (target / ".completo").write_text("ok", encoding="utf-8")
    return target


def find_binary(name: str) -> str | None:
    """Locates a binary: `HDL_<NAME>_BIN`, `tools/bin/`, the package, the data directory's tools
    folder and finally the PATH."""
    override = os.environ.get(f"HDL_{name.upper().replace('-', '_')}_BIN")
    if override:
        return override if Path(override).is_file() else None
    file_name = f"{name}.exe" if sys.platform == "win32" else name
    development = _REPO / "tools" / "bin" / file_name
    if development.is_file():
        return str(development)
    extracted = _extracted_tools()
    if extracted is not None and (extracted / file_name).is_file():
        return str(extracted / file_name)
    # Installed by `hdl tools --install`, or extracted earlier by the desktop app.
    installed = installed_tools_dir()
    if installed is not None and (installed / file_name).is_file():
        return str(installed / file_name)
    return shutil.which(name)


def run(
    cmd: list[str],
    *,
    cwd: Path,
    env: dict[str, str] | None = None,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
    heartbeat: Callable[[int], None] | None = None,
) -> subprocess.CompletedProcess[str]:
    """Launches a tool, without a shell and outside the analyzed folder.

    With `heartbeat`, it is called every few seconds with the elapsed seconds, so a
    long, silent step (a database download) can show that it is still working.
    """
    if heartbeat is not None:
        return _run_with_heartbeat(cmd, cwd, env, timeout, heartbeat)
    try:
        return subprocess.run(
            cmd,
            cwd=cwd,
            env={**os.environ, **(env or {})},
            capture_output=True,
            text=True,
            errors="replace",
            timeout=timeout,
            check=False,
            **no_window(),
        )
    except subprocess.TimeoutExpired as exc:
        raise AdapterError("adapter.timeout", seconds=timeout) from exc
    except OSError as exc:
        raise AdapterError("adapter.run_failed", command=cmd[0], error=str(exc)) from exc


def _run_with_heartbeat(
    cmd: list[str],
    cwd: Path,
    env: dict[str, str] | None,
    timeout: int,
    heartbeat: Callable[[int], None],
) -> subprocess.CompletedProcess[str]:
    started = time.monotonic()
    try:
        with subprocess.Popen(
            cmd,
            cwd=cwd,
            env={**os.environ, **(env or {})},
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            errors="replace",
            **no_window(),
        ) as proc:
            while True:
                try:
                    stdout, stderr = proc.communicate(timeout=HEARTBEAT_SECONDS)
                    break
                except subprocess.TimeoutExpired:
                    elapsed = time.monotonic() - started
                    if elapsed >= timeout:
                        proc.kill()
                        proc.communicate()
                        raise AdapterError("adapter.timeout", seconds=timeout) from None
                    heartbeat(int(elapsed))
    except OSError as exc:
        raise AdapterError("adapter.run_failed", command=cmd[0], error=str(exc)) from exc
    return subprocess.CompletedProcess(cmd, proc.returncode, stdout, stderr)


def stderr_tail(proc: subprocess.CompletedProcess[str], limit: int = 400) -> str:
    """Tail of the error output, masked, for the detail of a failure."""
    text = " ".join((proc.stderr or proc.stdout or "").split())
    return mask_generic(text[-limit:])


class BinaryAdapter(Adapter):
    """Adapter for a tool packaged as an external executable."""

    binary: ClassVar[str]
    version_args: ClassVar[tuple[str, ...]] = ("--version",)

    def _bin(self) -> str:
        path = find_binary(self.binary)
        if path is None:
            raise AdapterError("adapter.binary_missing", binary=self.binary)
        return path

    def is_available(self) -> bool:
        return find_binary(self.binary) is not None

    def version(self) -> str | None:
        path = find_binary(self.binary)
        if path is None:
            return None
        try:
            proc = run([path, *self.version_args], cwd=Path(path).parent, timeout=30)
        except AdapterError:
            return None
        # Each tool surrounds the version with different text; the number is enough.
        match = _VERSION.search(proc.stdout) or _VERSION.search(proc.stderr)
        return match[0] if match else None
