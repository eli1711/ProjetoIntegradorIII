# Usando a imagem oficial do Python
FROM python:3.11-slim

# Definir o diretório de trabalho
WORKDIR /app

# Copiar os arquivos do backend para o contêiner
COPY ./app /app

# Instalar as dependências do projeto
RUN pip install --no-cache-dir -r requirements.txt

# Expor a porta em que o Flask estará rodando
EXPOSE 5000

# Iniciar o Flask
CMD ["python", "main.py"]
