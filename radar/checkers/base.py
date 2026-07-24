"""Checker protocol.

A checker's ONE job is to report what it saw. It never decides status, never writes state,
and never swallows an exception into a false negative — `runner.py` turns any raise into
`Result.failed(...)`, which by construction cannot move `status`.
"""

from __future__ import annotations

from typing import Protocol

from ..models import Result


class Checker(Protocol):
    name: str

    def check(self, prog: dict, cfg: dict) -> Result:
        """Return what was observed. Raising is allowed — the runner catches it."""
        ...


REGISTRY: dict[str, "Checker"] = {}


def register(checker: "Checker") -> "Checker":
    REGISTRY[checker.name] = checker
    return checker
