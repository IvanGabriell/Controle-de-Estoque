# 1. Usar uma imagem leve do Python
FROM python:3.11-slim

# 2. Instalar dependências do sistema necessárias para o MySQL e compiladores
# (O mysqlclient precisa disso para ser instalado)
RUN apt-get update && apt-get install -y \
    gcc \
    pkg-config \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# 3. Definir o diretório de trabalho dentro do container
WORKDIR /app

# 4. Copiar o arquivo de requisitos e instalar as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Instalar o Gunicorn (Servidor de Produção para Django)
RUN pip install gunicorn

# 6. Copiar todo o código do projeto para dentro do container
COPY . .

# 7. Coletar arquivos estáticos (CSS do Admin, etc.)
# Isso move os arquivos para a pasta 'staticfiles' que definimos no settings.py
RUN python manage.py collectstatic --no-input

# 8. Expor a porta 8000
EXPOSE 8000

# 9. Comando para rodar o servidor (Usando Gunicorn em vez de runserver)
# 'config.wsgi:application' aponta para o arquivo wsgi.py na pasta config
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]