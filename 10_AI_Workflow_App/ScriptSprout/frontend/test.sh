#!/usr/bin/env bash
# Run frontend linter + unit tests. Run from repo root: ./frontend/test.sh  — or cd frontend first.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

npm run lint
npm run test
