from .base import *  # noqa
from .base import env

import environ
import os

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = True
# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="!!!SET DJANGO_SECRET_KEY!!!",
)
# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ["localhost", "0.0.0.0", "127.0.0.1"]

# CACHES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#caches
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "",
    }
}

# TEMPLATES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES[0]["OPTIONS"]["debug"] = DEBUG  # noqa F405

# EMAIL
# ------------------------------------------------------------------------------
{% if cookiecutter.use_mailhog == 'y' and cookiecutter.use_docker == 'y' -%}
# https://docs.djangoproject.com/en/dev/ref/settings/#email-host
EMAIL_HOST = env("EMAIL_HOST", default="mailhog")
# https://docs.djangoproject.com/en/dev/ref/settings/#email-port
EMAIL_PORT = 1025
{%- elif cookiecutter.use_mailhog == 'y' and cookiecutter.use_docker == 'n' -%}
# https://docs.djangoproject.com/en/dev/ref/settings/#email-host
EMAIL_HOST = "localhost"
# https://docs.djangoproject.com/en/dev/ref/settings/#email-port
EMAIL_PORT = 1025
{%- else -%}
# https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = env(
    "DJANGO_EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend"
)
{%- endif %}

{%- if cookiecutter.use_whitenoise == 'y' %}

# WhiteNoise
# ------------------------------------------------------------------------------
# http://whitenoise.evans.io/en/latest/django.html#using-whitenoise-in-development
INSTALLED_APPS = ["whitenoise.runserver_nostatic"] + INSTALLED_APPS  # noqa F405
{% endif %}

# django-debug-toolbar
# ------------------------------------------------------------------------------
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#prerequisites
INSTALLED_APPS += ["debug_toolbar"]  # noqa F405
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#middleware
MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]  # noqa F405
# https://django-debug-toolbar.readthedocs.io/en/latest/configuration.html#debug-toolbar-config
DEBUG_TOOLBAR_CONFIG = {
    "DISABLE_PANELS": ["debug_toolbar.panels.redirects.RedirectsPanel"],
    "SHOW_TEMPLATE_CONTEXT": True,
}
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#internal-ips
INTERNAL_IPS = ["127.0.0.1", "10.0.2.2"]
{% if cookiecutter.use_docker == 'y' -%}
if env("USE_DOCKER") == "yes":
    import socket

    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS += [".".join(ip.split(".")[:-1] + ["1"]) for ip in ips]
    {%- if cookiecutter.js_task_runner == 'Gulp' %}
    try:
        _, _, ips = socket.gethostbyname_ex("node")
        INTERNAL_IPS.extend(ips)
    except socket.gaierror:
        # The node container isn't started (yet?)
        pass
    {%- endif %}
{%- endif %}

# django-extensions
# ------------------------------------------------------------------------------
# https://django-extensions.readthedocs.io/en/latest/installation_instructions.html#configuration
INSTALLED_APPS += ["django_extensions"]  # noqa F405
{% if cookiecutter.use_celery == 'y' -%}

# Celery
# ------------------------------------------------------------------------------
{% if cookiecutter.use_docker == 'n' -%}
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#task-always-eager
CELERY_TASK_ALWAYS_EAGER = True
{%- endif %}
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#task-eager-propagates
CELERY_TASK_EAGER_PROPAGATES = True

{%- endif %}
# Your stuff...
# ------------------------------------------------------------------------------
ROOT_DIR = (
    environ.Path(__file__) - 3
)

MAX_LOG_BYTES = 1024 * 1024 * 10

PROJECT_NAME = os.path.basename(ROOT_DIR)

LOG_FILE_PATH = os.path.join(ROOT_DIR, os.path.join("logs"))

if not os.path.exists(LOG_FILE_PATH):
    try:
        os.makedirs(LOG_FILE_PATH)
    except OSError:
        pass

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)s : %(asctime)s : %(pathname)s : %(funcName)s : "
            "lineno: %(lineno)d : %(message)s"
        }
    },
    "handlers": {
        "stdout": {"class": "logging.StreamHandler"},
        "default": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOG_FILE_PATH, "%s.log" % PROJECT_NAME),
            "formatter": "verbose",
            "maxBytes": MAX_LOG_BYTES,
        },
        "django": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOG_FILE_PATH, "%s.log" % PROJECT_NAME),
            "maxBytes": MAX_LOG_BYTES,
        },
        "django.server": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(
                LOG_FILE_PATH, "%s_server.log" % PROJECT_NAME
            ),
        },
        "database": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(
                LOG_FILE_PATH, "%s_db.log" % PROJECT_NAME
            ),
            "maxBytes": MAX_LOG_BYTES,
        },
    },
    "loggers": {
        "": {
            "handlers": ["default", "stdout"],
            "level": "INFO",
            "propagate": True,
        },
        "django": {
            "handlers": ["django"],
            "level": "INFO",
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["database"],
            "level": "INFO",
            "propagate": False,
        },
        "django.server": {
            "handlers": ["django.server", "stdout"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
