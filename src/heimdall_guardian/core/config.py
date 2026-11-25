"""Application configuration (`config.toml`)."""

from __future__ import annotations

import json
import tomllib
from dataclasses import asdict, dataclass, field, fields, replace
from pathlib import Path
from typing import Any

from ..i18n import t
from ..i18n.languages import SUPPORTED
from .files import DEFAULT_EXCLUDED_DIRS, Exclusions, existing_file_entry, is_file_pattern
from .paths import config_path

UNSET = "<unset>"
NO_FALLBACK = "none"


class ConfigError(ValueError):
    """The configuration file cannot be used."""


class LegacyConfigError(ConfigError):
    """The file uses the Spanish keys of an earlier version (it is not migrated)."""

    def __init__(self, path: Path) -> None:
        self.path = path
        super().__init__(t("core.config.legacy", path=path))


@dataclass(frozen=True)
class LlmDestination:
    name: str
    url: str
    runtime: str = "ollama"
    requires_token: bool = False
    context_tokens: int = 32768
    model_triage: str = UNSET
    model_endpoints: str = UNSET
    model_summary: str = UNSET
    # Sink review (T4); when unset the triage model is used.
    model_sinks: str = UNSET
    # Second model for triage: if it agrees with the first, confidence goes up.
    model_consensus: str = UNSET
    # "off" asks reasoning models to answer directly; "on" lets them think first (slower).
    reasoning: str = "off"

    def model(self, task: str) -> str | None:
        """Model configured for `triage`, `endpoints`, `sinks`, `summary` or `consensus`."""
        value = str(getattr(self, f"model_{task}")).strip()
        return None if not value or value == UNSET else value


@dataclass(frozen=True)
class LlmConfig:
    enabled: bool = True
    active_destination: str = "laptop"
    fallback_destination: str = NO_FALLBACK
    allowed_hosts: tuple[str, ...] = ()
    internal_ca: str = ""
    temperature: float = 0.1
    max_targets_per_run: int = 150
    timeout_per_target_s: int = 120
    destinations: tuple[LlmDestination, ...] = (
        LlmDestination(name="laptop", url="http://localhost:11434/v1"),
    )

    def destination(self, name: str) -> LlmDestination | None:
        return next((d for d in self.destinations if d.name == name), None)

    def using(self, name: str) -> LlmConfig:
        """The same configuration, with `name` as the active destination (for a single run)."""
        if self.destination(name) is None:
            known = ", ".join(d.name for d in self.destinations)
            raise LookupError(t("core.config.no_ai_config", name=repr(name), known=known))
        return replace(self, active_destination=name)

    def candidates(self) -> list[LlmDestination]:
        """Active destination and, if there is one, the fallback, in that order."""
        names = [self.active_destination]
        if self.fallback_destination not in (NO_FALLBACK, "", self.active_destination):
            names.append(self.fallback_destination)
        return [d for name in names if (d := self.destination(name)) is not None]


@dataclass(frozen=True)
class GeneralConfig:
    default_profile: str = "standard"
    language: str = ""
    # Set once the first-run tour was finished or skipped.
    onboarding_seen: bool = False


@dataclass(frozen=True)
class ExclusionsConfig:
    paths: tuple[str, ...] = DEFAULT_EXCLUDED_DIRS
    # Added to `paths` (or subtracted from it) without repeating the base list.
    exclude_extra: tuple[str, ...] = ()
    include_extra: tuple[str, ...] = ()
    max_file_size_kb: int = 1024

    def to_exclusions(
        self,
        exclude: tuple[str, ...] = (),
        include: tuple[str, ...] = (),
        root: Path | None = None,
    ) -> Exclusions:
        """Folders that are not analyzed, plus any that a project asks for.

        The default ones always apply, even if `paths` comes from a file saved
        by an earlier version; to analyze one of them use `include_extra`
        (or `include`). With `root`, an entry that names an existing file there (no
        wildcard) excludes exactly that file, never a manifest or lockfile.
        """
        wanted = (*DEFAULT_EXCLUDED_DIRS, *self.paths, *self.exclude_extra, *exclude)
        kept = {*self.include_extra, *include}
        exact: dict[str, None] = {}
        dirs: list[str] = []
        for entry in wanted:
            if entry.strip() in kept or entry.strip("/") in kept:
                continue
            named = existing_file_entry(root, entry) if root is not None else None
            if named is not None:
                exact[named] = None
            elif entry.strip("/") and not is_file_pattern(entry):
                dirs.append(entry.strip("/"))
        files = [d.strip() for d in wanted if is_file_pattern(d) and d.strip() not in kept]
        return Exclusions(
            dirs=tuple(dict.fromkeys(dirs)),
            max_file_kb=self.max_file_size_kb,
            files=tuple(dict.fromkeys(files)),
            paths=tuple(exact),
        )


@dataclass(frozen=True)
class DatabasesConfig:
    alert_age_days: int = 7


@dataclass(frozen=True)
class RulesConfig:
    # Extra folders with the user's own Opengrep rules; `~` is expanded when they are used.
    extra_dirs: tuple[str, ...] = ()


@dataclass(frozen=True)
class Config:
    general: GeneralConfig = field(default_factory=GeneralConfig)
    exclusions: ExclusionsConfig = field(default_factory=ExclusionsConfig)
    llm: LlmConfig = field(default_factory=LlmConfig)
    databases: DatabasesConfig = field(default_factory=DatabasesConfig)
    rules: RulesConfig = field(default_factory=RulesConfig)
    path: Path | None = None


