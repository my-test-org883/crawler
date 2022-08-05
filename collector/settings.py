import os
from pathlib import Path

from config import (LEVEL_DEBUG, PSQL_DB, PSQL_HOST, PSQL_PORT, PSQL_PSW,
                    PSQL_USER)

from . import log_conf

BASE_DIR = Path(__file__).resolve().parent.parent

LOG_FILE_MAX_SIZE = 500
LOG_DIRECTORY = os.path.join(BASE_DIR, "logs")
log_conf.configure(LOG_DIRECTORY, LOG_FILE_MAX_SIZE)

SECRET_KEY = "70ea4db9-d3eb-47f6-9ea1-e4cd49e49f60"

DEBUG = LEVEL_DEBUG

ALLOWED_HOSTS = []
ALLOWED_HOSTS_ENV = os.environ.get("ALLOWED_HOSTS", "*")
if ALLOWED_HOSTS_ENV:
    ALLOWED_HOSTS.extend(ALLOWED_HOSTS_ENV.split(","))

INSTALLED_APPS = [
    "app.collector",
    "corsheaders",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
]

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
    "access-control-allow-origin",
]

ROOT_URLCONF = ".urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = ".wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": PSQL_DB,
        "USER": PSQL_USER,
        "PASSWORD": PSQL_PSW,
        "HOST": PSQL_HOST,
        "PORT": PSQL_PORT,
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = False

STATIC_URL = "/static/"
STATIC_ROOT = "/static/"
