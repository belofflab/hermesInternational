import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

if os.path.exists(ENV_PATH):
    load_dotenv(ENV_PATH)

SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = True if os.getenv("DEBUG") in ["1", 1, "True", True] else False

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS").split()

CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS").split()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CRYPTO_BOT_TOKEN = os.getenv("CRYPTO_BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "modeltranslation",
    "accounts",
    "main",
    "payments",
    "ajax",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "packageLocker.urls"

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
                "accounts.context_processors.delivery_options",
                "accounts.context_processors.account_information",
            ],
        },
    },
]

WSGI_APPLICATION = "packageLocker.wsgi.application"


# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.getenv("DATABASE_NAME"),
        "USER": os.getenv("DATABASE_USER"),
        "PASSWORD": os.getenv("DATABASE_PASSWORD"),
        "HOST": os.getenv("DATABASE_HOST"),
        "PORT": os.getenv("DATABASE_PORT"),
    }
}

SITE_ID = 1


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

AUTH_USER_MODEL = "accounts.Account"
AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.AllowAllUsersModelBackend",
    "accounts.backends.EmailBackend",
)

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = os.getenv('EMAIL_PORT')
EMAIL_USE_TLS = True if os.getenv("EMAIL_USE_TLS") in ["1", 1, "True", True] else False
EMAIL_USE_SSL = True if os.getenv("EMAIL_USE_SSL") in ["1", 1, "True", True] else False
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

LANGUAGE_CODE = "ru"

TIME_ZONE = "Europe/Moscow"

USE_I18N = True

USE_TZ = True

gettext = lambda s: s

LANGUAGES = (
    ("en", gettext("English")),
    ("ru", gettext("Russian")),
)

LOCALE_PATHS = [os.path.join(BASE_DIR, "locale")]


STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

MEDIA_URL = "media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
