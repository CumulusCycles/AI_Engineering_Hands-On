#!/usr/bin/env bash
# Remove test and build *artifacts* under ScriptSprout. Intended for manual use only —
# do not call this from verify.sh, test.sh, or other automation.
#
# Keeps (typical uv sync / npm install / dev server / app data):
#   backend/.venv, frontend/node_modules, frontend/.vite, data/, .env
#
# Removes caches and outputs from linters, pytest, Playwright, production build, etc.
#
# Usage (from ScriptSprout/): ./test-scripts/test-cleanup.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "==> test-cleanup: removing test/build artifacts under $REPO_ROOT"
echo "    (preserving .venv, node_modules, frontend/.vite, data/, .env)"

BACKEND="$REPO_ROOT/backend"
if [[ -d "$BACKEND" ]]; then
  find "$BACKEND" -type d -name '__pycache__' -print0 2>/dev/null | xargs -0 rm -rf 2>/dev/null || true
  for name in .pytest_cache .ruff_cache .mypy_cache .hypothesis htmlcov coverage; do
    path="$BACKEND/$name"
    if [[ -e "$path" ]]; then
      echo "    rm -rf backend/$name"
      rm -rf "$path"
    fi
  done
  rm -f "$BACKEND/.coverage" 2>/dev/null || true
  shopt -s nullglob
  for f in "$BACKEND"/.coverage.*; do
    echo "    rm -f backend/$(basename "$f")"
    rm -f "$f"
  done
  shopt -u nullglob
fi

FRONT="$REPO_ROOT/frontend"
if [[ -d "$FRONT" ]]; then
  for name in test-results playwright-report dist coverage; do
    path="$FRONT/$name"
    if [[ -e "$path" ]]; then
      echo "    rm -rf frontend/$name"
      rm -rf "$path"
    fi
  done
  if [[ -f "$FRONT/.eslintcache" ]]; then
    echo "    rm -f frontend/.eslintcache"
    rm -f "$FRONT/.eslintcache"
  fi
  find "$FRONT" -maxdepth 1 -type f -name '*.tsbuildinfo' -print 2>/dev/null | while read -r f; do
    echo "    rm -f frontend/$(basename "$f")"
    rm -f "$f"
  done
fi

for name in test-results playwright-report tmp temp; do
  path="$REPO_ROOT/$name"
  if [[ -e "$path" ]]; then
    echo "    rm -rf $name"
    rm -rf "$path"
  fi
done

echo "==> test-cleanup done."
