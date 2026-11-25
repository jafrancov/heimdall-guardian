"""Main window: on the left the question (what gets reviewed), on the right the answer.

A single screen. The left panel does not move; the right one goes from
«choose a folder» to the scan progress and from there to the result.
"""

from __future__ import annotations

import contextlib
import getpass
import os
import tempfile
import threading
from dataclasses import asdict, replace
from datetime import date
from pathlib import Path
from typing import Any

import flet as ft

from .. import __version__
from ..adapters import default_adapters, updates
from ..adapters.base import AdapterError
from ..adapters.opengrep import validate_rule_files
from ..core import cli_setup
from ..core.config import Config, ConfigError, save_config
from ..core.files import Exclusions, is_file_pattern, list_folders
from ..core.finding import BaselineStatus, Origin, Severity
from ..core.paths import config_path, data_dir
from ..core.presets import Suggestion, reason, suggest
from ..core.profiles import CUSTOM_PROFILE, PROFILES, Module
from ..core.runner import Plan, ScanCancelled, build_plan, run_scan
from ..core.subprojects import SubProject, find_subprojects
from ..core.user_rules import check_user_rules, own_rule_ids
from ..core.verdict import Thresholds
from ..i18n import Message, get_language, render, t, text_of, tn
from ..i18n import label as code_label
from ..llm.client import LlmClient, LlmError
from ..llm.module import AiRunner, ai_label
from ..report import write_report
from ..storage import (
    Store,
    forget_project,
    list_projects,
    load_project_exclusions,
    save_project_exclusions,
)
from ..storage.bases import UPDATED, bases_age_days, update_bases
from ..storage.thresholds import PinError, ThresholdStore
from . import model as m

QUESTION_WIDTH = 360
NAV_HEIGHT = 56
NAV_WIDE = 1160  # below this window width, the bar shows icons only
MONO = "Menlo, Consolas, monospace"
LICENSES = (
    ("Opengrep", "LGPL-2.1"),
    ("Gitleaks", "MIT"),
    ("Trivy", "Apache-2.0"),
    ("OSV-Scanner", "Apache-2.0"),
    ("Bandit", "Apache-2.0"),
    ("Flet", "Apache-2.0"),
)


def text(value: str, size: float = 15, color: str = m.GRAY_DARK, **kwargs: Any) -> ft.Text:
    return ft.Text(value, size=size, color=color, **kwargs)


def button(label: str, on_click: Any, *, primary: bool = False, on_dark: bool = False) -> Any:
    """Flat-ink rectangular button; the primary one has a background."""
    if primary:
        background, foreground = (m.GOLD, m.NIGHT) if on_dark else (m.NIGHT, m.WHITE)
        return ft.FilledButton(
            content=label,
            on_click=on_click,
            style=ft.ButtonStyle(
                bgcolor=background,
                color=foreground,
                shape=ft.RoundedRectangleBorder(radius=3),
                padding=ft.Padding.symmetric(horizontal=22, vertical=16),
                text_style=ft.TextStyle(size=15, weight=ft.FontWeight.W_600),
            ),
        )
    return ft.TextButton(
        content=label,
        on_click=on_click,
        style=ft.ButtonStyle(
            color=m.SAND if on_dark else m.BRONZE,
            shape=ft.RoundedRectangleBorder(radius=3),
            padding=ft.Padding.symmetric(horizontal=10, vertical=10),
            text_style=ft.TextStyle(size=14, weight=ft.FontWeight.W_500),
        ),
    )


_IMAGES: dict[str, bytes] = {}


def image(name: str, **kwargs: Any) -> ft.Control:
    """Brand image, read from the package.

    It is passed as bytes and not as an `assets` path: that way it looks the same in the
    native window, in the packaged application and in the browser.
    """
    if name not in _IMAGES:
        try:
            _IMAGES[name] = (m.ASSETS / name).read_bytes()
        except OSError:
            _IMAGES[name] = b""
    if not _IMAGES[name]:
        return ft.Container()
    return ft.Image(src=_IMAGES[name], **kwargs)


def export_button(label: str, on_click: Any, icon: Any = None) -> ft.Control:
    """Button with outline and icon: it is recognizable as something that can be pressed."""
    return ft.OutlinedButton(
        content=ft.Row(
            [
                ft.Icon(icon or ft.Icons.DOWNLOAD, size=16, color=m.BRONZE),
                ft.Text(label, size=13, color=m.NIGHT, weight=ft.FontWeight.W_500),
            ],
            spacing=6,
            tight=True,
        ),
        on_click=on_click,
        style=ft.ButtonStyle(
            side=ft.BorderSide(1, m.BRONZE),
            shape=ft.RoundedRectangleBorder(radius=3),
            padding=ft.Padding.symmetric(horizontal=12, vertical=10),
        ),
    )


def icon_button(label: str, icon: Any, on_click: Any, tooltip: str = "") -> ft.Control:
    """Dark-panel button: outline, icon and text, so that it does not get lost."""
    return ft.OutlinedButton(
        content=ft.Row(
            [ft.Icon(icon, size=17, color=m.GOLD), ft.Text(label, size=13, color=m.WHITE)],
            spacing=8,
            tight=True,
        ),
        on_click=on_click,
        tooltip=tooltip or None,
        style=ft.ButtonStyle(
            side=ft.BorderSide(1, m.GRAY_DARK),
            shape=ft.RoundedRectangleBorder(radius=3),
            padding=ft.Padding.symmetric(horizontal=12, vertical=12),
        ),
    )


