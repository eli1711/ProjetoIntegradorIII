FROM python:3.11-slim

# Instalar dependências do sistema necessárias para psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/* 
     # Limpar cache de APT para reduzir o tamanho da imagem

# Definir o diretório de trabalho no contêiner
WORKDIR /app

# Copiar o requirements.txt para o contêiner
COPY requirements.txt /app/

# Instalar as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o restante dos arquivos para o contêiner
COPY . /app

# Adicionar o diretório /app ao PYTHONPATH para garantir que o Python encontre o módulo 'app'
ENV PYTHONPATH=/app:$PYTHONPATH

# Expor a porta em que o Flask estará rodando
EXPOSE 5000

# Iniciar o Flask
CMD ["python", "/app/main.py"]
