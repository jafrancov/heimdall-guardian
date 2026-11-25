"""«What's new»: compares the installed tools with their published versions.

It is the only thing in Heimdall Guardian that queries the internet on its own initiative, and only
when asked (`hdl herramientas --novedades`). It downloads and changes nothing: updating a
tool still means editing `tools/tools.toml` and shipping a new release (P4).
It sends nothing from the analyzed code; it only asks for the latest version of each project.
"""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from importlib import metadata
from typing import Any

from .. import __version__
from ..i18n import t

TIMEOUT = 15

# Where each tool publishes its versions: a GitHub repository or a PyPI package.
SOURCES: dict[str, tuple[str, str]] = {
    "gitleaks": ("github", "gitleaks/gitleaks"),
    "trivy": ("github", "aquasecurity/trivy"),
    "osv": ("github", "google/osv-scanner"),
    "opengrep": ("github", "opengrep/opengrep"),
    "bandit": ("pypi", "bandit"),
}

Fetch = Callable[[str], Any]


@dataclass(frozen=True)
class Novelty:
    tool: str
    installed: str | None
    latest: str | None
    page: str
    error: str = ""

    @property
    def status(self) -> str:
        """The status in the current language (computed when requested, not stored)."""
        if self.error:
            return t("updates.status.error", error=self.error)
        if self.installed is None:
            return t("updates.status.not_installed", latest=self.latest)
        if self.latest is None:
            return t("updates.status.no_release")
        if self.outdated:
            return t("updates.status.newer", latest=self.latest)
        return t("updates.status.up_to_date")

    @property
    def outdated(self) -> bool:
        return bool(
            not self.error
            and self.installed is not None
            and self.latest is not None
            and parse_version(self.latest) > parse_version(self.installed)
        )


def parse_version(text: str) -> tuple[int, ...]:
    """«v8.30.1» → (8, 30, 1). Anything that is not a number is ignored."""
    return tuple(int(part) for part in re.findall(r"\d+", text.split("-")[0])[:4])


def fetch_json(url: str) -> Any:
    request = urllib.request.Request(  # noqa: S310 - only fixed https URLs from SOURCES
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": f"heimdall-guardian/{__version__}",
        },
    )
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:  # noqa: S310
        return json.load(response)


def _latest(kind: str, project: str, fetch: Fetch) -> tuple[str | None, str]:
    if kind == "github":
        data = fetch(f"https://api.github.com/repos/{project}/releases/latest")
        tag = str(data.get("tag_name") or "").lstrip("v") or None
        return tag, f"https://github.com/{project}/releases"
    data = fetch(f"https://pypi.org/pypi/{project}/json")
    return str(data["info"]["version"]), f"https://pypi.org/project/{project}/#history"


def check(installed: dict[str, str | None], fetch: Fetch = fetch_json) -> list[Novelty]:
    """One query per tool; if one fails, the others carry on."""
    results = []
    for tool, (kind, project) in SOURCES.items():
        if tool not in installed:
            continue
        try:
            latest, page = _latest(kind, project, fetch)
            results.append(Novelty(tool, installed[tool], latest, page))
        except (OSError, ValueError, KeyError, TypeError) as exc:
            reason = str(getattr(exc, "reason", "") or exc) or type(exc).__name__
            results.append(Novelty(tool, installed[tool], None, "", error=reason))
    return results


# ----------------------------------------------------------- Heimdall Guardian itself

# Same value as `[project.urls] Repository` in pyproject.toml; used if the metadata is missing.
FALLBACK_REPOSITORY = "https://github.com/jafrancov/heimdall-guardian"
_GITHUB_SLUG = re.compile(r"^https://github\.com/([^/\s]+)/([^/\s#?]+?)(?:\.git)?/?$")


def repository_slug(urls: list[str] | None = None) -> str:
    """«owner/repo» of the project's GitHub repository, from the package metadata."""
    if urls is None:
        try:
            urls = metadata.metadata("heimdall-guardian").get_all("Project-URL") or []
        except metadata.PackageNotFoundError:
            urls = []
    for entry in [*urls, f"Repository, {FALLBACK_REPOSITORY}"]:
        label, _, url = entry.partition(",")
        match = _GITHUB_SLUG.match(url.strip())
        if label.strip().lower() == "repository" and match:
            return f"{match.group(1)}/{match.group(2)}"
    owner, repo = _GITHUB_SLUG.match(FALLBACK_REPOSITORY).groups()  # type: ignore[union-attr]
    return f"{owner}/{repo}"


@dataclass(frozen=True)
class SelfUpdate:
    """How the installed Heimdall Guardian compares with its latest published release."""

    installed: str
    latest: str | None
    page: str
    error: str = ""

    @property
    def state(self) -> str:
        """`error`, `no_release`, `newer` (one is available), `current` or `ahead`."""
        if self.error:
            return "error"
        if self.latest is None:
            return "no_release"
        latest, installed = parse_version(self.latest), parse_version(self.installed)
        if not latest:
            return "no_release"
        if latest > installed:
            return "newer"
        return "current" if latest == installed else "ahead"

    @property
    def outdated(self) -> bool:
        return self.state == "newer"

    @property
    def status(self) -> str:
        """The status in the current language (computed when requested, not stored)."""
        state = self.state
        if state == "error":
            return t("updates.self.error", error=self.error)
        if state == "no_release":
            return t("updates.self.no_release")
        if state == "newer":
            return t("updates.self.newer", latest=self.latest)
        if state == "ahead":
            return t("updates.self.ahead", latest=self.latest)
        return t("updates.self.current")


def check_self(fetch: Fetch | None = None, installed: str = __version__) -> SelfUpdate:
    """Asks GitHub for the latest release; a failure is a neutral status, never an exception."""
    slug = repository_slug()
    page = f"https://github.com/{slug}/releases"
    fetch = fetch or fetch_json  # looked up when called, so tests can replace `fetch_json`
    try:
        data = fetch(f"https://api.github.com/repos/{slug}/releases/latest")
        tag = str(data.get("tag_name") or "").strip().lstrip("vV") or None
    except urllib.error.HTTPError as exc:
        exc.close()
        if exc.code == 404:  # the repository has no published release yet
            return SelfUpdate(installed, None, page)
        return SelfUpdate(installed, None, page, error=f"HTTP {exc.code}")
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        reason = str(getattr(exc, "reason", "") or exc) or type(exc).__name__
        return SelfUpdate(installed, None, page, error=reason)
    return SelfUpdate(installed, tag, f"{page}/latest" if tag else page)
