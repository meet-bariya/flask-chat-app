#!/bin/sh
FLASK_APP=${FLASK_APP:-'app.main:app'}
/opt/venv/bin/flask run --host 0.0.0.0 --port 8000