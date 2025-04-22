# Usa a imagem oficial do Nginx baseada no Alpine
FROM nginx:alpine

# Limpa o HTML padrão do Nginx
RUN rm -rf /usr/share/nginx/html/*

# Cria a pasta 'pages' caso seja necessário
RUN mkdir -p /usr/share/nginx/html/pages

# Copia tudo de 'public' (do seu diretório local) para dentro da pasta do Nginx
COPY public/ /usr/share/nginx/html/

# Copia o arquivo de configuração do Nginx customizado
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expõe a porta 80
EXPOSE 80
