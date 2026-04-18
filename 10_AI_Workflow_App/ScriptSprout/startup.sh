#!/usr/bin/env bash
# Launch backend first, then frontend once backend /health is ready.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"
BACKEND_URL="http://127.0.0.1:8000/health"

backend_pid=""

cleanup() {
  if [[ -n "$backend_pid" ]] && kill -0 "$backend_pid" 2>/dev/null; then
    echo
    echo "==> Stopping backend (PID $backend_pid)"
    kill "$backend_pid" 2>/dev/null || true
    wait "$backend_pid" 2>/dev/null || true
  fi
}

trap cleanup EXIT INT TERM

echo "==> Starting backend (uvicorn)"
(
  cd "$BACKEND_DIR"
  exec uv run uvicorn app.main:create_app --factory --reload --host 127.0.0.1 --port 8000
) &
backend_pid=$!

echo "==> Waiting for backend health: $BACKEND_URL"
max_tries=60
for ((i = 1; i <= max_tries; i++)); do
  if curl -fsS "$BACKEND_URL" >/dev/null 2>&1; then
    echo "==> Backend is ready"
    break
  fi
  if ! kill -0 "$backend_pid" 2>/dev/null; then
    echo "Backend process exited before becoming healthy."
    exit 1
  fi
  sleep 1
done

if ! curl -fsS "$BACKEND_URL" >/dev/null 2>&1; then
  echo "Backend did not become healthy within ${max_tries}s."
  exit 1
fi

echo "==> Starting frontend (Vite dev server on :5173)"
cd "$FRONTEND_DIR"
exec npm run dev -- --host 127.0.0.1 --port 5173 --strictPort
