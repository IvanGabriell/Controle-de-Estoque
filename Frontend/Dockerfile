Usar a imagem oficial do Nginx (versão leve 'alpine')
FROM nginx:alpine

# ⚠️ NOVO: Copia sua configuração customizada (default.conf) para a pasta do Nginx
COPY default.conf /etc/nginx/conf.d/default.conf

# Copiar os arquivos estáticos (HTML, CSS, JS) para a pasta do Nginx
COPY . /usr/share/nginx/html

# Expor a porta 80
EXPOSE 80