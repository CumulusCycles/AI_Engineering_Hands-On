#!/usr/bin/env bash
# Runs Postman collection with Newman against the full author workflow.
# Optional: include a lightweight admin smoke subset by setting POSTMAN_INCLUDE_ADMIN_SMOKE=1.
# Safe default: attempts to disable real OpenAI calls so "generate*" endpoints return 503 quickly.
#
# Usage (from ScriptSprout/):
#   ./test-scripts/test-postman.sh
#   POSTMAN_LIVE=1 ./test-scripts/test-postman.sh     # allow real OpenAI calls if OPENAI_API_KEY is set
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

if [[ -n "${POSTMAN_PORT:-}" ]]; then
  PORT="${POSTMAN_PORT}"
else
  PORT="$(
    python - <<'PY'
import socket
s = socket.socket()
s.bind(("127.0.0.1", 0))
print(s.getsockname()[1])
s.close()
PY
  )"
fi
BASE_URL="http://127.0.0.1:${PORT}"
COLLECTION_PATH="$REPO_ROOT/backend/postman/ScriptSprout.postman_collection.json"

if [[ ! -f "$COLLECTION_PATH" ]]; then
  echo "Missing collection: $COLLECTION_PATH" >&2
  exit 1
fi

AUTH_SUFFIX="$(date +%s)"
AUTH_USERNAME="${POSTMAN_AUTH_USERNAME:-postman_author_${AUTH_SUFFIX}}"
AUTH_PASSWORD="${POSTMAN_AUTH_PASSWORD:-PostmanPass123}"
ADMIN_USERNAME="${POSTMAN_ADMIN_USERNAME:-seedadmin}"
ADMIN_PASSWORD="${POSTMAN_ADMIN_PASSWORD:-seedpassword123}"

if [[ "${POSTMAN_LIVE:-0}" != "1" ]]; then
  export PYTEST_CURRENT_TEST=1
  export OPENAI_API_KEY=""
  unset OPENAI_SMOKE_MODEL OPENAI_NLP_MODEL OPENAI_SYNOPSIS_MODEL OPENAI_TITLE_MODEL OPENAI_DESCRIPTION_MODEL
else
  unset PYTEST_CURRENT_TEST
fi

INCLUDE_ADMIN_SMOKE="${POSTMAN_INCLUDE_ADMIN_SMOKE:-0}"
if [[ "$INCLUDE_ADMIN_SMOKE" == "1" ]]; then
  export ADMIN_USERNAME="$ADMIN_USERNAME"
  export ADMIN_PASSWORD="$ADMIN_PASSWORD"
fi

SERVER_LOG="$(mktemp "/tmp/scriptsprout-postman-server-XXXXXX.log")"
cleanup() {
  if [[ -n "${SERVER_PID:-}" ]]; then
    kill "${SERVER_PID}" 2>/dev/null || true
    wait "${SERVER_PID}" 2>/dev/null || true
    pkill -P "${SERVER_PID}" 2>/dev/null || true
  fi

  if command -v lsof >/dev/null 2>&1; then
    PIDS="$(lsof -t -iTCP:"${PORT}" -sTCP:LISTEN 2>/dev/null || true)"
    if [[ -n "${PIDS}" ]]; then
      kill ${PIDS} 2>/dev/null || true
      sleep 0.2
      kill -9 ${PIDS} 2>/dev/null || true
    fi
  fi
  rm -f "$SERVER_LOG" 2>/dev/null || true
}
trap cleanup EXIT

echo "Starting API server on ${BASE_URL} ..."
(
  cd "$REPO_ROOT/backend"
  uv run uvicorn app.main:create_app --factory --host 127.0.0.1 --port "$PORT" >"$SERVER_LOG" 2>&1
) &
SERVER_PID="$!"

python - "$BASE_URL" <<'PY'
import json
import sys
import time
import urllib.request

base = sys.argv[1].rstrip("/")
health_url = base + "/health"
deadline = time.time() + 30

while time.time() < deadline:
    try:
        with urllib.request.urlopen(health_url, timeout=2) as r:
            body = r.read().decode("utf-8")
            j = json.loads(body)
            if j.get("status") == "ok":
                print("API is up")
                sys.exit(0)
    except Exception:
        time.sleep(0.25)

print("Timed out waiting for API to be ready")
sys.exit(1)
PY

echo "Running Newman workflow ..."
unset OPENAI_API_KEY || true

FOLDERS=(
  "Auth"
  "NLP extract"
  "Content"
  "Synopsis"
  "Title + Description"
  "Story"
  "Thumbnail"
  "Audio"
  "Media"
  "Semantic index"
  "Semantic search"
)
if [[ "$INCLUDE_ADMIN_SMOKE" == "1" ]]; then
  FOLDERS+=(
    "Admin / RBAC"
    "Admin metrics"
  )
fi
NEWMAN_ARGS=(run "$COLLECTION_PATH" --env-var "baseUrl=$BASE_URL")
NEWMAN_ARGS+=(--env-var "adminUsername=$ADMIN_USERNAME")
NEWMAN_ARGS+=(--env-var "adminPassword=$ADMIN_PASSWORD")
for folder in "${FOLDERS[@]}"; do
  NEWMAN_ARGS+=(--folder "$folder")
done
npx -y newman "${NEWMAN_ARGS[@]}"

echo "Postman runner finished successfully."
