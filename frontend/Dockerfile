# Usa uma imagem leve do NGINX para servir arquivos estáticos
FROM nginx:alpine

# Remove o conteúdo padrão do NGINX (garante que não haja conflitos)
RUN rm -rf /usr/share/nginx/html/*

# Copia seus arquivos HTML, CSS e JS para o diretório de serviço do NGINX
COPY . /usr/share/nginx/html

# O NGINX por padrão roda na porta 80
EXPOSE 80

# Comando para iniciar o servidor
CMD ["nginx", "-g", "daemon off;"]