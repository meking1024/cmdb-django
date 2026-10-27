#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
VENV_DIR="$(pwd)/.venv"
if [ ! -x "$VENV_DIR/bin/python" ]; then
  BASE_PYTHON="${PYTHON_BIN:-python}"
  "$BASE_PYTHON" -m venv --system-site-packages "$VENV_DIR"
fi
PYTHON="$VENV_DIR/bin/python"
if ! "$PYTHON" -c 'import django, streamlit, psycopg2, django_filters' >/dev/null 2>&1; then
  "$PYTHON" -m pip install -r requirements.txt
fi
if [ "$("$PYTHON" -c 'import django; print(django.get_version())')" != "5.0.3" ]; then
  "$PYTHON" -m pip install Django==5.0.3
fi
if [ "$("$PYTHON" -c 'import django_filters; print(django_filters.__version__)')" != "24.2" ]; then
  "$PYTHON" -m pip install django-filter==24.2
fi
"$PYTHON" manage.py migrate
"$PYTHON" manage.py runserver 127.0.0.1:8000 &
API_PID=$!
cleanup() {
  kill "$API_PID" 2>/dev/null || true
  wait "$API_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM
"$PYTHON" -m streamlit run streamlit_app.py --server.address 127.0.0.1 --server.port 8501
