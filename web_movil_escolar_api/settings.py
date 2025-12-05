import os
from pathlib import Path
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Seguridad - IMPORTANTE: Genera una nueva clave secreta para producción
SECRET_KEY = os.environ.get('SECRET_KEY', 'clave-temporal-solo-para-desarrollo-cambiar-en-produccion')

# Solo DEBUG=True en desarrollo local
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# Hosts permitidos
ALLOWED_HOSTS = []
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Añade localhost para desarrollo si está en DEBUG
if DEBUG:
    ALLOWED_HOSTS.extend(['localhost', '127.0.0.1', '[::1]'])

# Aplicaciones instaladas
INSTALLED_APPS = [
    'corsheaders',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_filters',                
    'rest_framework',
    'rest_framework.authtoken',    
    'web_movil_escolar_api',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',     
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Configuración de CORS - ajusta según tus necesidades
CORS_ALLOWED_ORIGINS = [
    'http://localhost:4200',
    'http://localhost:54399',  
    'http://127.0.0.1:54399',
]
CORS_ALLOW_CREDENTIALS = True

ROOT_URLCONF = 'web_movil_escolar_api.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'web_movil_escolar_api.wsgi.application'

# CONFIGURACIÓN DE BASE DE DATOS PARA RENDER
# ------------------------------------------------------------
# Render automáticamente proporciona DATABASE_URL en el formato:
# postgresql://usuario:contraseña@host:puerto/nombre_bd

# Configuración principal usando dj-database-url
DATABASES = {
    'default': dj_database_url.config(
        # Fallback para desarrollo local (usa SQLite si no hay DATABASE_URL)
        default='sqlite:///' + str(BASE_DIR / 'db.sqlite3'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Si quieres ver la configuración de la BD (solo para debugging)
if DEBUG:
    print(f"Database config: {DATABASES['default']}")

# Validadores de contraseña
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internacionalización
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Archivos estáticos (CRÍTICO para Render)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Si tienes archivos estáticos adicionales
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Archivos multimedia
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Rest Framework
REST_FRAMEWORK = {
    'COERCE_DECIMAL_TO_STRING': False,
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'web_movil_escolar_api.models.BearerTokenAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
}

# Logging
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
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
    },
}

# Configuraciones de seguridad para producción
if not DEBUG:
    # SSL/HTTPS
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    
    # HSTS
    SECURE_HSTS_SECONDS = 31536000  # 1 año
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # Otros
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    
    # WhiteNoise para producción
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'