import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# SECRET_KEY = 'django-insecure-p#z!m^!b($d!m=^a549-$yk#2t=-@^7ja+(q2h7*xr$$hw_k#+'

DEBUG = True

# ALLOWED_HOSTS = []

SECRET_KEY = os.getenv('SECRET_KEY', default='secret_key')

# DEBUG = os.getenv('DEBUG', default=False) == 'True'

ALLOWED_HOSTS = ['158.160.67.222', '127.0.0.1', 'localhost', 'food.viewdns.net']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'djoser',
    'django_filters',
    'api.apps.ApiConfig',
    'recipes.apps.RecipesConfig',
    'users.apps.UsersConfig',
    'colorfield',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'foodgram_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'foodgram_backend.wsgi.application'

# DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.postgresql',
#        'NAME': os.getenv('POSTGRES_DB', 'foodgram'),
#        'USER': os.getenv('POSTGRES_USER', 'foodgram_user'),
#        'PASSWORD': os.getenv('POSTGRES_PASSWORD', ''),
#        'HOST': os.getenv('DB_HOST', ''),
#        'DB_PORT': os.getenv('DB_PORT', '5432'),
#    }
# }
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'foodgram',
        'USER': 'foodgram_user',
        'PASSWORD': 'foodgram_password',
        'HOST': '158.160.67.222',
        'PORT': 5432,
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

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'

STATIC_ROOT = BASE_DIR / 'static'

MEDIA_URL = '/media/'

MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'users.User'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'DEFAULT_PAGINATION_CLASS': [
        'api.pagination.StandartPaginator',
    ],
    'PAGE_SIZE': 6,
    'SEARCH_PARAM': 'name',
}

DJOSER = {
    'LOGIN_FIELD': 'email',
    'HIDE_USERS': False,
    'PERMISSIONS': {
        'current_user': ['rest_framework.permissions.AllowAny'],
        'user_list': ['rest_framework.permissions.AllowAny'],
    },
    'SERIALIZERS': {
        'user': 'djoser.serializers.UserSerializer',
        'user_list': 'djoser.serializers.UserSerializer',
        'set_password': 'djoser.serializers.SetPasswordSerializer'
    }
}

EMAIL_LENGTH = 254

FIELD_LENGTH = 150

MIN_COOKING_TIME = 1

MAX_COOKING_TIME = 360

MAX_QUANTITY = 1000

MIN_QUANTITY = 1

SMALL_FIELD_LENGTH = 60

SHORT_FIELD_LENGTH = 50

TITLE_LENGTH = 200
