"""Adapters for the analysis tools."""

from __future__ import annotations

from .bandit import BanditAdapter
from .base import Adapter
from .gitleaks import GitleaksAdapter
from .opengrep import OpengrepAdapter
from .osv import OsvAdapter
from .trivy import TrivyAdapter
from .vendored import VendoredAdapter


def default_adapters() -> list[Adapter]:
    # Deferred import: the `authz` adapter depends on this package.
    from ..authz.adapter import AuthzAdapter

    return [
        GitleaksAdapter(),
        TrivyAdapter(),
        OsvAdapter(),
        VendoredAdapter(),
        OpengrepAdapter(),
        BanditAdapter(),
        AuthzAdapter(),
    ]
