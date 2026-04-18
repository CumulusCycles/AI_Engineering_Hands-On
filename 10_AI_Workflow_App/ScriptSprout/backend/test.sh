#!/usr/bin/env bash
# Run linter (Ruff) and tests (pytest). Run from repo root: ./backend/test.sh  — or cd backend first.
# Optional args are passed to pytest (e.g. ./backend/test.sh -v).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

uv run ruff check app tests
uv run pytest "$@"
