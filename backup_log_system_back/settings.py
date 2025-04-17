from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')

DEBUG = os.getenv('DJANGO_DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', '').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_crontab',

    'dbbackup',
    'rest_framework',
    'corsheaders',
    'rest_framework_simplejwt.token_blacklist',

    'core.apps.CoreConfig',
]

DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'

BASE_BACKUP_DIR = {'location': BASE_DIR / os.getenv('DJANGO_BASE_BACKUP_DIR_LOCATION', 'backup')}

# Email settings
EMAIL_BACKEND = os.getenv('DJANGO_EMAIL_BACKEND')
EMAIL_HOST = os.getenv('DJANGO_EMAIL_HOST')
EMAIL_PORT = int(os.getenv('DJANGO_EMAIL_PORT', '465'))
EMAIL_USE_TLS = os.getenv('DJANGO_EMAIL_USE_TLS', 'False') == 'True'
EMAIL_USE_SSL = os.getenv('DJANGO_EMAIL_USE_SSL', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('DJANGO_EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('DJANGO_EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.getenv('DJANGO_DEFAULT_FROM_EMAIL')
SERVER_EMAIL = os.getenv('DJANGO_SERVER_EMAIL')

DEFAULT_TOKEN_GENERATOR = 'core.tokens.CustomTokenGenerator'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

CORS_ALLOWED_ORIGINS = os.getenv('DJANGO_CORS_ALLOWED_ORIGINS', '').split(',')

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'backup_log_system_back.urls'

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

WSGI_APPLICATION = 'backup_log_system_back.wsgi.application'

# Database settings
DATABASES = {
    'default': {
        'ENGINE': os.getenv('DJANGO_DATABASE_ENGINE', 'django.db.backends.postgresql'),
        'NAME': os.getenv('DJANGO_DATABASE_NAME'),
        'USER': os.getenv('DJANGO_DATABASE_USER'),
        'PASSWORD': os.getenv('DJANGO_DATABASE_PASSWORD'),
        'HOST': os.getenv('DJANGO_DATABASE_HOST', 'localhost'),
        'PORT': os.getenv('DJANGO_DATABASE_PORT', '5432'),
    }
}

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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'