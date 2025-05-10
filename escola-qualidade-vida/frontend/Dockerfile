FROM nginx:latest

WORKDIR /usr/share/nginx/html

# Remove os arquivos padrão do Nginx
RUN rm -rf ./*

# Copia os arquivos do frontend para o container
COPY public /usr/share/nginx/html

# Expondo a porta padrão do Nginx
EXPOSE 80
ENV PYTHONPATH="/app:${PYTHONPATH}"

