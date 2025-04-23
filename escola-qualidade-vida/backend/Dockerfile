# Use a imagem oficial do Python como base
FROM python:3.11-slim

# Defina o diretório de trabalho no container
WORKDIR /app

# Copie o conteúdo da pasta 'app' do projeto local para o container
COPY ./app /app

# Copie o script adicional, caso necessário
COPY atualiza_senha.py atualiza_senha.py

# Variável de ambiente para reconhecer o módulo 'app' corretamente
ENV PYTHONPATH=/app

# Instala as dependências listadas no requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Exponha a porta 5000, que é a porta padrão do Flask
EXPOSE 5000

# Comando para rodar a aplicação Flask quando o container for iniciado
CMD ["python", "app/main.py"]
