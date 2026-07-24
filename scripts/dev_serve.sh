#!/usr/bin/env bash
# Serve the site exactly as GitHub Pages will: static files, no build step.
set -euo pipefail
cd "$(dirname "$0")/.."
python -m radar build
echo "→ http://localhost:${1:-8080}"
cd site && exec python3 -m http.server "${1:-8080}"
