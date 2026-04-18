#!/usr/bin/env bash
# Run backend + frontend linters/tests from ScriptSprout root (parent of test-scripts/).
# Optional args are passed through to backend pytest only (e.g. ./test-scripts/test.sh -v).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "==> Running backend checks: Ruff + pytest (backend/test.sh)"
"$REPO_ROOT/backend/test.sh" "$@"

echo "==> Running frontend checks: ESLint + Vitest (frontend/test.sh)"
"$REPO_ROOT/frontend/test.sh"
