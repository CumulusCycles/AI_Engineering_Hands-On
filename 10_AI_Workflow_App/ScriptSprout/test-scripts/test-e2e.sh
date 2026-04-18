#!/usr/bin/env bash
# Run frontend automated UI tests (Playwright). Cwd must be ScriptSprout/frontend for npm.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT/frontend"

PLAYWRIGHT_ARGS=()
if [[ "${1:-}" == "headed" || "${1:-}" == "--headed" ]]; then
  PLAYWRIGHT_ARGS+=(--headed)
  shift
fi

if [[ $# -gt 0 ]]; then
  PLAYWRIGHT_ARGS+=("$@")
fi

if [[ ${#PLAYWRIGHT_ARGS[@]} -gt 0 ]]; then
  npm run test:e2e -- "${PLAYWRIGHT_ARGS[@]}"
else
  npm run test:e2e
fi
