#!/usr/bin/env bash
# Local verify: backend + frontend unit checks, Playwright E2E, Postman (author + admin smoke).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "==> 1/4 Backend + frontend unit checks"
"$SCRIPT_DIR/test.sh"

echo "==> 2/4 Frontend browser automation"
"$SCRIPT_DIR/test-e2e.sh"

echo "==> 3/4 Postman author workflow"
"$SCRIPT_DIR/test-postman.sh"

echo "==> 4/4 Optional admin Postman smoke"
POSTMAN_INCLUDE_ADMIN_SMOKE=1 "$SCRIPT_DIR/test-postman.sh"

echo "==> Verify checks passed."
