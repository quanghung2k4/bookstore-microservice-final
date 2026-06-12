import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = "order-service-secret-key"
DEBUG = True
ALLOWED_HOSTS = [
    "*",
    "localhost", 
    "127.0.0.1",
    "user_service",
    "user_service:8004",
    "product_service",
    "product_service:8001", 
    "cart_service",
    "cart_service:8002",
    "order_service",
    "order_service:8003",
    "payment_service",
    "payment_service:8005",
    "api_gateway",
    "api_gateway:8000"
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "orders",
]

MIDDLEWARE = [
    "orders.middleware.DisableHostCheckMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

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

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.getenv("SQLITE_PATH", str(BASE_DIR / "db.sqlite3")),
    }
}

AUTH_PASSWORD_VALIDATORS = []
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = "/static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://localhost:8001")
CART_SERVICE_URL = os.getenv("CART_SERVICE_URL", "http://localhost:8002")
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:8004")
PAYMENT_SERVICE_URL = os.getenv("PAYMENT_SERVICE_URL", "http://localhost:8005")
AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://localhost:8007")
