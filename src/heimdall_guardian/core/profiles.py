"""Analysis modules and predefined profiles."""

from __future__ import annotations

from enum import StrEnum

from ..i18n import t


class Module(StrEnum):
    SEC = "SEC"
    SEC_H = "SEC-H"
    DEP = "DEP"
    SAST = "SAST"
    CONF = "CONF"
    AUTHZ = "AUTHZ"
    AI = "AI"
    SBOM = "SBOM"


CUSTOM_PROFILE = "custom"

_QUICK = frozenset({Module.SEC, Module.DEP, Module.CONF})
_STANDARD = _QUICK | {Module.SAST, Module.AUTHZ}
_FULL = _STANDARD | {Module.SEC_H, Module.AI}

PROFILES: dict[str, frozenset[Module]] = {
    "quick": _QUICK,
    "standard": _STANDARD,
    "full": _FULL,
    "vendor": _FULL | {Module.SBOM},
}

# Profile codes of earlier versions (in Spanish): accepted as input, but what is stored
# is always the English code (their texts: `ui.profile.<code>.name`).
PROFILE_ALIASES = {
    "rapido": "quick",
    "estandar": "standard",
    "completo": "full",
    "proveedor": "vendor",
    "personalizado": CUSTOM_PROFILE,
}


def canonical_profile(profile: str) -> str:
    """The stored code of a profile written in English or with the old Spanish name."""
    code = profile.strip().lower()
    return PROFILE_ALIASES.get(code, code)


def profile_name(profile: str) -> str:
    """The visible name of a profile in the current language; an unknown one, as is."""
    code = canonical_profile(profile)
    return t(f"ui.profile.{code}.name") if code in (*PROFILES, CUSTOM_PROFILE) else profile


# Modules with an implementation; the rest arrive in later milestones and are
# declared as a limitation of the run instead of being silently ignored.
IMPLEMENTED = frozenset(Module)
# Modules that already run but with incomplete coverage: also declared.
PARTIAL: dict[Module, str] = {}


def resolve(profile: str, custom: frozenset[Module] | None = None) -> frozenset[Module]:
    """Modules a profile asks for; `custom` uses the ones the user ticks."""
    profile = canonical_profile(profile)
    if profile == CUSTOM_PROFILE:
        if not custom:
            raise ValueError(t("core.profiles.custom_needs_module"))
        return custom
    try:
        return PROFILES[profile]
    except KeyError:
        valid = ", ".join([*PROFILES, CUSTOM_PROFILE])
        raise ValueError(
            t("core.profiles.unknown_profile", profile=repr(profile), valid=valid)
        ) from None


def parse_modules(text: str) -> frozenset[Module]:
    """Parses a comma-separated list, e.g. `SEC,DEP,sec-h`."""
    modules = set()
    for raw in text.split(","):
        code = raw.strip().upper().replace("_", "-")
        if code == "IA":  # the Spanish name of the module
            code = Module.AI.value
        if not code:
            continue
        try:
            modules.add(Module(code))
        except ValueError:
            valid = ", ".join(m.value for m in Module)
            raise ValueError(
                t("core.profiles.unknown_module", module=repr(raw.strip()), valid=valid)
            ) from None
    return frozenset(modules)
