# House rules

1. **No build step.** Vanilla ES modules + CSS, served as-is. No npm, no bundler, no
   framework, no vendored chart library. If something needs a build, it doesn't go in.
2. **`status` vs `health` are orthogonal.** A failed check degrades `health` and never moves
   `status`. See `radar/state.py` and `tests/test_state_machine.py`.
3. **A false negative is worse than a false positive.** Ambiguity resolves toward "go look."
4. **Never invent a date.** `predict.py` returns `precision: "unknown"` for anything it
   can't parse; the UI renders that as visibly uncertain. Do not backfill a plausible guess.
5. **Never `innerHTML` with data.** Firm names and job titles are third-party strings on a
   public page. `render/fmt.js` `el()` refuses it outright.
6. **CI never writes `main`.** State goes to the `data` branch, fast-forward only.
7. **Guards belong in `runner.py`, not in checkers.** Collapse guard and canary ship with
   the first listing checker, not as later hardening.
8. **"Nothing is open" is a conviction too — verify negatives.** On 2026-08-22 the sister
   board claimed 0 open doors while TikTok's Summer 2027 HR reqs were live and Aerotek had
   posted five weeks earlier than last cycle. Curated rows without live checkers decay
   fastest during the Aug–Nov posting season. Before asserting "0 open now" to a person —
   sharing a link, answering a question — run a refutation sweep against the firms' own
   boards; treat a curated row's `curated_verified_on` older than ~2 weeks in season as
   "we don't know", not "not open". Firms post EARLIER each cycle, never later.