def _build(cls: type, data: dict[str, Any], where: str) -> Any:
    known = {f.name for f in fields(cls)}
    unknown = sorted(set(data) - known)
    if unknown:
        raise ConfigError(t("core.config.unknown_option", where=where, names=", ".join(unknown)))
    try:
        return cls(**data)
    except TypeError as exc:
        raise ConfigError(t("core.config.incomplete", where=where, error=exc)) from exc


# Keys of the configuration of earlier versions (in Spanish): they are not migrated.
_V1_SECTIONS = frozenset({"exclusiones", "bases"})
_V1_KEYS = frozenset(
    {
        "perfil_por_defecto",
        "destinos",
        "destino_activo",
        "destino_respaldo",
        "ca_interna",
        "temperatura",
        "habilitado",
        "max_objetivos_por_corrida",
        "timeout_seg_por_objetivo",
    }
)


def _is_v1(raw: dict[str, Any]) -> bool:
    """The file uses the Spanish keys of versions 0.11 and earlier."""
    if _V1_SECTIONS & set(raw):
        return True
    return any(_V1_KEYS & set(section) for section in raw.values() if isinstance(section, dict))


def load_config(path: Path | None = None) -> Config:
    """Reads `config.toml`; if it does not exist, returns the defaults."""
    path = path or config_path()
    if not path.is_file():
        return Config()
    try:
        raw = tomllib.loads(path.read_text(encoding="utf-8"))
    except (tomllib.TOMLDecodeError, OSError) as exc:
        raise ConfigError(t("core.config.unreadable", path=path, error=exc)) from exc

    if _is_v1(raw):
        raise LegacyConfigError(path)
    unknown = sorted(set(raw) - {"general", "exclusions", "llm", "databases", "rules"})
    if unknown:
        raise ConfigError(
            t("core.config.unknown_section", file=path.name, names=", ".join(unknown))
        )
    exclusions_raw = {
        key: tuple(value) if isinstance(value, list) else value
        for key, value in raw.get("exclusions", {}).items()
    }
    llm_raw = dict(raw.get("llm", {}))
    destinations = tuple(
        _build(LlmDestination, dict(item), "[[llm.destinations]]")
        for item in llm_raw.pop("destinations", [])
    )
    if "allowed_hosts" in llm_raw:
        llm_raw["allowed_hosts"] = tuple(str(h).lower() for h in llm_raw["allowed_hosts"])
    for destination in destinations:
        if destination.reasoning not in ("off", "on"):
            raise ConfigError(
                t(
                    "core.config.bad_reasoning",
                    name=destination.name,
                    value=repr(destination.reasoning),
                )
            )
    if destinations:
        llm_raw["destinations"] = destinations
    rules_raw = {
        key: tuple(str(v) for v in value) if isinstance(value, list) else value
        for key, value in raw.get("rules", {}).items()
    }
    general = _build(GeneralConfig, dict(raw.get("general", {})), "[general]")
    if general.language not in ("", *SUPPORTED):
        raise ConfigError(
            t(
                "core.config.bad_language",
                value=repr(general.language),
                first=SUPPORTED[0],
                second=SUPPORTED[-1],
            )
        )
    return Config(
        general=general,
        exclusions=_build(ExclusionsConfig, exclusions_raw, "[exclusions]"),
        llm=_build(LlmConfig, llm_raw, "[llm]"),
        databases=_build(DatabasesConfig, dict(raw.get("databases", {})), "[databases]"),
        rules=_build(RulesConfig, rules_raw, "[rules]"),
        path=path,
    )


def _value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, tuple | list):
        return "[" + ", ".join(_value(item) for item in value) + "]"
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def dump_config(config: Config) -> str:
    """TOML text of the configuration, to create or save it from the interface."""
    lines = ["# Heimdall Guardian: local configuration. Model names are never hard-coded:"]
    lines.append("# write them as your runtime lists them (`hdl llm`).")
    lines.append('# [general] language: "es", "en" or "" (empty: follow the system language).')
    for name in ("general", "exclusions", "databases", "rules"):
        lines += ["", f"[{name}]"]
        lines += [
            f"{key} = {_value(value)}" for key, value in asdict(getattr(config, name)).items()
        ]
    llm = asdict(config.llm)
    destinations = llm.pop("destinations")
    lines += ["", "[llm]"]
    lines += [f"{key} = {_value(value)}" for key, value in llm.items()]
    for destination in destinations:
        lines += ["", "[[llm.destinations]]"]
        lines += [f"{key} = {_value(value)}" for key, value in destination.items()]
    return "\n".join(lines) + "\n"


def _back_up_legacy(path: Path) -> None:
    """Saves a file from an earlier version as `config.toml.v1.bak` before replacing it."""
    try:
        legacy = path.is_file() and _is_v1(tomllib.loads(path.read_text(encoding="utf-8")))
        if legacy:
            path.replace(path.with_name(path.name + ".v1.bak"))
    except (tomllib.TOMLDecodeError, OSError):
        pass


def save_config(config: Config, path: Path | None = None) -> Path:
    path = path or config.path or config_path()
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    _back_up_legacy(path)
    path.write_text(dump_config(config), encoding="utf-8")
    return path


TEMPLATE = dump_config(Config())
