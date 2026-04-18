#!/usr/bin/env bash
# Dev helper: wipe SQLite DB + Chroma vectorstore (paths relative to ScriptSprout root).
#
# It deletes:
# - $SQLITE_PATH (default: ./data/app.db)
# - $CHROMA_PATH (default: ./data/chroma)
#
# After running, restart the FastAPI server so tables are recreated and admin is reseeded.
#
# Usage (from ScriptSprout/):
#   ./reset-db-and-chroma.sh --yes
#   ./reset-db-and-chroma.sh --kill-port 8000 --yes

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$SCRIPT_DIR"
cd "$REPO_ROOT"

SQLITE_PATH_DEFAULT="./data/app.db"
CHROMA_PATH_DEFAULT="./data/chroma"

SQLITE_PATH="${SQLITE_PATH:-$SQLITE_PATH_DEFAULT}"
CHROMA_PATH="${CHROMA_PATH:-$CHROMA_PATH_DEFAULT}"

CONFIRM=false
KILL_PORT=""

if [[ -f ".env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source ".env"
  set +a
fi

while [[ $# -gt 0 ]]; do
  case "$1" in
    --yes)
      CONFIRM=true
      shift
      ;;
    --kill-port)
      KILL_PORT="${2:-}"
      if [[ -z "$KILL_PORT" ]]; then
        echo "Missing value for --kill-port" >&2
        exit 1
      fi
      shift 2
      ;;
    *)
      echo "Unknown arg: $1" >&2
      exit 1
      ;;
  esac
done

SQLITE_PATH="${SQLITE_PATH:-$SQLITE_PATH_DEFAULT}"
CHROMA_PATH="${CHROMA_PATH:-$CHROMA_PATH_DEFAULT}"

echo "About to wipe:"
echo "  SQLITE_PATH=$SQLITE_PATH"
echo "  CHROMA_PATH=$CHROMA_PATH"

if [[ "$CONFIRM" != "true" ]]; then
  read -r -p "Type 'yes' to continue: " ans
  if [[ "$ans" != "yes" ]]; then
    echo "Aborted."
    exit 1
  fi
fi

if [[ -n "$KILL_PORT" ]]; then
  if command -v lsof >/dev/null 2>&1; then
    PIDS="$(lsof -t -iTCP:"$KILL_PORT" -sTCP:LISTEN 2>/dev/null || true)"
    if [[ -n "${PIDS}" ]]; then
      echo "Killing processes listening on port $KILL_PORT: $PIDS"
      kill $PIDS 2>/dev/null || true
      sleep 0.2
      kill -9 $PIDS 2>/dev/null || true
    fi
  fi
fi

mkdir -p "$(dirname "$SQLITE_PATH")" 2>/dev/null || true

rm -f "$SQLITE_PATH"
rm -rf "$CHROMA_PATH"
mkdir -p "$CHROMA_PATH"

echo "Wipe complete."
echo "Next: restart the API server so tables/seed admin are recreated."
