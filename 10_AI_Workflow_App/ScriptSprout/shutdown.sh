#!/usr/bin/env bash
# Stop local frontend/backend dev servers for this app (ScriptSprout).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

BACKEND_PORT=8000
FRONTEND_PORT=5173
FRONTEND_PORT_MAX=5180

stop_by_port() {
  local port="$1"
  local name="$2"
  local pids
  pids="$(lsof -ti tcp:"$port" || true)"

  if [[ -z "$pids" ]]; then
    echo "==> $name is not running on port $port"
    return 0
  fi

  echo "==> Stopping $name on port $port (PID(s): $pids)"
  kill $pids 2>/dev/null || true
}

stop_frontend() {
  local found=0
  for port in $(seq "$FRONTEND_PORT" "$FRONTEND_PORT_MAX"); do
    local pids
    pids="$(lsof -ti tcp:"$port" || true)"
    if [[ -n "$pids" ]]; then
      found=1
      echo "==> Stopping Frontend on port $port (PID(s): $pids)"
      kill $pids 2>/dev/null || true
    fi
  done

  if [[ "$found" -eq 0 ]]; then
    # Fallback: terminate remaining Vite dev processes in this workspace.
    local vite_pids
    vite_pids="$(pgrep -f "vite.*${SCRIPT_DIR}/frontend" || true)"
    if [[ -n "$vite_pids" ]]; then
      echo "==> Stopping Frontend Vite process(es): $vite_pids"
      kill $vite_pids 2>/dev/null || true
      found=1
    fi
  fi

  if [[ "$found" -eq 0 ]]; then
    echo "==> Frontend is not running on ports ${FRONTEND_PORT}-${FRONTEND_PORT_MAX}"
  fi
}

echo "==> Shutting down ScriptSprout services"
stop_frontend
stop_by_port "$BACKEND_PORT" "Backend"
echo "==> Shutdown signal sent."
