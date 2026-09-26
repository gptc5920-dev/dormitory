import json
import os
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "development-only-change-me")
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = [host.strip() for host in os.environ.get("DJANGO_ALLOWED_HOSTS","ickwwsoogco44cwoskc4kcgw.76.13.217.76.sslip.io", "127.0.0.1,localhost").split(",") if host.strip()]
if not DEBUG and (SECRET_KEY == "development-only-change-me" or len(SECRET_KEY) < 50):
    raise ImproperlyConfigured("Set DJANGO_SECRET_KEY to a unique secret of at least 50 characters in production.")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "rest_framework.authtoken",
    "accounts",
    "tenants",
    "monitoring",
    "violations",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
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
        "OPTIONS": {"context_processors": [
            "django.template.context_processors.request",
            "django.contrib.auth.context_processors.auth",
            "django.contrib.messages.context_processors.messages",
        ]},
    }
]
WSGI_APPLICATION = "config.wsgi.application"

DB_ENGINE = os.environ.get("DB_ENGINE", "mysql")
local_database_path = BASE_DIR / "config" / "database.local.json"
local_database = {}
if DEBUG and local_database_path.is_file():
    local_database = json.loads(local_database_path.read_text(encoding="utf-8"))

if DB_ENGINE == "mysql":
    DATABASES = {"default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ.get("MYSQL_DATABASE", local_database.get("NAME", "dormitory")),
        "USER": os.environ.get("MYSQL_USER", local_database.get("USER", "root" if DEBUG else "dormitory")),
        "PASSWORD": os.environ.get("MYSQL_PASSWORD", local_database.get("PASSWORD", "")),
        "HOST": os.environ.get("MYSQL_HOST", local_database.get("HOST", "127.0.0.1")),
        "PORT": os.environ.get("MYSQL_PORT", local_database.get("PORT", "3306")),
        "CONN_MAX_AGE": 60,
        "CONN_HEALTH_CHECKS": True,
        "OPTIONS": {
            "charset": "utf8mb4",
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            "isolation_level": "read committed",
        },
        "TEST": {"CHARSET": "utf8mb4", "COLLATION": "utf8mb4_bin"},
    }}
elif DB_ENGINE == "sqlite" and DEBUG:
    # Explicit opt-in only for local tests and exporting the old database.
    DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}
else:
    raise ImproperlyConfigured("Use DB_ENGINE=mysql (or sqlite with DJANGO_DEBUG=1 for local development).")

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
AUTH_USER_MODEL = "accounts.User"

LANGUAGE_CODE = "en-us"
TIME_ZONE = os.environ.get("DJANGO_TIME_ZONE", "Asia/Singapore")
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",") if origin.strip()]
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = not DEBUG
SECURE_REDIRECT_EXEMPT = [r"^api/health/$"]
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

CORS_ALLOWED_ORIGINS = [origin.strip() for origin in os.environ.get(
    "CORS_ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
).split(",") if origin.strip()]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework.authentication.TokenAuthentication"],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_PAGINATION_CLASS": "config.pagination.StandardResultsPagination",
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "EXCEPTION_HANDLER": "config.api.api_exception_handler",
    "DEFAULT_THROTTLE_RATES": {"login": "10/minute"},
}

YOLO_MODEL_PATH = os.environ.get("YOLO_MODEL_PATH", str(BASE_DIR / "models" / "yolo11n.pt"))
YOLO_CONFIDENCE = float(os.environ.get("YOLO_CONFIDENCE", "0.45"))
DETECTION_COOLDOWN_SECONDS = int(os.environ.get("DETECTION_COOLDOWN_SECONDS", "60"))
VIDEO_SAMPLE_EVERY_FRAMES = int(os.environ.get("VIDEO_SAMPLE_EVERY_FRAMES", "15"))
VIDEO_MAX_SAMPLED_FRAMES = int(os.environ.get("VIDEO_MAX_SAMPLED_FRAMES", "300"))
MAX_FRAME_UPLOAD_BYTES = int(os.environ.get("MAX_FRAME_UPLOAD_BYTES", str(8 * 1024 * 1024)))
MAX_IMAGE_UPLOAD_BYTES = int(os.environ.get("MAX_IMAGE_UPLOAD_BYTES", str(10 * 1024 * 1024)))
MAX_VIDEO_UPLOAD_BYTES = int(os.environ.get("MAX_VIDEO_UPLOAD_BYTES", str(250 * 1024 * 1024)))
