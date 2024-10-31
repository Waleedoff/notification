#! /usr/bin/env sh
set -e

python init_db.py

# Start Gunicorn
exec gunicorn -k "uvicorn.workers.UvicornWorker" -c "gunicorn_conf.py" "app.main:app"