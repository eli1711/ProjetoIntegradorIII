#!/bin/sh

echo "⌛ Aguardando MySQL iniciar..."

while ! nc -z db 3306; do
  sleep 1
done

echo "✅ MySQL está pronto. Iniciando aplicação Flask..."
exec python main.py
