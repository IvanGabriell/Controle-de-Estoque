"""
Django settings for config project.
Versão: Testes Locais + Produção EasyPanel
"""

from pathlib import Path
import os
from datetime import timedelta

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# ==============================================================================
# 1. CONFIGURAÇÕES GERAIS
# ==============================================================================

SECRET_KEY = 'django-insecure-r#4sg#ygc(&g7em3seei-lo79*3pfeo6f1w(t4hjs1cloc=88*'

# ✅ MODO DESENVOLVIMENTO - Altere para False no EasyPanel
DEBUG = True

ALLOWED_HOSTS = [
    'api.morenadoaco.com.br',  # Produção
    'mysql-db',                # Container MySQL
    'localhost',               # Local
    '127.0.0.1',               # Local
    'backend',                 # Container interno
]

# ==============================================================================
# 2. APLICATIVOS
# ==============================================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party
    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    
    # Your apps
    'app_estoque',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ==============================================================================
# 3. BANCO DE DADOS (USANDO APENAS ENV VARS)
# ==============================================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'controle_estoque',
        
        # OBTIDO VIA ENV VARS (DB_USER, DB_PASSWORD)
        'USER': os.getenv('DB_USER', 'root'),          
        'PASSWORD': os.getenv('DB_PASSWORD', ''),      
        
        'HOST': os.getenv('DB_HOST', '127.0.0.1'),     
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# ==============================================================================
# 4. ARQUIVOS ESTÁTICOS
# ==============================================================================

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==============================================================================
# 5. DJANGO REST FRAMEWORK (ALTERADO AQUI)
# ==============================================================================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        # Autenticação para o Site/App (Token)
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        
        # Autenticação para o Navegador (Login Admin) - ADICIONADO AGORA
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# ==============================================================================
# 6. CORS - CONFIGURAÇÃO COMPLETA PARA LOCAL + PRODUÇÃO
# ==============================================================================

# ✅ CORS PARA DESENVOLVIMENTO LOCAL
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True  # Permite todas as origens
    CORS_ALLOW_CREDENTIALS = True
    
    CORS_ALLOW_HEADERS = [
        'accept', 
        'accept-encoding', 
        'authorization', 
        'content-type', 
        'dnt', 
        'origin', 
        'user-agent',
        'x-csrftoken', 
        'x-requested-with',
    ]
    
    CORS_ALLOW_METHODS = ['*']
    
    # Desativa segurança para testes
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    
    # CSRF para local
    CSRF_TRUSTED_ORIGINS = [
        'http://localhost:8000',
        'http://127.0.0.1:8000',
        'http://localhost:5500',
        'http://127.0.0.1:5500',
        'http://localhost:3000',
        'http://127.0.0.1:3000',
    ]
else:
    # ✅ CORS PARA PRODUÇÃO
    CORS_ALLOWED_ORIGINS = [
        'https://faculdade.morenadoaco.com.br',
    ]
    CORS_ALLOW_CREDENTIALS = True
    CORS_ALLOW_METHODS = [
        'DELETE', 'GET', 'OPTIONS', 'PATCH', 'POST', 'PUT',
    ]
    
    CORS_ALLOW_HEADERS = [
        'accept', 
        'accept-encoding', 
        'authorization',
        'content-type', 
        'dnt', 
        'origin', 
        'user-agent',
        'x-csrftoken', 
        'x-requested-with',
    ]
    
    # Segurança para produção
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    CSRF_TRUSTED_ORIGINS = [
        'https://api.morenadoaco.com.br',
        'https://faculdade.morenadoaco.com.br',
    ]

# Proxy settings
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True

# ==============================================================================
# 7. LOGGING
# ==============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO' if DEBUG else 'WARNING',
    },
}