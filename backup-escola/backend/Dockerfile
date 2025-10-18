FROM python:3.11-slim

# Dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Define o diretório correto do projeto
WORKDIR /app

# Copia tudo que está em backend/
COPY . /app

# Adiciona o caminho ao PYTHONPATH
ENV PYTHONPATH=/app:$PYTHONPATH

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta do Flask
EXPOSE 5000

# Inicia a aplicação
CMD ["python", "main.py"]
