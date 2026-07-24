"""The honest no-op checker.

Rows with no automated source use this. It reports `ok=True, open=None` — meaning "the check
ran and we genuinely learned nothing new". That is deliberately different from `not_open`:
it lets the UI say "not watched; predicted window only" instead of showing a confident,
stale-looking negative that the user might trust.

It is also what makes Phase 1 safe to ship: the whole pipeline (fetch -> diff -> events ->
commit -> deploy) gets exercised on the real schedule with zero scraping risk.
"""

from __future__ import annotations

from ..models import Result
from .base import register


class ManualChecker:
    name = "manual"

    def check(self, prog: dict, cfg: dict) -> Result:
        return Result.unwatched()


register(ManualChecker())
