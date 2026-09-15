"""
BioTeacher — Self-Development Platform sozlamalari.

TZ.md 9-bo'lim (texnologiyalar steki) va 8-bo'lim (NFR-09, NFR-10, NFR-18) ga muvofiq.
Maxfiy qiymatlar `.env` faylidan o'qiladi (`.env.example` ga qarang).
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def env(key, default=None):
    """Oddiy .env o'quvchi — tashqi bog'liqliksiz (NFR-10)."""
    return os.environ.get(key, default)


def env_bool(key, default=False):
    raw = env(key)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _load_dotenv(path):
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_dotenv(BASE_DIR / ".env")

# NFR-10: prod'da SECRET_KEY env'dan keladi, DEBUG=False bo'ladi.
SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    "django-insecure-dev-only-$uu4=6ff@06aj(&$=ujz#i5nqr4-cgekp0+42(m7o%#l0uv+5=",
)
DEBUG = env_bool("DJANGO_DEBUG", True)

# Saytning asosiy domeni; SITE_ALT_DOMAINS — shu saytga olib keladigan qo'shimcha domenlar.
SITE_DOMAIN = env("SITE_DOMAIN", "bioteacher.uz")
SITE_ALT_DOMAINS = [d.strip() for d in env("SITE_ALT_DOMAINS", "najo.uz").split(",") if d.strip()]
_SITE_DOMAINS = [SITE_DOMAIN, *SITE_ALT_DOMAINS]

_default_hosts = ",".join(
    ["localhost", "127.0.0.1", *_SITE_DOMAINS, *(f"www.{d}" for d in _SITE_DOMAINS)]
)
_default_origins = ",".join(
    [*(f"https://{d}" for d in _SITE_DOMAINS), *(f"https://www.{d}" for d in _SITE_DOMAINS)]
)

ALLOWED_HOSTS = [
    h.strip() for h in env("DJANGO_ALLOWED_HOSTS", _default_hosts).split(",") if h.strip()
]
CSRF_TRUSTED_ORIGINS = [
    o.strip()
    for o in env("DJANGO_CSRF_TRUSTED_ORIGINS", _default_origins).split(",")
    if o.strip()
]


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    # BioTeacher (TZ 6.1)
    "accounts",
    "diagnostics",
    "goals",
    "content",
    "assignments",
    "development",
    "reflection",
    "progress",
    "gamification",
    "research",
    "notifications",
    "home",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "accounts.middleware.OnboardingMiddleware",
]

# WhiteNoise ixtiyoriy — o'rnatilmagan bo'lsa middleware olib tashlanadi.
try:  # pragma: no cover
    import whitenoise  # noqa: F401
except ImportError:  # pragma: no cover
    MIDDLEWARE.remove("whitenoise.middleware.WhiteNoiseMiddleware")

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "notifications.context_processors.unread_notifications",
                "accounts.context_processors.current_profile",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"
ASGI_APPLICATION = "core.asgi.application"


# TZ 9: SQLite (dev) → PostgreSQL (prod). DATABASE_URL berilsa Postgres ishlatiladi.
if env("DATABASE_URL"):
    from urllib.parse import urlparse

    _db = urlparse(env("DATABASE_URL"))
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": _db.path.lstrip("/"),
            "USER": _db.username,
            "PASSWORD": _db.password,
            "HOST": _db.hostname,
            "PORT": _db.port or 5432,
            "CONN_MAX_AGE": 60,
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


AUTH_USER_MODEL = "accounts.User"
AUTHENTICATION_BACKENDS = ["accounts.backends.EmailOrUsernameBackend"]

# NFR-09: Argon2 birinchi o'rinda (o'rnatilgan bo'lsa), aks holda PBKDF2.
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.ScryptPasswordHasher",
]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
     "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "home:dashboard"
LOGOUT_REDIRECT_URL = "home:landing"


# NFR-01: asosiy til — o'zbek (lotin); arxitektura i18n'ga tayyor.
LANGUAGE_CODE = "uz"
LANGUAGES = [("uz", "O'zbekcha"), ("ru", "Русский"), ("en", "English")]
LOCALE_PATHS = [BASE_DIR / "locale"]
TIME_ZONE = "Asia/Tashkent"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
        if not DEBUG and "whitenoise.middleware.WhiteNoiseMiddleware" in MIDDLEWARE
        else "django.contrib.staticfiles.storage.StaticFilesStorage"
    },
}

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# NFR-11: yuklanadigan fayl chegaralari.
MAX_UPLOAD_SIZE_MB = int(env("MAX_UPLOAD_SIZE_MB", "10"))
ALLOWED_UPLOAD_EXTENSIONS = [
    ".pdf", ".png", ".jpg", ".jpeg", ".webp", ".gif",
    ".docx", ".pptx", ".xlsx", ".txt", ".zip",
]
DATA_UPLOAD_MAX_MEMORY_SIZE = MAX_UPLOAD_SIZE_MB * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = DATA_UPLOAD_MAX_MEMORY_SIZE

EMAIL_BACKEND = env("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = env("EMAIL_HOST", "")
EMAIL_PORT = int(env("EMAIL_PORT", "587"))
EMAIL_HOST_USER = env("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS", True)
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", "BioTeacher <noreply@bioteacher.uz>")

SITE_NAME = "BioTeacher"
SITE_URL = env("SITE_URL", "http://127.0.0.1:8000" if DEBUG else f"https://{SITE_DOMAIN}")

# NFR-09: login urinishlarini cheklash (accounts.ratelimit).
LOGIN_RATELIMIT_ATTEMPTS = int(env("LOGIN_RATELIMIT_ATTEMPTS", "8"))
LOGIN_RATELIMIT_WINDOW_SECONDS = int(env("LOGIN_RATELIMIT_WINDOW_SECONDS", "900"))

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"

if not DEBUG:  # NFR-10, NFR-18
    SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", True)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"simple": {"format": "{levelname} {asctime} {name} {message}", "style": "{"}},
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "simple"},
        "audit_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_DIR / "logs" / "audit.log",
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 5,
            "formatter": "simple",
            "encoding": "utf-8",
        },
    },
    "loggers": {
        "bioteacher.audit": {"handlers": ["audit_file", "console"], "level": "INFO"},
    },
}
(BASE_DIR / "logs").mkdir(exist_ok=True)
