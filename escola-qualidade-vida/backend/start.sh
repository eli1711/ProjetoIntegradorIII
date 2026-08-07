#!/bin/sh
set -e

echo "Aguardando PostgreSQL iniciar..."

while ! python - <<'PY'
import os
import socket

host = os.environ.get("DB_HOST", "postgres")
port = int(os.environ.get("DB_PORT", "5432"))

try:
    with socket.create_connection((host, port), timeout=2):
        pass
except OSError:
    raise SystemExit(1)
PY
do
  sleep 1
done

echo "PostgreSQL esta pronto. Aplicando migracoes..."
python -m flask --app app:create_app db upgrade

echo "Iniciando aplicacao Flask..."
exec gunicorn --bind 0.0.0.0:5000 wsgi:app
