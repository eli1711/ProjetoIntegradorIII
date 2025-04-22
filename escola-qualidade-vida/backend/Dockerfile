FROM python:3.11-slim

# Diretório principal do container
WORKDIR /app

# Copia o conteúdo da pasta 'app' para dentro do container
COPY ./app /app

COPY atualiza_senha.py atualiza_senha.py
# Variável de ambiente para reconhecer o módulo 'app'
ENV PYTHONPATH=/app

# Instala as dependências
RUN pip install --no-cache-dir -r /app/requirements.txt

# Expõe a porta 5000 (caso a aplicação utilize essa porta)
EXPOSE 5000

# Comando para rodar a aplicação
CMD ["python", "app/main.py"]
