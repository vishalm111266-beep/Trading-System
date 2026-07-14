#!/bin/sh
set -eu

ROOT="$(cd "$(dirname "$0")" && pwd)"

fail() { echo "ERROR: $1" >&2; exit 1; }

command -v python3 >/dev/null 2>&1 || fail "python3 not found"
echo "[ok] python3 $(python3 --version 2>&1 | cut -d' ' -f2)"

command -v uv >/dev/null 2>&1 || fail "uv not found"
echo "[ok] uv $(uv --version 2>&1 | cut -d' ' -f2)"

command -v git >/dev/null 2>&1 || fail "git not found"
echo "[ok] git $(git --version 2>&1 | cut -d' ' -f3)"

command -v opencode >/dev/null 2>&1 || fail "opencode not found"
echo "[ok] opencode installed"

if [ ! -d "$ROOT/.venv" ]; then
  echo "Creating .venv..."
  uv venv "$ROOT/.venv" --python python3
fi

echo "Syncing dependencies..."
cd "$ROOT" && uv sync

echo "Bootstrap complete."
