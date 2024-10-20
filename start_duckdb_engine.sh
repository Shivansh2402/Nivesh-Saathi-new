#!/bin/bash
#
# Run the uwsgi application
source venv/bin/activate

gunicorn -w 2 --keep-alive 60 -b 0.0.0.0:10470 --timeout 300000  --worker-class uvicorn.workers.UvicornWorker --access-logfile \
   logs/duckdb-engine-access.log --access-logformat "%(h)s %(l)s %(u)s %(t)s %(r)s %(s)s %(b)s %(f)s %(a)s TIMETAKEN:%(D)s" \
   --pid duckdb-engine.pid --log-file logs/duckdb-engine.log  --backlog 2048  --preload duckdbengine:app
