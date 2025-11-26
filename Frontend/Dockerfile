# 1. Usar a imagem oficial do Nginx (versão leve 'alpine') <--- ADICIONE O # AQUI
FROM nginx:alpine

# 2. Copiar sua configuração customizada para a pasta de configs
COPY default.conf /etc/nginx/conf.d/default.conf

# 3. Copiar os arquivos estáticos (HTML, CSS, JS) para a pasta do Nginx
COPY . /usr/share/nginx/html

# 4. Remover o index.html padrão que o Nginx instala.
RUN rm /usr/share/nginx/html/index.html 

# 5. Expor a porta 80
EXPOSE 80