#!/bin/sh
set -eu

ROOT="$(cd "$(dirname "$0")" && pwd)"

echo "Installing dependencies..."
cd "$ROOT" && uv sync

echo "Install complete."
