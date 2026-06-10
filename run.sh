#!/usr/bin/env sh

# Stop any process using port 8000 so the app can start cleanly.
PORT=8000
pids=$(lsof -tiTCP:${PORT} -sTCP:LISTEN)
if [ -n "$pids" ]; then
  echo "Stopping process on port ${PORT}: $pids"
  echo "$pids" | xargs -r kill -9
fi

# Use the project virtual environment when available.
PYTHON=.venv/bin/python
if [ ! -x "$PYTHON" ]; then
  PYTHON=python3
fi

exec "$PYTHON" -m uvicorn app.main:app --host 127.0.0.1 --port ${PORT}
