FROM nginx:latest

# Definir o diretório de trabalho no contêiner
WORKDIR /usr/share/nginx/html

# Remove os arquivos padrão do Nginx
RUN rm -rf ./*

# Copiar os arquivos do frontend (public) para o contêiner
COPY public /usr/share/nginx/html

# Expondo a porta padrão do Nginx
EXPOSE 80
