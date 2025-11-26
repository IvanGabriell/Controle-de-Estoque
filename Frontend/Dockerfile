# 1. Usar a imagem oficial do Nginx (versão leve 'alpine')
FROM nginx:alpine

# 2. Copiar os arquivos da pasta atual (onde está o Dockerfile, ou seja, /frontend) 
# para a pasta padrão onde o Nginx serve sites
COPY . /usr/share/nginx/html

# 3. Expor a porta 80 (porta padrão de sites http)
EXPOSE 80

# O Nginx inicia automaticamente, então não é necessário um comando CMD extra.