"""`python -m radar <command>` — one entry point for every operation."""

import sys

USAGE = """usage: python -m radar <command>

  seed      rebuild data/seed.json from the curated dataset
  check     run all configured checks, update state, append events
  compose   build site/data/*.json from seed + state
  build     seed + compose (no network)
"""


def main() -> int:
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    sys.argv = [sys.argv[0], *sys.argv[2:]]
    if cmd == "seed":
        from .registry import main as run; run()
    elif cmd == "check":
        from .runner import main as run; run()
    elif cmd == "compose":
        from .compose import main as run; run()
    elif cmd == "build":
        from .registry import main as seed; from .compose import main as compose
        seed(); compose()
    else:
        print(USAGE)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