class App:
    def __init__(self, page: ft.Page) -> None:
        self.page = page
        self.root: Path | None = None
        self.plan: Plan | None = None
        self._suggestions: list[Suggestion] = []
        self._subprojects: list[SubProject] = []
        self.config, config_notice = m.load_startup_config()
        self.profile = self.config.general.default_profile
        if all(self.profile != key for key, _, _ in m.profiles()):
            self.profile = "standard"
        self.custom_modules: set[str] = {str(module) for module in PROFILES["standard"]}
        self.issuer = getpass.getuser()
        self.ai_choice = ""  # AI configuration for this scan; empty = the active one
        self.payload: dict[str, Any] | None = None
        self.severity: str | None = None
        self.search = ""
        self.running = False
        self._cancel = threading.Event()
        self._update_slot: ft.Column | None = None
        self._update_busy = False
        self._tool_rows: dict[str, ft.Text] = {}
        self._panel_view: ft.Control | None = None  # settings, thresholds or about
        self._section = ""  # which navigation bar section opened the panel
        self._panel_title = ""
        self._nav_wide = True
        self._width: float | None = None
        self._progress_view: ft.Control | None = None

        page.padding = 0
        page.bgcolor = m.WHITE
        page.theme = ft.Theme(color_scheme_seed=m.NIGHT, font_family="Helvetica Neue")
        page.theme_mode = ft.ThemeMode.LIGHT
        if not page.web:
            page.window.width, page.window.height = 1240, 800
            page.window.min_width, page.window.min_height = 980, 640

        # Asking each tool for its version takes a few seconds: it is done once, separately.
        # The data is stored, not the text, so it follows the language if it changes.
        self._tool_data: list[tuple[str, bool, str, str]] = []
        page.run_thread(self._load_tool_data)

        page.on_keyboard_event = self._on_key
        self.picker = ft.FilePicker()
        page.services.append(self.picker)
        self.launcher = ft.UrlLauncher()
        page.services.append(self.launcher)

        self.show_suppressed = False
        self._updating_bases = False
        # What the download is doing now, and the labels that show it (panel and Settings).
        self._bases_status = ""
        self._bases_labels: list[ft.Text] = []
        self._bases_slot: ft.Row | None = None  # databases button inside Settings
        self._cli_slot: ft.Column | None = None  # "Command line" section inside Settings
        self._cli_busy: str = ""  # "install" / "uninstall" while the installer runs
        self._python: cli_setup.PythonInfo | None = None
        self._python_checked = False
        # Without databases (or with old ones) updating them is suggested; the user decides.
        age = bases_age_days()
        self.update_dbs = age is None or age > self.config.databases.alert_age_days
        self._recents: list[dict[str, Any]] = []
        self._load_recents()
        self._build_layout()

        initial = os.environ.get("HDL_UI_FOLDER")
        if initial:
            self.set_folder(initial)
            # To test the packaged application without operating the window.
            if os.environ.get("HDL_UI_AUTOSTART") and self.plan is not None:
                self.start_scan()
        else:
            self.refresh()
        if config_notice:
            self.notify(config_notice)
        if m.tour_pending(self.config):
            self.show_tour()  # the command offer follows when the tour ends
        else:
            self._maybe_offer_cli()

    def _build_layout(self) -> None:
        """Builds the left panel and the central part.

        Done once at startup and again if the user changes the language; in between only
        the columns are refilled (`_fill_question`): recreating the logo made the window
        flicker.
        """
        page = self.page
        page.title = t("ui.window.title")
        page.controls.clear()
        self._q_project = ft.Column(spacing=6)
        self._q_profiles = ft.Column(spacing=2)
        self._q_extras = ft.Column(spacing=6)
        self._q_actions = ft.Column(spacing=6)
        self._q_recent = ft.Column(spacing=0)
        self._q_footer = ft.Row(spacing=0)
        # The logo is fixed: it never scrolls with the options.
        brand = ft.Container(
            content=ft.Column(
                [image("logo.png", width=150), text(m.tagline(), 13, m.SAND)],
                spacing=0,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            alignment=ft.Alignment.CENTER,
            on_click=self.go_home,
            tooltip=t("ui.brand.home_tip"),
        )
        # Only this column scrolls: project, how thorough, folders and databases.
        scrolling = ft.Column(
            [
                self._q_project,
                ft.Container(height=8),
                ft.Divider(height=1, thickness=1, color=m.GOLD),
                ft.Container(height=4),
                text(t("ui.question.depth"), 13, m.GOLD, weight=ft.FontWeight.W_600),
                self._q_profiles,
                self._q_extras,
                ft.Container(height=6),
                self._q_actions,
                self._q_recent,
            ],
            spacing=6,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )
        # «Analyze» (or «Cancel») stays fixed at the bottom: it must never fall out of view.
        self.question = ft.Container(
            content=ft.Column(
                [brand, ft.Container(height=4), scrolling, self._q_footer],
                spacing=10,
                expand=True,
            ),
            width=QUESTION_WIDTH,
            bgcolor=m.NIGHT,
            padding=ft.Padding.only(left=28, right=20, top=18, bottom=22),
        )
        self.answer = ft.Container(expand=True, padding=ft.Padding.all(48))
        # The seal goes behind the answer, as a watermark.
        watermark = ft.Container(
            content=image("sello.png", width=340, opacity=0.08),
            alignment=ft.Alignment.BOTTOM_RIGHT,
            padding=ft.Padding.only(right=28, bottom=16),
        )
        body = ft.Container(
            content=ft.Stack([watermark, self.answer], expand=True),
            expand=True,
            bgcolor=m.WHITE,
        )
        # The navigation bar sits above the central part and is built only once.
        self._nav_context = text("", 15, m.GRAY_DARK, weight=ft.FontWeight.W_600)
        self._nav_items = ft.Row(spacing=2)
        self._nav = ft.Container(
            content=ft.Row(
                [
                    ft.Container(content=self._nav_context, expand=True),
                    self._nav_items,
                ],
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            height=NAV_HEIGHT,
            bgcolor=m.WHITE,
            padding=ft.Padding.only(left=32, right=16),
            border=ft.Border.only(bottom=ft.BorderSide(1, m.LINE)),
        )
        right = ft.Column([self._nav, body], spacing=0, expand=True)
        page.add(ft.Row([self.question, right], spacing=0, expand=True))
        page.on_resize = self._on_resize
        self._fill_nav()

    # ------------------------------------------------------------ estado

    def refresh(self) -> None:
        """Updates both sides. For changes to the left panel only, use `_sync_question`."""
        self._fill_question()
        if self._panel_view is not None:
            self.answer.content = self._panel_view
        elif self.running:
            self.answer.content = self._progress_view
        elif self.payload is not None:
            self.answer.content = self._results()
        else:
            self.answer.content = self._home()
        self._fill_nav()
        self.page.update()

    def _on_resize(self, event: Any = None) -> None:
        """With a narrow window, the navigation bar shows only the icons."""
        self._width = getattr(event, "width", None) or self.page.width
        wide = self._nav_is_wide()
        if wide != self._nav_wide:
            self._fill_nav()
            self._nav.update()

    def _nav_is_wide(self) -> bool:
        width = self._width or self.page.width
        return not width or width >= NAV_WIDE

    def _active_section(self) -> str | None:
        return self._section if self._panel_view is not None else None

    def _fill_nav(self) -> None:
        """Fills the navigation bar: context on the left, sections on the right."""
        self._nav_wide = self._nav_is_wide()
        active = self._active_section()
        self._nav_context.value = m.nav_context(
            self.plan.root.name if self.plan else None, self._panel_title if active else None
        )
        entries = (
            ("home", ft.Icons.ADD, "ui.nav.new_analysis", "ui.nav.new_analysis_tip", self.go_home),
            (
                "coverage",
                ft.Icons.SHIELD_OUTLINED,
                "ui.nav.coverage",
                "ui.nav.coverage_tip",
                self.show_coverage,
            ),
            (
                "settings",
                ft.Icons.SETTINGS_OUTLINED,
                "ui.nav.settings",
                "ui.nav.settings_tip",
                self.show_settings,
            ),
            ("about", ft.Icons.INFO_OUTLINE, "ui.nav.about", "ui.nav.about_tip", self.show_about),
        )
        self._nav_items.controls = [
            self._nav_item(key, icon, t(label), t(tip), handler, key == active)
            for key, icon, label, tip, handler in entries
        ]

    def _nav_item(
        self, key: str, icon: Any, label: str, tip: str, handler: Any, active: bool
    ) -> ft.Control:
        color = m.BRONZE if active else m.GRAY_DARK
        parts: list[ft.Control] = [ft.Icon(icon, size=18, color=color)]
        if self._nav_wide:
            parts.append(
                text(
                    label, 14, color, weight=ft.FontWeight.W_600 if active else ft.FontWeight.W_500
                )
            )

        def click(event: Any) -> None:
            # Pressing the open section closes it and brings back what was underneath.
            if active:
                self._close()
            else:
                handler(event)

        return ft.Container(
            content=ft.Row(parts, spacing=6, tight=True),
            height=NAV_HEIGHT - 1,
            padding=ft.Padding.symmetric(horizontal=12),
            alignment=ft.Alignment.CENTER,
            on_click=click,
            tooltip=tip,
            ink=True,
            border=ft.Border.only(bottom=ft.BorderSide(2, m.BRONZE if active else "#00000000")),
        )

    def _sync_question(self) -> None:
        """Redraws only the left panel; the central part is left alone."""
        self._fill_question()
        self.question.update()

    def _on_key(self, event: Any) -> None:
        """⌘N or Ctrl+N: new scan."""
        if (event.meta or event.ctrl) and str(event.key).lower() == "n":
            self.go_home()

    def set_folder(self, raw: str) -> None:
        try:
            self.plan = self._plan(Path(raw).expanduser())
        except ValueError as exc:
            self.notify(str(exc))
            return
        self.root = self.plan.root
        self.payload = None
        self._panel_view = None
        self.severity = None
        try:
            with Store(self.root) as store:
                self.payload = store.payload()
            previous = self.payload["run"]["profile"]
            if previous in PROFILES and previous != self.profile:
                # Repeating the same profile is suggested: that way the comparison is fair.
                self.profile = previous
                self.plan = self._plan(self.root)
        except (LookupError, ValueError):
            pass  # no previous runs: the invitation to scan is shown
        self.refresh()

    def _load_tool_data(self) -> None:
        data = []
        for adapter in default_adapters():
            available = adapter.is_available()
            version = (adapter.version() or "") if available else ""
            database = (adapter.db_updated_at() or "")[:10] if available else ""
            data.append((adapter.name, available, version, database))
        self._tool_data = data

    def _tool_lines(self) -> list[str]:
        """One line per tool, in the current language."""
        lines = []
        for name, available, version, database in self._tool_data:
            if available:
                detail = version or t("ui.tool.unknown_version")
                if database:
                    detail = t("ui.tool.database", detail=detail, date=database)
            else:
                detail = t("ui.tool.not_installed")
            lines.append(f"{m.tool_name(name)}: {detail}")
        return [*lines, *m.data_lines()] if lines else []

    def go_home(self, _: Any = None) -> None:
        """Leaves the previous scan and returns to the welcome screen."""
        if self.running:
            self.notify(t("ui.scan.busy"))
            return
        self.root = self.plan = self.payload = None
        self._suggestions = []
        self._subprojects = []
        self.severity, self.search = None, ""
        self._panel_view = None
        self.refresh()

    def set_profile(self, profile: str) -> None:
        if self.running:
            return
        self.profile = profile
        self._replan()

    def _plan(self, root: Path) -> Plan:
        custom = frozenset(Module(code) for code in self.custom_modules)
        plan = build_plan(
            root,
            profile=self.profile,
            custom_modules=custom if self.profile == CUSTOM_PROFILE else None,
            exclusions=self.config.exclusions.to_exclusions(
                *load_project_exclusions(root), root=root
            ),
            extra_rule_dirs=self.config.rules.extra_dirs,
        )
        self._suggestions = suggest(plan.root, plan.stacks, plan.exclusions)
        self._subprojects = find_subprojects(plan.root, plan.tree.files)
        return plan

    def _replan(self) -> None:
        if self.root is not None:
            try:
                self.plan = self._plan(self.root)
            except ValueError as exc:
                self.notify(str(exc))
        self._sync_question()

    def toggle_module(self, code: str, enabled: bool) -> None:
        if enabled:
            self.custom_modules.add(code)
        elif len(self.custom_modules) > 1:
            self.custom_modules.discard(code)
        self._replan()

    def notify(self, message: str) -> None:
        self.page.show_dialog(ft.SnackBar(content=ft.Text(message), bgcolor=m.GRAY_DARK))

    # ---------------------------------------------------------- pregunta

    def _bases_action(self, *, on_dark: bool) -> ft.Control:
        """The update button, or a loading indicator while it downloads."""
        if self._updating_bases:
            ink = m.GOLD if on_dark else m.BRONZE
            label = text(
                self._bases_status or t("ui.bases.downloading"), 13, m.WHITE if on_dark else m.NIGHT
            )
            self._bases_labels.append(label)
            return ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.ProgressRing(width=16, height=16, stroke_width=2.5, color=ink),
                                label,
                            ],
                            spacing=10,
                        ),
                        text(t("bases.size_notice"), 12, m.SAND if on_dark else m.GRAY_DARK),
                    ],
                    spacing=6,
                ),
                padding=ft.Padding.symmetric(horizontal=10, vertical=10),
            )
        action: ft.Control = button(
            t("ui.action.update_bases_now"),
            self.update_bases_now,
            primary=not on_dark,
            on_dark=on_dark,
        )
        return action

    def update_bases_now(self, _: Any = None) -> None:
        """Downloads the vulnerability databases without scanning anything."""
        if self._updating_bases or self.running:
            return
        self._updating_bases = True
        self._bases_status = ""
        self._refresh_bases_ui()

        def show(line: str) -> None:
            # Only the label text changes: rebuilding the panel every few seconds flickers.
            self._bases_status = line
            for label in self._bases_labels:
                label.value = line
            self.page.update()

        def work() -> None:
            outcome: dict[str, Any]
            try:
                outcome = update_bases(show, on_wait=show)
            except Exception as exc:
                outcome = {t("ui.bases.download_label"): str(exc)}
            finally:
                self._updating_bases = False
                self._bases_status = ""
            failed = {name: state for name, state in outcome.items() if state != UPDATED}
            if failed:
                detail = "; ".join(f"{name}: {state}" for name, state in failed.items())
                self.notify(t("ui.bases.partial_failure", detail=detail))
            else:
                self.update_dbs = False
                self.notify(t("ui.bases.updated"))
            self._load_tool_data()
            self._refresh_bases_ui()

        self.page.run_thread(work)

    def _refresh_bases_ui(self) -> None:
        """Updates the button or the indicator in the left panel and in Settings."""
        self._bases_labels = []
        self._fill_question()
        if self._bases_slot is not None:
            self._bases_slot.controls = [
                self._bases_action(on_dark=False),
                text(self._bases_note(), 13, m.GRAY_DARK),
            ]
        self.page.update()

    def _bases_note(self) -> str:
        age = bases_age_days()
        if age is None:
            return t("ui.bases.none")
        if age == 0:
            return t("ui.bases.updated_today")
        return tn("ui.bases.updated_ago", age)

    def _load_recents(self) -> None:
        """Reads the project list once; `_fill_question` runs too often to query storage."""
        self._recents = list_projects()

    def _recent_compact(self, item: dict[str, Any]) -> ft.Control:
        active = bool(item["active"])
        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(width=8, height=8, border_radius=4, bgcolor=item["tone"]),
                    ft.Column(
                        [
                            text(
                                item["name"],
                                14,
                                m.WHITE if active else m.SAND,
                                weight=ft.FontWeight.W_600 if active else None,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                            text(item["date"], 11, m.GRAY_MID),
                        ],
                        spacing=0,
                        expand=True,
                    ),
                ],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding.symmetric(vertical=6),
            ink=True,
            tooltip=item["path"],
            on_click=None if active else (lambda _: self.set_folder(item["path"])),
        )

    def _subproject_controls(self) -> list[ft.Control]:
        root = self.root
        if root is None:
            return []
        controls: list[ft.Control] = [
            ft.Container(height=6),
            text(
                tn("ui.subprojects.title", len(self._subprojects)),
                13,
                m.GOLD,
                weight=ft.FontWeight.W_600,
            ),
            text(t("ui.subprojects.help"), 12, m.SAND),
        ]
        for row in m.subproject_rows(self._subprojects):
            controls.append(
                ft.Container(
                    ink=True,
                    padding=ft.Padding.symmetric(vertical=4),
                    tooltip=t("ui.subprojects.open_tip", name=row["name"]),
                    on_click=lambda _, p=row["path"]: self.set_folder(str(root / p)),
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.SUBDIRECTORY_ARROW_RIGHT, size=14, color=m.SAND),
                            ft.Column(
                                [
                                    text(
                                        row["name"],
                                        13,
                                        m.WHITE,
                                        max_lines=1,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                    ),
                                    text(row["stacks"], 11, m.GRAY_MID),
                                ],
                                spacing=0,
                                expand=True,
                            ),
                        ],
                        spacing=6,
                    ),
                )
            )
        return controls

    def _fill_question(self) -> None:
        plan = self.plan
        if plan is None:
            self._q_project.controls = [
                text(t("ui.question.which_folder"), 22, m.WHITE, weight=ft.FontWeight.BOLD),
                text(t("ui.question.local_note"), 13, m.SAND),
            ]
        else:
            stacks = ", ".join(hit.stack for hit in plan.stacks) or t("ui.question.no_stack")
            self._q_project.controls = [
                text(plan.root.name, 22, m.WHITE, weight=ft.FontWeight.BOLD),
                text(
                    str(plan.root.parent),
                    12,
                    m.SAND,
                    max_lines=2,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
                text(
                    t(
                        "ui.question.files_stacks",
                        count=len(plan.tree.analyzable),
                        stacks=stacks,
                    ),
                    13,
                    m.SAND,
                ),
            ]
            if self._subprojects and not self.running and self.root is not None:
                self._q_project.controls.extend(self._subproject_controls())
        self._q_profiles.controls = [self._profile_option(*profile) for profile in m.profiles()]
        self._q_extras.controls = self._profile_extras()
        recent = (
            m.recent_projects(self._recents, str(self.root) if self.root else None)
            if not self.running
            else []
        )
        self._q_recent.controls = (
            [
                ft.Container(height=8),
                ft.Divider(height=1, thickness=1, color=m.GOLD),
                ft.Container(height=4),
                text(t("ui.recent.title"), 13, m.GOLD, weight=ft.FontWeight.W_600),
                *[self._recent_compact(item) for item in recent],
            ]
            if recent
            else []
        )
        self._q_actions.controls = [
            ft.Row(
                [
                    button(
                        t("ui.action.choose_folder" if plan is None else "ui.action.change_folder"),
                        self.pick_folder,
                        primary=plan is None,
                        on_dark=True,
                    ),
                    button(t("ui.action.preview"), self.show_preview, on_dark=True),
                ],
                spacing=4,
                visible=not self.running,
            ),
            ft.Row(
                [
                    button(
                        tn("ui.action.skip_folders_suggested", len(self._suggestions))
                        if self._suggestions
                        else t("ui.action.skip_folders"),
                        self.show_folders,
                        on_dark=True,
                    )
                ],
                visible=plan is not None and not self.running,
            ),
            ft.Column(
                [
                    ft.Checkbox(
                        label=t("ui.action.update_bases_on_scan"),
                        value=self.update_dbs,
                        on_change=lambda e: setattr(self, "update_dbs", bool(e.control.value)),
                        label_style=ft.TextStyle(size=13, color=m.WHITE),
                        check_color=m.NIGHT,
                        active_color=m.GOLD,
                        border_side=ft.BorderSide(1.5, m.SAND),
                    ),
                    text(self._bases_note(), 12, m.SAND),
                    self._bases_action(on_dark=True),
                ],
                spacing=0,
                visible=plan is not None and not self.running,
            ),
        ]
        if self.running:
            main = icon_button(t("ui.common.cancel"), ft.Icons.CLOSE, self.cancel_scan)
        else:
            main = button(t("ui.action.analyze"), self.start_scan, primary=True, on_dark=True)
        main.expand = True
        self._q_footer.controls = [main]
        self._q_footer.visible = plan is not None

    def _uses_ai(self) -> bool:
        if self.profile == CUSTOM_PROFILE:
            return "AI" in self.custom_modules
        return Module.AI in PROFILES.get(self.profile, frozenset())

    def _ai_warning(self) -> list[ft.Control]:
        if not self._uses_ai():
            return []
        return [
            *self._ai_selector(),
            ft.Container(
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.HOURGLASS_BOTTOM, size=16, color=m.GOLD),
                        text(m.ai_time_warning(), 12, m.GOLD_LIGHT, expand=True),
                    ],
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
                padding=ft.Padding.only(left=14, top=6, right=4),
            ),
        ]

    def _ai_selector(self) -> list[ft.Control]:
        """With several AI configurations, which one to use in this scan."""
        llm = self.config.llm
        if len(llm.destinations) < 2:
            return []
        current = self.ai_choice if llm.destination(self.ai_choice) else llm.active_destination

        def models_of(name: str) -> str:
            destination = llm.destination(name)
            return m.destination_label(destination).partition(" · ")[2] if destination else ""

        models = text(models_of(current), 12, m.SAND)

        def select(e: Any) -> None:
            self.ai_choice = e.control.value or ""
            models.value = models_of(self.ai_choice)
            models.update()

        choice = ft.Dropdown(
            label=t("ui.ai.choice_label"),
            value=current,
            options=[ft.DropdownOption(key=d.name, text=d.name) for d in llm.destinations],
            dense=True,
            text_size=13,
            color=m.WHITE,
            border_color=m.SAND,
            label_style=ft.TextStyle(color=m.SAND, size=12),
            on_select=select,
        )
        return [
            ft.Container(
                content=ft.Column([choice, models], spacing=4),
                padding=ft.Padding.only(left=14, top=8, right=4),
            )
        ]

    def _profile_extras(self) -> list[ft.Control]:
        """What the chosen profile asks for: the modules of the custom one or who issues."""
        return [*self._profile_inputs(), *self._ai_warning()]

    def _profile_inputs(self) -> list[ft.Control]:
        if self.profile == CUSTOM_PROFILE:
            boxes: list[ft.Control] = [
                ft.Container(
                    content=ft.Checkbox(
                        label=label,
                        value=code in self.custom_modules,
                        on_change=lambda e, c=code: self.toggle_module(c, bool(e.control.value)),
                        label_style=ft.TextStyle(size=13, color=m.WHITE),
                        check_color=m.NIGHT,
                        active_color=m.GOLD,
                        border_side=ft.BorderSide(1.5, m.SAND),
                    ),
                    width=146,
                )
                for code, label in m.module_names().items()
            ]
            return [ft.Row(boxes, wrap=True, spacing=0, run_spacing=0)]
        if self.profile == "vendor":
            field = ft.TextField(
                value=self.issuer,
                label=t("ui.custom.issuer"),
                dense=True,
                text_size=14,
                color=m.WHITE,
                border_color=m.SAND,
                label_style=ft.TextStyle(color=m.SAND, size=12),
                cursor_color=m.WHITE,
                on_change=lambda e: setattr(self, "issuer", e.control.value or ""),
            )
            return [ft.Container(content=field, padding=ft.Padding.only(left=14, top=6))]
        return []

    def _profile_option(self, key: str, label: str, description: str) -> ft.Control:
        selected = key == self.profile
        steps = " · ".join(m.profile_steps(key, self.custom_modules))
        return ft.Container(
            content=ft.Column(
                [
                    text(
                        label,
                        16,
                        m.GOLD if selected else m.WHITE,
                        weight=ft.FontWeight.W_600 if selected else ft.FontWeight.W_400,
                    ),
                    text(description, 12, m.SAND, visible=selected),
                    # Which processes this option runs, so the choice is an informed one.
                    text(
                        t("ui.profile.steps", steps=steps),
                        12,
                        m.WHITE,
                        visible=selected and bool(steps),
                    ),
                ],
                spacing=3,
                tight=True,
            ),
            padding=ft.Padding.only(left=14, top=8, bottom=8, right=8),
            bgcolor=m.CHARCOAL if selected else None,
            border=ft.Border.only(left=ft.BorderSide(3, m.GOLD if selected else "#00000000")),
            on_click=lambda _: self.set_profile(key),
            ink=True,
        )

    # ------------------------------------------------------------ inicio

    def _home(self) -> ft.Control:
        if self.plan is not None:
            return ft.Column(
                [
                    text(
                        t("ui.home.not_analyzed", name=self.plan.root.name),
                        34,
                        m.NIGHT,
                        weight=ft.FontWeight.BOLD,
                    ),
                    text(t("ui.home.not_analyzed_hint"), 17),
                ],
                spacing=14,
            )

        path_field = ft.TextField(
            hint_text=t("ui.home.path_hint"),
            border=ft.InputBorder.UNDERLINE,
            border_color=m.GRAY_LIGHT,
            text_size=15,
            on_submit=lambda e: self.set_folder(e.control.value),
        )
        recents = list_projects()
        rows: list[ft.Control] = [self._recent_row(item) for item in recents[:8]]
        watch = m.watch_line(recents)
        checks = [
            (ft.Icons.KEY, "SEC"),
            (ft.Icons.INVENTORY_2_OUTLINED, "DEP"),
            (ft.Icons.CODE, "SAST"),
            (ft.Icons.LOCK_OPEN, "AUTHZ"),
        ]
        return ft.Column(
            [
                text(m.motto(), 15, m.BRONZE, weight=ft.FontWeight.W_600),
                text(
                    t("ui.home.title"),
                    32,
                    m.NIGHT,
                    weight=ft.FontWeight.BOLD,
                ),
                text(t("ui.home.subtitle"), 16),
                ft.Container(height=4),
                ft.Row(
                    [
                        button(t("ui.action.choose_folder"), self.pick_folder, primary=True),
                        ft.Container(content=path_field, width=420),
                    ],
                    spacing=18,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Container(height=10),
                # What it watches: four fronts, without cards.
                ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Icon(icon, size=22, color=m.BRONZE),
                                text(m.module_name(code), 15, m.NIGHT, weight=ft.FontWeight.W_600),
                                text(t(f"ui.home.check.{code.lower()}"), 13, m.GRAY_DARK),
                            ],
                            spacing=4,
                            expand=True,
                        )
                        for icon, code in checks
                    ],
                    spacing=22,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
                ft.Container(height=10),
                ft.Divider(height=1, thickness=1, color=m.GOLD),
                text(
                    watch or t("ui.home.no_projects"),
                    14,
                    m.NIGHT,
                    weight=ft.FontWeight.W_600,
                ),
                ft.Column(rows, spacing=0, scroll=ft.ScrollMode.AUTO, expand=True),
            ],
            spacing=10,
            expand=True,
        )

    def _recent_row(self, item: dict[str, Any]) -> ft.Control:
        headline, _ = m.verdict(item)
        return ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            text(item["name"], 16, m.NIGHT, weight=ft.FontWeight.W_600),
                            text(
                                item["path"],
                                12,
                                m.GRAY_MID,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                        ],
                        spacing=1,
                        expand=True,
                    ),
                    text(f"{headline} {item['started'][:10]}", 13, m.GRAY_DARK),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        icon_color=m.GRAY_MID,
                        icon_size=20,
                        tooltip=t("ui.recent.remove_tip"),
                        on_click=lambda _: self.confirm_forget(item),
                    ),
                ],
            ),
            padding=ft.Padding.symmetric(vertical=12),
            border=ft.Border.only(bottom=ft.BorderSide(1, m.LINE)),
            on_click=lambda _: self.set_folder(item["path"]),
            ink=True,
        )

    def confirm_forget(self, item: dict[str, Any]) -> None:
        def forget(_: Any) -> None:
            forget_project(item["id"])
            self._load_recents()
            self._close()
            if self.root is not None and str(self.root) == item["path"]:
                self.go_home()
            else:
                self.refresh()
            self.notify(t("ui.recent.forgotten", name=item["name"]))

        self._dialog(
            t("ui.recent.forget_title", name=item["name"]),
            [
                text(t("ui.recent.forget_body"), 15),
                text(
                    t("ui.recent.forget_irreversible"), 14, m.SEVERITY_COLORS[Severity.CRITICAL][0]
                ),
            ],
            [
                button(t("ui.common.cancel"), self._close),
                button(t("ui.recent.remove_tip"), forget, primary=True),
            ],
        )

    async def pick_folder(self, _: Any = None) -> None:
        chosen = await self.picker.get_directory_path(dialog_title=t("ui.picker.choose"))
        if chosen:
            self.set_folder(chosen)

    # ----------------------------------------------------------- scan

    def start_scan(self, _: Any = None) -> None:
        if self.plan is None or self.running:
            return
        self.running = True
        self._cancel.clear()
        self._tool_rows = {}
        self._progress_list = ft.Column(spacing=0)
        self._progress_view = ft.Column(
            [
                text(
                    t("ui.scan.running", name=self.plan.root.name),
                    34,
                    m.NIGHT,
                    weight=ft.FontWeight.BOLD,
                ),
                text(t("ui.scan.keep_working"), 17),
                text(m.ai_time_warning(), 14, m.BRONZE, visible=self._uses_ai()),
                ft.Container(height=12),
                ft.ProgressBar(color=m.GOLD, bgcolor=m.PAPER, bar_height=3),
                self._progress_list,
            ],
            spacing=10,
        )
        self._panel_view = None
        self.answer.content = self._progress_view
        self._fill_question()
        self.page.update()
        self.page.run_thread(self._scan)

    def cancel_scan(self, _: Any = None) -> None:
        self._cancel.set()
        self.notify(t("ui.scan.cancel_notice"))

    def _plan_stacks(self) -> list[str]:
        return [hit.stack.value for hit in self.plan.stacks] if self.plan else []

    def _on_progress(self, tool: str, status: str | Message) -> None:
        labels = {
            "start": t("ui.scan.status.start"),
            "ran": t("ui.scan.status.done"),
            "skipped": t("ui.scan.status.skipped"),
            "error": t("ui.scan.status.error"),
        }
        row = self._tool_rows.get(tool)
        if row is None:
            row = text("", 14, m.GRAY_MID)
            self._tool_rows[tool] = row
            self._progress_list.controls.append(
                ft.Container(
                    content=ft.Row(
                        [
                            text(m.tool_name(tool, self._plan_stacks()), 16, m.NIGHT, expand=True),
                            row,
                        ]
                    ),
                    padding=ft.Padding.symmetric(vertical=10),
                    border=ft.Border.only(bottom=ft.BorderSide(1, m.LINE)),
                )
            )
        if not isinstance(status, str):
            # «reviewing 23 of 150» (AI): a structured message, in the current language.
            row.value = render(status)
            row.color = m.NIGHT
            self.page.update()
            return
        if status == "start" and tool in ("summary", "result"):
            row.value = t("ui.scan.status.in_progress")  # they are not tools that analyze the code
        else:
            row.value = labels.get(status, status)
        running = status not in labels or status == "start"
        row.color = m.NIGHT if running else m.GRAY_MID
        self.page.update()

    def _scan(self) -> None:
        plan = self.plan
        assert plan is not None  # noqa: S101 - start_scan guarantees it
        try:
            llm = self.config.llm
            if self.ai_choice and llm.destination(self.ai_choice) is not None:
                llm = llm.using(self.ai_choice)
            ai = AiRunner(llm) if Module.AI in plan.modules else None
            with Store(plan.root) as store:
                result = run_scan(
                    plan,
                    ai=ai,
                    on_progress=self._on_progress,
                    cancelled=self._cancel.is_set,
                    db_alert_days=self.config.databases.alert_age_days,
                    update_dbs=self.update_dbs,
                )
                # The verdict is only issued when receiving vendor code.
                threshold_store = ThresholdStore() if plan.profile == "vendor" else None
                thresholds = threshold_store.load() if threshold_store else None
                result.limitations += threshold_store.notices if threshold_store else []
                issuer = self.issuer.strip() or getpass.getuser()
                self._on_progress("result", "start")
                store.record(result, thresholds=thresholds, issuer=issuer)
            self._load_recents()
            self.payload = result.to_dict()
            self.severity = None
            self.update_dbs = False
        except ScanCancelled:
            self.notify(t("ui.scan.cancelled"))
        except (ValueError, ConfigError, OSError) as exc:
            self.notify(t("ui.scan.failed", error=exc))
        finally:
            self.running = False
            self.refresh()

    # --------------------------------------------------------- resultados

    def _results(self) -> ft.Control:
        payload = self.payload
        assert payload is not None  # noqa: S101
        summary = payload["summary"]
        headline, why = m.verdict(summary, payload.get("verdict"))
        baseline = payload.get("baseline") or {}
        endpoints = payload.get("endpoints") or []
        open_endpoints = sum(1 for e in endpoints if e["has_auth"] is False)

        links: list[ft.Control] = [
            text(t("ui.result.save_report"), 13, m.GRAY_DARK),
            export_button("HTML", lambda _: self.page.run_task(self.export, "html")),
            export_button("PDF", lambda _: self.page.run_task(self.export, "pdf")),
            export_button("Excel", lambda _: self.page.run_task(self.export, "xlsx")),
            export_button("SARIF", lambda _: self.page.run_task(self.export, "sarif")),
        ]
        if endpoints:
            links.append(
                export_button(
                    t("ui.result.endpoints", count=len(endpoints), open=open_endpoints),
                    self.show_endpoints,
                    ft.Icons.LIST_ALT,
                )
            )
        links.append(export_button(t("ui.result.how"), self.show_how, ft.Icons.FACT_CHECK_OUTLINED))
        if m.plan_rows(payload):
            links.append(export_button(t("ui.plan.button"), self.show_plan, ft.Icons.FLAG_OUTLINED))
        if payload["limitations"]:
            count = len(payload["limitations"])
            links.append(
                export_button(
                    tn("ui.result.limitations", count),
                    self.show_limitations,
                    ft.Icons.INFO_OUTLINE,
                )
            )

        header = ft.Column(
            [
                text(payload["project"]["name"], 18, m.GRAY_DARK, weight=ft.FontWeight.W_600),
                text(
                    headline,
                    34,
                    m.verdict_tone(summary, payload.get("verdict")),
                    weight=ft.FontWeight.BOLD,
                ),
                text(why, 17, m.NIGHT),
                text(
                    t(
                        "ui.result.context",
                        comparison=m.comparison(summary, baseline.get("previous_run")),
                        date=payload["run"]["started"][:10],
                        profile=m.profile_name(payload["run"]["profile"]),
                    ),
                    13,
                    m.GRAY_MID,
                ),
                text(
                    m.run_facts(payload)[-1],
                    13,
                    m.GRAY_DARK,
                    max_lines=2,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
                ft.Row(
                    links,
                    spacing=8,
                    run_spacing=8,
                    wrap=True,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ],
            spacing=6,
        )
        self._finding_list = ft.ListView(expand=True, spacing=0)
        self._strata_column = ft.Column(
            spacing=0, width=220, horizontal_alignment=ft.CrossAxisAlignment.STRETCH
        )
        self._fill_strata()
        self._fill_findings()
        search = ft.TextField(
            hint_text=t("ui.result.search_hint"),
            border=ft.InputBorder.UNDERLINE,
            border_color=m.GRAY_LIGHT,
            text_size=14,
            dense=True,
            on_change=self._on_search,
        )
        body = ft.Row(
            [
                self._strata_column,
                ft.Column(
                    [search, self._finding_list, self._suppressed_toggle()],
                    spacing=6,
                    expand=True,
                    horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                ),
            ],
            spacing=28,
            expand=True,
            vertical_alignment=ft.CrossAxisAlignment.STRETCH,
        )
        return ft.Column([header, ft.Container(height=10), body], spacing=8, expand=True)

    def _ai_summary(self, payload: dict[str, Any]) -> list[ft.Control]:
        summary = payload.get("ai_summary")
        if not summary:
            return []
        return [
            ft.Container(
                content=ft.Column(
                    [
                        text(
                            t("ui.result.ai_summary", model=summary["model"]),
                            12,
                            m.BRONZE,
                            weight=ft.FontWeight.W_600,
                        ),
                        text(summary["text"], 14, m.NIGHT, selectable=True),
                    ],
                    spacing=3,
                ),
                border=ft.Border.only(left=ft.BorderSide(3, m.GOLD)),
                padding=ft.Padding.only(left=12, top=2, bottom=2),
            )
        ]

    def _suppressed_toggle(self) -> ft.Control:
        assert self.payload is not None  # noqa: S101
        count = m.suppressed_count(self.payload["findings"])
        if not count:
            return ft.Container()
        label = t(
            "ui.result.hide_suppressed" if self.show_suppressed else "ui.result.show_suppressed",
            count=count,
        )

        def toggle(_: Any) -> None:
            self.show_suppressed = not self.show_suppressed
            self.refresh()

        return ft.Row([button(label, toggle)])

    def _fill_strata(self) -> None:
        """The strata column: one band per severity, as tall as how many there are.

        Number and name go on one line: that way they fit even if the band is short.
        """
        assert self.payload is not None  # noqa: S101
        bands: list[ft.Control] = []
        for stratum in m.strata(self.payload["summary"]):
            dimmed = self.severity is not None and self.severity != stratum.severity
            bands.append(
                ft.Container(
                    content=ft.Row(
                        [
                            text(
                                str(stratum.count),
                                26,
                                stratum.foreground,
                                weight=ft.FontWeight.BOLD,
                            ),
                            text(
                                m.severity_name(stratum.severity, stratum.count),
                                14,
                                stratum.foreground,
                            ),
                        ],
                        spacing=10,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    bgcolor=stratum.background,
                    padding=ft.Padding.symmetric(horizontal=16, vertical=4),
                    alignment=ft.Alignment.CENTER_LEFT,
                    expand=stratum.flex,
                    opacity=0.35 if dimmed else 1,
                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                    on_click=lambda _, s=stratum.severity: self._toggle_severity(s),
                    tooltip=t("ui.result.stratum_tip"),
                )
            )
        if not bands:
            bands = [
                ft.Container(
                    content=text(t("ui.result.no_open"), 14, m.GOOD[1]),
                    bgcolor=m.GOOD[0],
                    padding=ft.Padding.all(16),
                    expand=True,
                )
            ]
        self._strata_column.controls = bands

    def _fill_findings(self) -> None:
        assert self.payload is not None  # noqa: S101
        findings = m.visible_findings(
            self.payload["findings"],
            self.severity,
            self.search,
            include_suppressed=self.show_suppressed,
        )
        rows: list[ft.Control] = [self._finding_row(f) for f in findings[:400]]
        if not rows:
            rows = [text(t("ui.result.nothing_matches"), 15, m.GRAY_MID)]
        self._finding_list.controls = rows

    def _finding_row(self, finding: dict[str, Any]) -> ft.Control:
        is_open = finding["baseline_status"] in m.OPEN_STATUSES
        background, _ = m.STRATUM_COLORS[finding["severity"]]
        state = code_label(finding["baseline_status"], "status", variant="lower")
        if finding["origin"] == Origin.AI:
            state = t("ui.finding.ai_suggestion", state=state)
        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(width=6, height=38, bgcolor=background),
                    ft.Column(
                        [
                            text(
                                text_of(finding, "title"),
                                15,
                                m.NIGHT if is_open else m.GRAY_MID,
                                weight=ft.FontWeight.W_600,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                            text(
                                m.location(finding),
                                12,
                                m.GRAY_MID,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                        ],
                        spacing=1,
                        expand=True,
                    ),
                    text(
                        state,
                        12,
                        m.NIGHT if finding["baseline_status"] == BaselineStatus.NEW else m.GRAY_MID,
                    ),
                ],
                spacing=12,
            ),
            padding=ft.Padding.symmetric(vertical=9),
            border=ft.Border.only(bottom=ft.BorderSide(1, m.LINE)),
            on_click=lambda _: self.show_finding(finding),
            ink=True,
        )

    def _toggle_severity(self, severity: str) -> None:
        self.severity = None if self.severity == severity else severity
        self._fill_strata()
        self._fill_findings()
        self.page.update()

    def _on_search(self, event: Any) -> None:
        self.search = event.control.value or ""
        self._fill_findings()
        self.page.update()

    # ------------------------------------------------------------ dialogs

    def _dialog(self, title: str, body: list[ft.Control], actions: list[ft.Control]) -> None:
        self.page.show_dialog(
            ft.AlertDialog(
                title=text(title, 20, m.NIGHT, weight=ft.FontWeight.BOLD),
                content=ft.Container(
                    content=ft.Column(
                        body,
                        spacing=12,
                        # With little content, no scrolling: otherwise the dialog
                        # takes the full height even with only two lines.
                        scroll=ft.ScrollMode.AUTO if len(body) > 6 else None,
                        tight=True,
                        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                    ),
                    width=720,
                ),
                actions=actions,
                bgcolor=m.WHITE,
                shape=ft.RoundedRectangleBorder(radius=4),
            )
        )

    def _panel(
        self,
        title: str,
        body: list[ft.Control],
        actions: list[ft.Control],
        section: str = "settings",
    ) -> None:
        """Shows a section in the central part, with an X to close it.

        `section` says which navigation bar item gets highlighted. The X and pressing
        that item again do the same thing: close it and reveal what was underneath.
        """
        self._section, self._panel_title = section, title
        self._panel_view = ft.Column(
            [
                ft.Row(
                    [
                        text(title, 28, m.NIGHT, weight=ft.FontWeight.BOLD, expand=True),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE,
                            icon_color=m.NIGHT,
                            tooltip=t("ui.common.close"),
                            on_click=self._close,
                        ),
                    ]
                ),
                ft.Divider(height=1, color=m.LINE),
                ft.Column(
                    body,
                    spacing=14,
                    expand=True,
                    scroll=ft.ScrollMode.AUTO,
                    horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                ),
                ft.Divider(height=1, color=m.LINE),
                ft.Row(actions, alignment=ft.MainAxisAlignment.END, spacing=8),
            ],
            spacing=12,
            expand=True,
        )
        self.refresh()

    def _close(self, _: Any = None) -> None:
        """Closes the central section if one is open; otherwise, the dialog."""
        if self._panel_view is not None:
            self._panel_view = None
            self._bases_slot = None
            self._cli_slot = None
            self.refresh()
        else:
            self.page.pop_dialog()

    def show_finding(self, finding: dict[str, Any]) -> None:
        def part(label: str, value: str) -> list[ft.Control]:
            if not value:
                return []
            return [
                ft.Column(
                    [
                        text(label, 13, m.GRAY_MID, weight=ft.FontWeight.W_600),
                        text(value, 15, selectable=True),
                    ],
                    spacing=2,
                )
            ]

        body: list[ft.Control] = [
            text(f"{m.location(finding)}  ·  {finding['id']}", 13, m.GRAY_MID, selectable=True)
        ]
        if finding["snippet"]:
            body.append(
                ft.Container(
                    content=ft.Text(
                        finding["snippet"],
                        font_family=MONO,
                        size=13,
                        color=m.NIGHT,
                        selectable=True,
                    ),
                    bgcolor=m.PAPER,
                    padding=ft.Padding.all(14),
                )
            )
        body += part(t("ui.finding.what"), text_of(finding, "description"))
        body += part(t("ui.finding.how_fix"), text_of(finding, "recommendation"))
        classification = " · ".join(
            v
            for v in (
                code_label(finding["severity"], "severity", variant="capitalized"),
                finding["cwe"],
                finding["owasp"],
            )
            if v
        )
        body += part(t("ui.finding.classification"), classification)
        body.append(self._expert_block(finding))
        assessment = finding.get("llm_assessment")
        if assessment:
            body.append(
                ft.Container(
                    content=ft.Column(
                        [
                            text(ai_label(), 13, m.NIGHT, weight=ft.FontWeight.W_600),
                            *(text(line, 14, selectable=True) for line in m.ai_opinion(assessment)),
                            text(
                                t("ui.finding.model", model=assessment.get("model", "")),
                                12,
                                m.GRAY_MID,
                            ),
                        ],
                        spacing=4,
                    ),
                    border=ft.Border.only(left=ft.BorderSide(3, m.GOLD)),
                    padding=ft.Padding.only(left=14),
                )
            )
        actions: list[ft.Control] = [button(t("ui.common.close"), self._close, primary=True)]
        if finding["baseline_status"] in m.OPEN_STATUSES:
            actions = [
                button(
                    t("ui.finding.accept"),
                    lambda _: self.ask_justification(finding, BaselineStatus.ACCEPTED),
                ),
                button(
                    t("ui.finding.false_positive"),
                    lambda _: self.ask_justification(finding, BaselineStatus.FALSE_POSITIVE),
                ),
                *actions,
            ]
        else:
            actions = [
                button(t("ui.finding.recount"), lambda _: self.remove_suppression(finding)),
                *actions,
            ]
        self._dialog(text_of(finding, "title"), body, actions)

    def _expert_block(self, finding: dict[str, Any]) -> ft.Control:
        """Technical data for whoever verifies by hand; collapsed so it stays out of the way."""
        rows: list[ft.Control] = [
            ft.Row(
                [
                    text(label, 13, m.GRAY_MID, weight=ft.FontWeight.W_600, width=130),
                    text(value, 14, m.NIGHT, selectable=True, expand=True),
                ],
                vertical_alignment=ft.CrossAxisAlignment.START,
            )
            for label, value in m.expert_facts(finding)
        ]
        return ft.ExpansionTile(
            title=text(t("ui.expert.title"), 14, m.NIGHT, weight=ft.FontWeight.W_600),
            subtitle=text(t("ui.expert.subtitle"), 12),
            controls=[ft.Container(ft.Column(rows, spacing=6), padding=ft.Padding.all(12))],
            controls_padding=ft.Padding.all(0),
            tile_padding=ft.Padding.symmetric(horizontal=0),
            maintain_state=True,
        )

    def _reload_last_run(self) -> None:
        """Rereads the last run: a suppression updates it without scanning again."""
        if self.root is None:
            return
        try:
            with Store(self.root) as store:
                self.payload = store.payload()
        except (LookupError, ValueError):
            return
        # Accepting a risk recomputes the summary: the recent list's color follows it.
        self._load_recents()
        self.refresh()

    def remove_suppression(self, finding: dict[str, Any]) -> None:
        assert self.root is not None  # noqa: S101
        with Store(self.root) as store:
            store.unsuppress(finding["id"])
        self._close()
        self._reload_last_run()
        self.notify(t("ui.finding.recounted", id=finding["id"]))

    def ask_justification(self, finding: dict[str, Any], status: BaselineStatus) -> None:
        self._close()
        reason = ft.TextField(
            label=t("ui.finding.reason"), multiline=True, min_lines=3, autofocus=True
        )
        review = ft.TextField(label=t("ui.finding.review_date"), width=320)

        def save(_: Any) -> None:
            try:
                review_date = date.fromisoformat(review.value) if review.value else None
                assert self.root is not None  # noqa: S101
                with Store(self.root) as store:
                    store.suppress(
                        finding["id"],
                        status,
                        reason.value or "",
                        os.environ.get("USER", t("ui.finding.unknown_user")),
                        review_date,
                    )
            except (ValueError, LookupError) as exc:
                reason.error = str(exc)
                self.page.update()
                return
            self._close()
            self._reload_last_run()
            self.notify(t("ui.finding.saved", id=finding["id"]))

        title = t(
            "ui.finding.accept"
            if status is BaselineStatus.ACCEPTED
            else "ui.finding.mark_false_positive"
        )
        self._dialog(
            title,
            [text(text_of(finding, "title"), 15), reason, review],
            [
                button(t("ui.common.cancel"), self._close),
                button(t("ui.common.save"), save, primary=True),
            ],
        )

    def show_how(self, _: Any = None) -> None:
        """Which tools ran, whether the AI took part, and its summary."""
        assert self.payload is not None  # noqa: S101
        payload = self.payload
        modules = ", ".join(m.module_name(code) for code in payload["run"]["modules"])
        self._dialog(
            t("ui.how.title"),
            [
                text(
                    t(
                        "ui.how.profile",
                        profile=m.profile_name(payload["run"]["profile"]),
                        modules=modules,
                    ),
                    15,
                    m.NIGHT,
                ),
                *[text(fact, 14, selectable=True) for fact in m.run_facts(payload)],
                *self._ai_summary(payload),
            ],
            [button(t("ui.common.close"), self._close, primary=True)],
        )

    def show_plan(self, _: Any = None) -> None:
        """Where to start: findings grouped by common cause, worst first."""
        assert self.payload is not None  # noqa: S101
        rows: list[ft.Control] = [text(t("report.plan.help"), 13, m.GRAY_DARK)]
        for row in m.plan_rows(self.payload):
            colors = m.STRATUM_COLORS.get(row["severity"]) or m.STRATUM_COLORS[Severity.INFO]
            color = colors[0]
            rows.append(
                ft.Row(
                    [
                        ft.Container(width=10, height=10, border_radius=5, bgcolor=color),
                        ft.Container(text(row["line"], 14, selectable=True), expand=True),
                    ],
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                )
            )
        self._dialog(
            t("report.plan.title"),
            rows,
            [button(t("ui.common.close"), self._close, primary=True)],
        )

    def show_limitations(self, _: Any = None) -> None:
        assert self.payload is not None  # noqa: S101
        self._dialog(
            t("ui.limitations.title"),
            [text(render(item), 15, selectable=True) for item in self.payload["limitations"]],
            [button(t("ui.common.close"), self._close, primary=True)],
        )

    def show_endpoints(self, _: Any = None) -> None:
        assert self.payload is not None  # noqa: S101
        rows: list[ft.Control] = []
        for endpoint in sorted(
            self.payload["endpoints"], key=lambda e: (e["has_auth"] is not False, e["path"])
        ):
            methods = (
                t("ui.endpoints.any_method")
                if endpoint["methods"] == ["*"]
                else ", ".join(endpoint["methods"])
            )
            protected = {
                True: t("ui.endpoints.protected"),
                False: t("ui.endpoints.unprotected"),
                None: t("ui.endpoints.unknown"),
            }[endpoint["has_auth"]]
            is_open = endpoint["has_auth"] is False
            rows.append(
                ft.Container(
                    content=ft.Column(
                        [
                            text(
                                f"{methods}  {endpoint['path']}",
                                15,
                                m.NIGHT if is_open else m.GRAY_DARK,
                                weight=ft.FontWeight.W_600,
                            ),
                            text(f"{protected}: {render(endpoint['evidence'])}", 13, m.GRAY_MID),
                        ],
                        spacing=1,
                    ),
                    padding=ft.Padding.symmetric(vertical=8),
                    border=ft.Border.only(bottom=ft.BorderSide(1, m.LINE)),
                )
            )
        self._dialog(
            t("ui.endpoints.title"),
            rows,
            [button(t("ui.common.close"), self._close, primary=True)],
        )

    def show_folders(self, _: Any = None) -> None:
        """Choose, for this project, which folders are not scanned."""
        if self.plan is None or self.root is None:
            self.notify(t("ui.folders.choose_first"))
            return
        root, exclusions = self.root, self.plan.exclusions
        base = self.config.exclusions.to_exclusions()
        boxes: dict[str, ft.Checkbox] = {}
        rows: list[ft.Control] = []
        for folder in list_folders(root):
            by_default = base.excludes_dir(folder)
            boxes[folder] = ft.Checkbox(
                label=t("ui.folders.by_default", folder=folder) if by_default else folder,
                value=exclusions.excludes_dir(folder),
                label_style=ft.TextStyle(size=14, color=m.NIGHT),
            )
            rows.append(boxes[folder])
        if not rows:
            rows = [text(t("ui.folders.none"), 14)]
        suggestions = self._suggestions
        defaults = m.suggestion_defaults(suggestions, self.profile)
        suggested: dict[str, ft.Checkbox] = {}
        top: list[ft.Control] = []
        if suggestions:
            top += [
                text(t("ui.folders.suggested_title"), 15, m.NIGHT, weight=ft.FontWeight.W_600),
                text(t("ui.folders.suggested_help"), 14),
            ]
            if self.profile == "vendor" and any(
                s.source in ("tool", "gitignore") for s in suggestions
            ):
                top.append(text(t("ui.folders.vendor_note"), 14))
            for s in suggestions:
                suggested[s.pattern] = ft.Checkbox(
                    label=f"{s.pattern}   · {render(reason(s))}",
                    value=defaults[s.pattern],
                    label_style=ft.TextStyle(size=14, color=m.NIGHT),
                )
            top += list(suggested.values())

        saved_exclude = list(load_project_exclusions(root)[0])
        patterns_field = ft.TextField(
            label=t("ui.folders.patterns_label"),
            hint_text=t("ui.folders.patterns_hint"),
            value=m.pattern_text(saved_exclude),
            text_size=14,
        )

        def save(_: Any) -> None:
            unchecked = [folder for folder, box in boxes.items() if not box.value]
            exclude, include = m.kept_folder_entries(saved_exclude, unchecked), []
            for folder, box in boxes.items():
                by_default = base.excludes_dir(folder)
                if box.value and not by_default:
                    exclude.append(folder)
                elif not box.value and by_default:
                    # The pattern that omits it is saved, not the path: that way it is also
                    # scanned again in subfolders with the same name.
                    include += [d for d in base.dirs if Exclusions(dirs=(d,)).excludes_dir(folder)]
            exclude += [p for p, box in suggested.items() if box.value and p not in exclude]
            exclude = [e for e in exclude if not is_file_pattern(e)]
            exclude += [p for p in m.parse_patterns(patterns_field.value or "") if p not in exclude]
            save_project_exclusions(root, exclude, include)
            self._close()
            self._replan()
            assert self.plan is not None  # noqa: S101
            self.notify(t("ui.folders.will_analyze", count=len(self.plan.tree.analyzable)))

        self._dialog(
            t("ui.folders.title"),
            [
                *top,
                text(t("ui.folders.help"), 14),
                *rows,
                patterns_field,
                text(t("ui.folders.patterns_help"), 13, m.GRAY_DARK),
            ],
            [
                button(t("ui.common.cancel"), self._close),
                button(t("ui.common.save"), save, primary=True),
            ],
        )

    def show_preview(self, _: Any = None) -> None:
        if self.plan is None:
            self.notify(t("ui.folders.choose_first"))
            return
        plan = self.plan
        files = plan.tree.analyzable
        listing = "\n".join(files[:300]) + ("\n…" if len(files) > 300 else "")
        self._dialog(
            t("ui.preview.title", count=len(files)),
            [
                text(t("ui.preview.modules", modules=", ".join(sorted(plan.modules))), 14),
                text(
                    t("ui.preview.excluded", folders=", ".join(plan.exclusions.dirs)),
                    13,
                    m.GRAY_MID,
                ),
                ft.Container(
                    content=ft.Text(
                        listing, font_family=MONO, size=12, color=m.GRAY_DARK, selectable=True
                    ),
                    bgcolor=m.PAPER,
                    padding=ft.Padding.all(14),
                ),
            ],
            [button(t("ui.common.close"), self._close, primary=True)],
        )

    def show_settings(self, _: Any = None) -> None:
        tools: list[ft.Control] = [text(line, 14) for line in self._tool_lines()] or [
            text(t("ui.settings.checking_versions"), 14, m.GRAY_MID)
        ]

        config = self.config
        llm = config.llm
        status = text("", 13, m.SEVERITY_COLORS[Severity.CRITICAL][0])
        default_profile = ft.Dropdown(
            label=t("ui.settings.default_profile"),
            value=config.general.default_profile,
            options=[ft.DropdownOption(key=key, text=label) for key, label, _ in m.profiles()[:4]],
            width=260,
            dense=True,
        )
        language = ft.Dropdown(
            label=t("ui.settings.language"),
            value=get_language(),
            options=[
                # Each language under its own name: recognizable in any interface language.
                ft.DropdownOption(key=code, text=t(f"lang.name.{code}", lang=code))
                for code in ("es", "en")
            ],
            width=260,
            dense=True,
        )
        extra = ft.TextField(
            label=t("ui.settings.extra_folders"),
            value=", ".join(config.exclusions.exclude_extra),
            dense=True,
        )
        rule_dirs = ft.TextField(
            label=t("ui.settings.user_rules_dirs"),
            value=", ".join(config.rules.extra_dirs),
            dense=True,
        )
        rules_result = text("", 13, m.GRAY_DARK)
        enabled = ft.Checkbox(label=t("ui.settings.use_ai"), value=llm.enabled)
        editor = _AiEditor(self, llm)

        def typed_rule_dirs() -> tuple[str, ...]:
            return tuple(f.strip() for f in (rule_dirs.value or "").split(",") if f.strip())

        def check_rules(_: Any) -> None:
            dirs = typed_rule_dirs()
            rules_result.value = t("ui.settings.user_rules_checking")
            self.page.update()

            def work() -> None:
                user = check_user_rules(dirs, analyzed_root=self.root, own_ids=own_rule_ids())
                failures: dict[Path, str] | None = None
                note = ""
                try:
                    with tempfile.TemporaryDirectory() as workdir:
                        failures = validate_rule_files(user.files, Path(workdir))
                except AdapterError:
                    note = t("ui.settings.user_rules_no_engine")
                lines = m.user_rules_summary(user, failures)
                rules_result.value = "\n".join([*lines, *([note] if note else [])])
                self.page.update()

            self.page.run_thread(work)

        def edited() -> Config:
            folders = tuple(f.strip() for f in (extra.value or "").split(",") if f.strip())
            return replace(
                config,
                general=replace(
                    config.general, default_profile=default_profile.value or "standard"
                ),
                exclusions=replace(config.exclusions, exclude_extra=folders),
                rules=replace(config.rules, extra_dirs=typed_rule_dirs()),
                llm=editor.result(enabled=bool(enabled.value)),
            )

        def save(_: Any) -> None:
            new_language = language.value or get_language()
            changed = new_language != get_language()
            if changed and self.running:
                status.value = t("ui.settings.language_busy")
                self.page.update()
                return
            try:
                self.config = edited()
                # Changing the language also saves the configuration.
                if changed:
                    self.config = m.change_language(self.config, new_language)
                    path = self.config.path or config_path()
                else:
                    path = save_config(self.config)
            except (ValueError, OSError) as exc:
                status.value = t("ui.settings.not_saved", error=exc)
                self.page.update()
                return
            if changed:
                # A language change rebuilds the whole layout, only once.
                self._panel_view = None
                self._bases_slot = None
                self._cli_slot = None
                self._build_layout()
                self._replan()
                self.refresh()
            else:
                self._close()
                self._replan()
            self.notify(t("ui.settings.saved", path=path))

        bases_row = ft.Row(
            [self._bases_action(on_dark=False), text(self._bases_note(), 13, m.GRAY_DARK)],
            wrap=True,
            spacing=14,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        self._bases_slot = bases_row
        cli_slot = ft.Column([], spacing=8, horizontal_alignment=ft.CrossAxisAlignment.START)
        self._cli_slot = cli_slot
        self._fill_cli()
        if not self._python_checked:
            self.page.run_thread(self._find_python_for_settings)
        excluded = ", ".join(config.exclusions.paths)
        self._panel(
            t("ui.settings.title"),
            [
                text(t("ui.settings.analysis"), 16, m.NIGHT, weight=ft.FontWeight.W_600),
                language,
                default_profile,
                text(t("ui.settings.never_analyzed", folders=excluded), 13, m.GRAY_DARK),
                extra,
                text(t("ui.settings.user_rules"), 14, m.NIGHT, weight=ft.FontWeight.W_600),
                text(t("ui.settings.user_rules_help"), 13, m.GRAY_DARK),
                rule_dirs,
                button(t("ui.settings.user_rules_check"), check_rules),
                rules_result,
                ft.Divider(height=1, color=m.LINE),
                text(t("ui.settings.ai_section"), 16, m.NIGHT, weight=ft.FontWeight.W_600),
                enabled,
                text(t("ui.settings.ai_help"), 13, m.GRAY_DARK),
                *editor.controls(),
                status,
                ft.Divider(height=1, color=m.LINE),
                text(t("ui.settings.tools"), 16, m.NIGHT, weight=ft.FontWeight.W_600),
                *tools,
                bases_row,
                ft.Divider(height=1, color=m.LINE),
                text(t("ui.cli.title"), 16, m.NIGHT, weight=ft.FontWeight.W_600),
                cli_slot,
            ],
            [
                button(t("ui.settings.thresholds"), self.show_thresholds),
                button(t("ui.common.cancel"), self._close),
                button(t("ui.common.save"), save, primary=True),
            ],
        )

    # ------------------------------------------------ the `hdl` command (Settings, first offer)

    def _lookup_python(self) -> cli_setup.PythonInfo | None:
        """Looks for a usable Python once (it starts a few programs, so not on the UI thread)."""
        if not self._python_checked:
            self._python = cli_setup.find_python()
            self._python_checked = True
        return self._python

    def _find_python_for_settings(self) -> None:
        self._lookup_python()
        if self._cli_slot is not None:
            self._fill_cli()
            self.page.update()

    def _fill_cli(self) -> None:
        """Fills the "Command line" column of Settings; the rest of the panel stays as is."""
        slot = self._cli_slot
        if slot is None:
            return
        if self._cli_busy:
            slot.controls = [
                ft.Row(
                    [
                        ft.ProgressRing(width=18, height=18, stroke_width=2, color=m.BRONZE),
                        text(m.cli_running_text(self._cli_busy), 14, m.GRAY_DARK),
                    ],
                    spacing=10,
                )
            ]
            return
        if not self._python_checked:
            slot.controls = [text(t("ui.cli.checking"), 14, m.GRAY_MID)]
            return
        section = m.cli_section(cli_setup.cli_status(), self._python, cli_setup.bundled_cli_files())
        controls: list[ft.Control] = [
            text(line, 13 if i else 14, m.GRAY_DARK if i else m.NIGHT)
            for i, line in enumerate(section.lines)
        ]
        if section.action != "none":
            controls.append(button(section.button, self._cli_action(section.action)))
        slot.controls = controls

    def _cli_action(self, action: str) -> Any:
        if action == "download_python":
            return lambda _: self.page.run_task(self.open_python_site)
        return lambda _: self.run_cli(action)

    async def open_python_site(self) -> None:
        await self.launcher.launch_url(cli_setup.DOWNLOADS_URL)

    def run_cli(self, action: str, bin_dir: Path | None = None) -> None:
        """Runs the installer (or its uninstall) in the background and reports the outcome."""
        files = cli_setup.bundled_cli_files()
        if self._cli_busy or self.running or files is None:
            return
        python = self._lookup_python()
        executable = python.path if python else None
        if executable is None and action == "uninstall":
            fallback = cli_setup.venv_python(data_dir())
            executable = str(fallback) if fallback.is_file() else None
        if executable is None:
            return
        if action == "uninstall":
            command = cli_setup.uninstall_command(executable, files, bin_dir=bin_dir)
        else:
            command = cli_setup.install_command(executable, files, bin_dir=bin_dir)
        self._cli_busy = action
        self._fill_cli()
        self.page.update()

        def work() -> None:
            try:
                result = cli_setup.run_installer(command, get_language())
            finally:
                self._cli_busy = ""
            status = cli_setup.cli_status(bin_dir=bin_dir)
            title, lines, _ok = m.cli_result(action, result, status)
            self._fill_cli()
            self._dialog(
                title,
                [text(line, 14, selectable=True) for line in lines],
                [button(t("ui.common.close"), self._close, primary=True)],
            )
            self.page.update()

        self.page.run_thread(work)

    def _maybe_offer_cli(self) -> None:
        """Once, the first time the app opens: offers the command if it is not installed."""
        marker = cli_setup.offer_marker()
        installed = cli_setup.cli_status().installed
        if not cli_setup.offer_due(marker, installed):
            return

        def work() -> None:
            python = self._lookup_python()
            title, body, action, label = m.cli_offer(python)
            # Remembered now: closing the dialog any way (button or click outside) counts.
            with contextlib.suppress(OSError):  # failing only means it may be offered again
                cli_setup.mark_offered(marker)

            def later(_: Any) -> None:
                self.page.pop_dialog()

            def accept(_: Any) -> None:
                self.page.pop_dialog()
                if action == "download_python":
                    self.page.run_task(self.open_python_site)
                else:
                    self.run_cli("install")

            self._dialog(
                title,
                [text(line, 14) for line in body],
                [
                    button(t("ui.cli.offer.later"), later),
                    button(label, accept, primary=True),
                ],
            )

        self.page.run_thread(work)

    def show_thresholds(self, _: Any = None) -> None:
        """Verdict thresholds: changing them asks for a PIN and is logged."""
        store = ThresholdStore()
        current = asdict(store.load())
        names = (
            "max_critical",
            "max_secrets",
            "max_unauth_write_endpoints",
            "max_high",
            "max_patchable_critical_deps",
        )
        fields = {
            name: ft.TextField(
                label=t("ui.thresholds.maximum", label=t(f"ui.thresholds.{name}")),
                value=str(current[name]),
                dense=True,
                width=340,
            )
            for name in names
        }
        count_ai = ft.Checkbox(
            label=t("ui.thresholds.count_ai"), value=current["count_ai_findings"]
        )
        has_pin = store.has_pin()
        pin = ft.TextField(
            label=t("ui.thresholds.pin" if has_pin else "ui.thresholds.pin_new"),
            password=True,
            dense=True,
            width=340,
        )
        repeat = ft.TextField(
            label=t("ui.thresholds.pin_repeat"),
            password=True,
            dense=True,
            width=340,
            visible=not has_pin,
        )
        status = text(
            " ".join(render(notice) for notice in store.notices),
            13,
            m.SEVERITY_COLORS[Severity.CRITICAL][0],
        )

        def save(_: Any) -> None:
            author = getpass.getuser()
            try:
                values = {name: int(box.value or "") for name, box in fields.items()}
                updated = Thresholds.from_dict(
                    {**values, "count_ai_findings": bool(count_ai.value)}
                )
                if not store.has_pin():
                    if pin.value != repeat.value:
                        raise PinError(t("ui.thresholds.pin_mismatch"))
                    store.set_pin(pin.value or "", author)
                store.save(updated, pin.value or "", author)
            except ValueError as exc:  # incluye PinError
                status.value = (
                    str(exc) if isinstance(exc, PinError) else t("ui.thresholds.invalid", error=exc)
                )
                self.page.update()
                return
            self._close()
            self.notify(t("ui.thresholds.saved"))

        changes = len(store.history())
        self._panel(
            t("ui.thresholds.title"),
            [
                text(t("ui.thresholds.help"), 14),
                ft.Row(list(fields.values()), wrap=True, spacing=12, run_spacing=10),
                count_ai,
                ft.Row([pin, repeat], wrap=True, spacing=12, run_spacing=10),
                status,
                text(t("ui.thresholds.changes", count=changes), 12, m.GRAY_MID),
            ],
            [
                button(t("ui.common.cancel"), self._close),
                button(t("ui.common.save"), save, primary=True),
            ],
        )

    def show_coverage(self, _: Any = None) -> None:
        """What Heimdall Guardian reviews of the OWASP Top 10, with open ones if any."""
        view = m.owasp_overview(self.payload)

        def chip(label: str, background: str, ink: str) -> ft.Control:
            return ft.Container(
                content=text(label, 12, ink, weight=ft.FontWeight.W_600),
                bgcolor=background,
                padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                border_radius=10,
            )

        def card(row: dict[str, Any]) -> ft.Control:
            chips: list[ft.Control] = [chip(row["coverage"], row["background"], row["ink"])]
            if row["count"] is not None:
                label = (
                    t("ui.coverage.none_open")
                    if not row["count"]
                    else tn("ui.coverage.open", row["count"])
                )
                chips.append(chip(label, m.PAPER, m.NIGHT if row["count"] else m.GRAY_MID))
            return ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Column(
                                    [
                                        text(row["title"], 16, m.NIGHT, weight=ft.FontWeight.BOLD),
                                        *(
                                            [text(row["subtitle"], 12, m.GRAY_MID)]
                                            if row["subtitle"]
                                            else []
                                        ),
                                    ],
                                    spacing=0,
                                    expand=True,
                                ),
                                ft.Row(chips, spacing=6, tight=True),
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.START,
                        ),
                        text(row["explanation"], 14, selectable=True),
                        text(
                            t("ui.coverage.example", example=row["example"]),
                            13,
                            m.GRAY_DARK,
                            selectable=True,
                        ),
                        text(row["coverage_note"], 13, m.NIGHT, selectable=True),
                    ],
                    spacing=6,
                ),
                padding=ft.Padding.all(14),
                border=ft.Border.all(1, m.LINE),
                border_radius=4,
            )

        self._panel(
            t("ui.coverage.title"),
            [
                text(t("ui.coverage.what_is"), 16, m.NIGHT, weight=ft.FontWeight.W_600),
                text(view["intro"], 14, selectable=True),
                text(view["edition"], 14, selectable=True),
                *[card(row) for row in view["rows"]],
                ft.Container(
                    content=text(view["warning"], 14, m.NIGHT, selectable=True),
                    border=ft.Border.only(left=ft.BorderSide(3, m.GOLD)),
                    padding=ft.Padding.only(left=14),
                ),
            ],
            [button(t("ui.common.close"), self._close, primary=True)],
            section="coverage",
        )

    def show_tour(self, _: Any = None) -> None:
        """First-run tour: three steps in a modal dialog, redrawn in place."""
        state = {"step": 0}
        last = len(m.TOUR_STEPS) - 1
        body = ft.Container(width=560)
        dialog = ft.AlertDialog(
            modal=True,
            content=body,
            bgcolor=m.WHITE,
            shape=ft.RoundedRectangleBorder(radius=4),
            content_padding=ft.Padding.all(28),
        )

        def finish(_: Any = None) -> None:
            try:
                self.config = m.mark_tour_seen(self.config)
            except OSError as exc:
                self.notify(str(exc))
            self.page.pop_dialog()
            self._maybe_offer_cli()

        def go(delta: int) -> None:
            state["step"] = max(0, min(last, state["step"] + delta))
            draw()
            self.page.update()

        def draw() -> None:
            step = m.tour_step(state["step"])
            column = ft.Column(
                [
                    ft.Container(
                        content=ft.Icon(getattr(ft.Icons, step["icon"]), size=56, color=m.GOLD),
                        bgcolor=m.NIGHT,
                        width=112,
                        height=112,
                        border_radius=56,
                        alignment=ft.Alignment.CENTER,
                    ),
                    text(step["indicator"], 13, m.BRONZE, weight=ft.FontWeight.W_600),
                    text(step["title"], 24, m.NIGHT, weight=ft.FontWeight.BOLD),
                    text(step["body"], 16, m.GRAY_DARK),
                ],
                spacing=14,
                tight=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
            body.content = column
            first = state["step"] == 0
            final = state["step"] == last
            footer = ft.Row(
                [
                    button(t("ui.tour.skip"), finish),
                    ft.Container(expand=True),
                    *([] if first else [button(t("ui.tour.back"), lambda _: go(-1))]),
                    button(
                        t("ui.tour.start") if final else t("ui.tour.next"),
                        finish if final else (lambda _: go(1)),
                        primary=True,
                    ),
                ],
                alignment=ft.MainAxisAlignment.END,
            )
            column.controls.append(
                ft.Container(content=footer, width=504, margin=ft.Margin.only(top=12))
            )

        draw()
        self.page.show_dialog(dialog)

    def _replay_tour(self, _: Any = None) -> None:
        self._close()
        self.show_tour()

    def _check_own_update(self, _: Any = None) -> None:
        """On demand only: asks GitHub for the latest release and fills the About slot."""
        slot = self._update_slot
        if slot is None or self._update_busy:
            return
        self._update_busy = True
        slot.controls = [text(t("ui.about.update_checking"), 14, m.GRAY_DARK)]
        self.page.update()

        def work() -> None:
            try:
                line, link = m.about_update(updates.check_self())
            finally:
                self._update_busy = False
            controls: list[ft.Control] = [text(line, 14)]
            if link:
                controls.append(
                    ft.TextButton(
                        content=t("ui.about.update_open"),
                        icon=ft.Icons.OPEN_IN_NEW,
                        on_click=lambda _: self.page.run_task(self.launcher.launch_url, link),
                        style=ft.ButtonStyle(color=m.BRONZE),
                    )
                )
            slot.controls = controls
            self.page.update()

        self.page.run_thread(work)

    def show_about(self, _: Any = None) -> None:
        self._update_slot = ft.Column(
            [
                ft.TextButton(
                    content=t("ui.about.update_check"),
                    icon=ft.Icons.SYSTEM_UPDATE_ALT,
                    on_click=self._check_own_update,
                    style=ft.ButtonStyle(color=m.BRONZE),
                )
            ],
            spacing=4,
        )
        self._panel(
            f"Heimdall Guardian {__version__}",
            [
                ft.Container(
                    content=image("sello_letras.png", height=190),
                    bgcolor="#000000",
                    alignment=ft.Alignment.CENTER,
                    padding=ft.Padding.all(14),
                    border_radius=6,
                ),
                text(f"{m.tagline()}. {m.motto()}.", 18, m.NIGHT, weight=ft.FontWeight.W_600),
                text(t("ui.about.author", author=m.AUTHOR), 15),
                text(m.PROJECT_URL, 14, m.BRONZE, selectable=True),
                self._update_slot,
                text(t("ui.about.description"), 15),
                text(t("ui.about.guarantees"), 14),
                ft.TextButton(
                    content=t("ui.tour.replay"),
                    icon=ft.Icons.PLAY_CIRCLE_OUTLINE,
                    on_click=self._replay_tour,
                    style=ft.ButtonStyle(color=m.BRONZE),
                ),
                ft.Divider(height=1, color=m.LINE),
                text(t("ui.about.third_party"), 16, m.NIGHT, weight=ft.FontWeight.W_600),
                *[
                    text(t("ui.about.license_line", name=name, license=license_), 14)
                    for name, license_ in LICENSES
                ],
                text(t("ui.about.third_party_note"), 13, m.GRAY_DARK),
                ft.Divider(height=1, color=m.LINE),
                text(t("ui.about.graphics"), 16, m.NIGHT, weight=ft.FontWeight.W_600),
                # The notice is the author's and is shown as is, in Spanish, in both languages.
                text(m.ART_NOTICE, 13, m.GRAY_DARK),
                *(
                    [text(t("ui.about.art_notice_original"), 12, m.GRAY_MID)]
                    if get_language() != "es"
                    else []
                ),
            ],
            [button(t("ui.common.close"), self._close, primary=True)],
            section="about",
        )

    # ----------------------------------------------------------- exportar

    async def export(self, extension: str) -> None:
        assert self.payload is not None  # noqa: S101
        assert self.root is not None  # noqa: S101
        name = f"heimdall-{self.root.name}.{extension}"
        target: str | None = None
        if not self.page.web:
            target = await self.picker.save_file(
                dialog_title=t("ui.export.dialog_title"),
                file_name=name,
                allowed_extensions=[extension],
            )
            if target is None:
                return
        path = Path(target) if target else Path.home() / "Downloads" / name
        if path.suffix.lower() != f".{extension}":
            path = path.with_suffix(f".{extension}")
        if path.resolve().is_relative_to(self.root):
            self.notify(t("ui.export.inside_folder"))
            return
        try:
            write_report(self.payload, path)
        except OSError as exc:
            self.notify(t("ui.export.failed", error=exc))
            return
        self.notify(t("ui.export.saved", path=path))


def main(page: ft.Page) -> None:
    App(page)


def run(*, web: bool = False, port: int = 0) -> None:
    """Opens the desktop window; with `web`, serves it on a local port."""
    if web:
        os.environ.setdefault("FLET_FORCE_WEB_SERVER", "true")
    ft.run(
        main,
        view=ft.AppView.WEB_BROWSER if web else ft.AppView.FLET_APP,
        host="127.0.0.1" if web else None,
        port=port,
        no_cdn=True,
        assets_dir=str(m.ASSETS),
        # Flet 1.1's automatic renderer picks WebAssembly, which some embedded browsers
        # cannot load; CanvasKit works everywhere the preview runs.
        web_renderer=ft.WebRenderer.CANVAS_KIT,
    )


class _AiEditor:
    """The AI configurations in «Settings»: add, remove, test and choose.

    Each one is a server with its models; there can be several, even the same
    server with other models. The active one and the fallback are stored by position,
    so that renaming one does not lose the choice.
    """

    def __init__(self, app: App, llm: Any) -> None:
        self.app = app
        self.llm = llm
        self.forms = [m.destination_form(d) for d in llm.destinations]
        names = [d.name for d in llm.destinations]
        self.active = names.index(llm.active_destination) if llm.active_destination in names else 0
        self.fallback: int | None = (
            names.index(llm.fallback_destination) if llm.fallback_destination in names else None
        )
        self.cards = ft.Column(spacing=14)
        self.active_choice = ft.Dropdown(label=t("ui.aiedit.use"), width=320, dense=True)
        self.fallback_choice = ft.Dropdown(label=t("ui.aiedit.fallback"), width=320, dense=True)
        self.active_choice.on_select = lambda e: setattr(self, "active", int(e.control.value))
        self.fallback_choice.on_select = lambda e: setattr(
            self, "fallback", None if e.control.value == "ninguna" else int(e.control.value)
        )
        self.cards.controls = [self._card(i, form) for i, form in enumerate(self.forms)]
        self._sync_choices()

    def controls(self) -> list[ft.Control]:
        return [
            self.cards,
            ft.Row([button(t("ui.aiedit.add"), self._add)]),
            ft.Row(
                [self.active_choice, self.fallback_choice],
                wrap=True,
                spacing=12,
                run_spacing=10,
            ),
        ]

    def result(self, *, enabled: bool) -> Any:
        return m.llm_from_forms(self.llm, self.forms, self.active, self.fallback, enabled=enabled)

    def _sync_choices(self) -> None:
        labels = [
            f["name"].strip() or t("ui.aiedit.unnamed", number=n)
            for n, f in enumerate(self.forms, 1)
        ]
        options = [ft.DropdownOption(key=str(i), text=label) for i, label in enumerate(labels)]
        self.active_choice.options = options
        self.active_choice.value = str(self.active)
        self.fallback_choice.options = [
            ft.DropdownOption(key="ninguna", text=t("ui.aiedit.none")),
            *[ft.DropdownOption(key=o.key, text=o.text) for o in options],
        ]
        self.fallback_choice.value = "ninguna" if self.fallback is None else str(self.fallback)

    def _draw(self) -> None:
        self.cards.controls = [self._card(i, form) for i, form in enumerate(self.forms)]
        self._sync_choices()
        self.app.page.update()

    def _add(self, _: Any) -> None:
        # The new one starts from the last one's server: the usual case is changing models.
        url = self.forms[-1]["url"] if self.forms else "http://localhost:11434/v1"
        blank = dict.fromkeys(m.AI_TASK_IDS, "")
        self.forms.append({"original": "", "name": "", "url": url, "reasoning": "off", **blank})
        self._draw()

    def _remove(self, index: int, note: ft.Text) -> None:
        if len(self.forms) == 1:
            note.value = t("ui.aiedit.keep_one")
            self.app.page.update()
            return
        self.forms.pop(index)
        self.active = 0 if self.active == index else self.active - (self.active > index)
        if self.fallback == index:
            self.fallback = None
        elif self.fallback is not None and self.fallback > index:
            self.fallback -= 1
        self._draw()

    def _probe(self, form: dict[str, str], note: ft.Text) -> None:
        note.value = t("ui.aiedit.testing")
        self.app.page.update()
        try:
            single = m.llm_from_forms(self.llm, [form], 0, None, enabled=True)
            found = LlmClient(single.destinations[0], single).models()
            note.value = t(
                "ui.aiedit.connected",
                models=", ".join(found) or t("ui.aiedit.no_models"),
            )
        except (ValueError, LlmError) as exc:
            note.value = t("ui.aiedit.no_connection", error=exc)
        self.app.page.update()

    def _field(self, form: dict[str, str], key: str, label: str, **options: Any) -> ft.TextField:
        def changed(e: Any) -> None:
            form[key] = e.control.value or ""
            if key == "name":
                self._sync_choices()
                self.app.page.update()

        return ft.TextField(label=label, value=form[key], dense=True, on_change=changed, **options)

    def _card(self, index: int, form: dict[str, str]) -> ft.Control:
        note = text("", 13, m.NIGHT)
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            self._field(form, "name", t("ui.aiedit.name"), width=220),
                            self._field(form, "url", t("ui.aiedit.url"), expand=True),
                            ft.IconButton(
                                ft.Icons.DELETE_OUTLINE,
                                icon_color=m.GRAY_DARK,
                                tooltip=t("ui.aiedit.remove_tip"),
                                on_click=lambda _: self._remove(index, note),
                            ),
                        ],
                        spacing=12,
                    ),
                    ft.Row(
                        [self._field(form, task, label, width=330) for task, label in m.ai_tasks()],
                        wrap=True,
                        spacing=12,
                        run_spacing=10,
                    ),
                    ft.Checkbox(
                        label=t("ui.settings.ai_reasoning"),
                        value=form.get("reasoning") == "on",
                        on_change=lambda e: form.__setitem__(
                            "reasoning", "on" if e.control.value else "off"
                        ),
                    ),
                    ft.Row(
                        [button(t("ui.aiedit.test"), lambda _: self._probe(form, note)), note],
                        wrap=True,
                        spacing=14,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ],
                spacing=10,
            ),
            border=ft.Border.all(1, m.LINE),
            border_radius=8,
            padding=ft.Padding.all(14),
        )
