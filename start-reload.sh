#! /usr/bin/env sh
set -e

python init_db.py

# Start Uvicorn with live reload
exec uvicorn --reload --host 0.0.0.0 --port 80 --log-level info "app.main:app"