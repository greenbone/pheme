# -*- coding: utf-8 -*-
# pheme/settings.py
# Copyright (C) 2020-2021 Greenbone Networks GmbH
#
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
Django settings for pheme project.

Generated by 'django-admin startproject' using Django 3.1.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from pathlib import Path
import secrets
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
__configured_base = os.environ.get("PHEME_BASE_PATH")
BASE_DIR = (
    Path(__configured_base)
    if __configured_base
    else Path(__file__).resolve(strict=True).parent.parent
)
STATIC_DIR = BASE_DIR / "static"
TEMPLATE_DIR = BASE_DIR / "template"
# set default to actual gos path instead of static dir

GSAD_URL = os.environ.get("GSAD_URL", "https://localhost/gmp")

SENTRY_DSN = os.environ.get("SENTRY_DSN_PHEME")

# load sentry_sdk only when SENTRY_DSN_PHEME is set otherwise don't bother
if SENTRY_DSN is not None:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    # pylint: disable=E0110
    # Due to the MYPY handling within sentry_sdk.init, to have a nicer user
    # experience than to have to look up lambdas, pylint detectes this as an
    # abstract class; which it is.
    sentry_sdk.init(
        SENTRY_DSN,
        traces_sample_rate=1.0,
        environment=os.environ.get("SENTRY_ENVIRONMENT"),
        server_name=os.environ.get("SENTRY_SERVER_NAME"),
        integrations=[DjangoIntegration()],
    )

DATA_UPLOAD_MAX_MEMORY_SIZE = None

PHEME_CONFIGURATION_PATH = Path(
    os.environ.get(
        "PHEME_CONFIGURATION_PATH",
        "/var/lib/pheme" if Path("/var/lib/pheme").exists() else Path("/tmp/"),
    )
)


SECRET_KEY_LOCATION = PHEME_CONFIGURATION_PATH.joinpath("api_key")

PARAMETER_FILE_ADDRESS = PHEME_CONFIGURATION_PATH.joinpath("parameter.json")
DATA_OBJECT_PATH = "/opt/greenbone/feed/gvmd"
GOS_VERSION = "21.04"
DEFAULT_PARAMETER_ADDRESS = (
    os.environ.get("DEFAULT_PARAMETER_FILE_ADDRESS")
    or f"{DATA_OBJECT_PATH}/{GOS_VERSION}/pheme/default-parameter.json"
)


def __load_or_create_api_key() -> str:
    if SECRET_KEY_LOCATION.exists():
        may_token = SECRET_KEY_LOCATION.read_text()
        if len(may_token.strip()) > 0:
            return may_token
    token = secrets.token_urlsafe(50)
    SECRET_KEY_LOCATION.write_text(token)
    return token


SECRET_KEY = os.environ.get("PHEME_API_KEY", __load_or_create_api_key())

ENV_HOSTS = os.environ.get("ALLOWED_HOSTS", "*")
DEBUG = os.environ.get("PHEME_DEBUG", "").lower() == "true"
ALLOWED_HOSTS = ENV_HOSTS.split(" ") if ENV_HOSTS else []

# Application definition

INSTALLED_APPS = [
    "pheme",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "pheme.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            TEMPLATE_DIR,
        ],
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

WSGI_APPLICATION = "pheme.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = []


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = "/static/"
STATICFILES_DIRS = [
    STATIC_DIR,
    TEMPLATE_DIR,
]

# Logging
# https://docs.djangoproject.com/en/3.1/topics/logging/

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
        "syslog": {
            "class": "logging.handlers.SysLogHandler",
            "formatter": "standard",
            "facility": "user",
            "address": "/dev/log",
        },
        "file": {
            "class": "logging.FileHandler",
            "formatter": "standard",
            "filename": "/var/log/pheme/pheme.log"
            if Path("/var/log/pheme").exists()
            else "/tmp/pheme.log",
        },
    },
    "formatters": {
        "standard": {
            "format": "{module}#{funcName} {levelname} {asctime}: {message}",
            "style": "{",
        },
    },
    "root": {
        "handlers": [
            "syslog" if Path("/dev/log").exists() and not DEBUG else "console",
            "file",
        ],
        "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
    },
}
# https://docs.djangoproject.com/en/3.1/topics/cache/
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": "/tmp/django_cache",
        "TIMEOUT": 1 * 60 * 2 * 60,  # 2 hours
    }
}

# testing
REST_FRAMEWORK = {
    "TEST_REQUEST_RENDERER_CLASSES": [
        "pheme.renderer.XMLRenderer",
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.MultiPartRenderer",
    ],
}
