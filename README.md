# Summer 2027 Internship Radar

Live tracker for Summer 2027 internship application windows — 69 programmes across energy,
finance and consulting, weighted to Houston and NYC, filtered for sophomore eligibility.

**Live site:** https://artyomderkach-bit.github.io/internship-radar/

## The one rule

> `status` is what we last **knew**. `health` is whether we still **know** it.

A failed check may never move `status`. A timeout, a 403, a parse error or a collapsed job
listing degrade `health` only, so the page says *"we last knew: not open, 14h ago, 403 — go
look"* rather than the one lie that could cost a deadline: **"closed."**

`tests/test_state_machine.py` pins this across every status x every error class. If it goes
red, stop and fix it before anything else.

Corollary, enforced everywhere: **a false negative is worse than a false positive.** Every
ambiguous case resolves toward "go check the firm's own site."

## Commands

```bash
python -m radar seed      # rebuild data/seed.json from the curated dataset
python -m radar check     # run checks, update state, append events  (--dry-run to preview)
python -m radar compose   # build site/data/*.json from seed + state
python -m radar build     # seed + compose, no network
pytest tests/             # the invariants
scripts/dev_serve.sh      # serve site/ at http://localhost:8080
```

## Layout

| Path | What |
| --- | --- |
| `radar/` | pipeline: registry, predict, runner, state, events, compose |
| `radar/checkers/` | one module per job-board platform; `manual` is the honest no-op |
| `sources/` | **one YAML per firm** — adding a firm needs no Python |
| `data/seed.json` | 69 curated programmes; `ids.lock` freezes the id set |
| `site/` | the site, served as-is. **No build step, no npm, no bundler.** |
| `state/` | live state + append-only event log (lives on the `data` branch) |

## Branches

- `main` — code. CI never writes here.
- `data` — live state, written by CI and (optionally) the Lightsail box. Each runner owns
  exactly one shard file so the two can never conflict. Fast-forward only, never force.
- The site publishes as a Pages **artifact**, so bot commits never pollute git history.

## Adding a firm

Drop a YAML in `sources/`:

```yaml
id: vitol-commercial-trading      # must match an id in data/seed.json
check:
  method: greenhouse
  board: vitol
  match: {any_of: ["intern", "internship"], year: 2027}
  canary: "Trading Analyst"       # a posting that must ALWAYS be on this board
  runner: either                  # actions | vps | either
confidence: high
```

No file means `manual`: the row shows as a curated prediction and says so. That is the
correct default — a programme with no live checker is a prediction, not a fact.

## Operational notes

- **Cron jitter** on Actions runs 5-20 min. The header shows observed data age, never a
  promised cadence.
- **60-day inactivity** disables scheduled workflows. `keepalive.yml` needs a
  `KEEPALIVE_PAT` secret — a `GITHUB_TOKEN` commit does *not* reset that timer.
- **Pages CDN** serves `max-age=600`; `cache: 'no-store'` does not defeat it. `api.js`
  cache-busts with `?t=<epoch>`.
- Personal application state is `localStorage` only. There is no backend, so it cannot leak
  to anyone the link is shared with.
