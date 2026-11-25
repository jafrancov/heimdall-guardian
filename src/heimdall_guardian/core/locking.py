"""Cross-process locks around database downloads and tool installation.

The desktop app and the `hdl` command share one data directory, so two of them may try to
update the vulnerability databases at once. The lock is an OS-level file lock (not a pid
file): the system releases it if the holder dies.
"""

from __future__ import annotations

import sys
import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import IO

from ..i18n import t
from .paths import bases_dir, data_dir

LOCK_NAME = ".update.lock"
TOOLS_LOCK_NAME = ".install.lock"
LOCK_TIMEOUT_SECONDS = 30 * 60
POLL_SECONDS = 1.0


class DatabaseLockTimeout(ValueError):  # noqa: N818 - a user-facing condition, not a bug
    """The databases stayed locked by another process for too long."""


def lock_path() -> Path:
    return bases_dir() / LOCK_NAME


def _try_lock(handle: IO[str]) -> bool:
    """One non-blocking attempt; `True` if this handle now holds the lock."""
    if sys.platform == "win32":
        import msvcrt

        try:
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError:
            return False
        return True
    import fcntl

    try:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        return False
    return True


def _unlock(handle: IO[str]) -> None:
    if sys.platform == "win32":
        import msvcrt

        try:
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        except OSError:
            pass
        return
    import fcntl

    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


@contextmanager
def file_lock(
    path: Path,
    on_wait: Callable[[str], None] | None = None,
    *,
    timeout: float | None = None,
    poll: float | None = None,
) -> Iterator[None]:
    """Holds an exclusive lock on `path`; waits (telling once) if someone else has it.

    Raises `DatabaseLockTimeout` if it cannot be obtained within `timeout` seconds.
    """
    limit = LOCK_TIMEOUT_SECONDS if timeout is None else timeout
    step = POLL_SECONDS if poll is None else poll
    path.parent.mkdir(parents=True, exist_ok=True)
    # Not a context manager on purpose: the handle must outlive the wait loop.
    handle = path.open("a+", encoding="utf-8")
    try:
        deadline = time.monotonic() + limit
        announced = False
        while not _try_lock(handle):
            if not announced:
                announced = True
                if on_wait is not None:
                    on_wait(t("bases.lock.waiting"))
            if time.monotonic() >= deadline:
                raise DatabaseLockTimeout(t("bases.lock.timeout"))
            time.sleep(step)
        try:
            yield
        finally:
            _unlock(handle)
    finally:
        handle.close()


@contextmanager
def database_lock(
    on_wait: Callable[[str], None] | None = None,
    *,
    timeout: float | None = None,
    poll: float | None = None,
) -> Iterator[None]:
    """Holds the exclusive databases lock (see `file_lock`)."""
    with file_lock(lock_path(), on_wait, timeout=timeout, poll=poll):
        yield


def tools_lock_path() -> Path:
    """Lock of the extracted-tools folder: it lives in `<data>/tools/`, not in the databases."""
    return data_dir() / "tools" / TOOLS_LOCK_NAME


@contextmanager
def tools_lock(
    on_wait: Callable[[str], None] | None = None,
    *,
    timeout: float | None = None,
    poll: float | None = None,
) -> Iterator[None]:
    """Holds the exclusive lock for installing tools, so two `hdl tools --install` do not race."""
    with file_lock(tools_lock_path(), on_wait, timeout=timeout, poll=poll):
        yield
