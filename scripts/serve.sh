#!/usr/bin/env bash
# Run the FastAPI backend bound to all interfaces so it can be reached locally
# and tunneled (e.g. via `ngrok http 8000`). Uses the default SQLite database.
set -euo pipefail

PORT="${PORT:-8000}"

exec uv run uvicorn app.main:app --host 0.0.0.0 --port "${PORT}"
