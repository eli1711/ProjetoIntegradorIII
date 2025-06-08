#!/usr/bin/env bash

# Instalar o Rasa se não estiver instalado
if ! command -v rasa &> /dev/null
then
    echo "Rasa não encontrado, instalando..."
    pip install rasa
fi

# Iniciar o servidor de ações do Rasa
rasa run actions &

# Iniciar o servidor principal do Rasa com a API habilitada e CORS configurado
rasa run --enable-api --cors "*" --debug
