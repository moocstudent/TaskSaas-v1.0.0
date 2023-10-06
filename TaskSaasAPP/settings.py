"""
Django settings for TaskSaasAPP project.

Generated by 'django-admin startproject' using Django 1.11.28.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
import django
from django.utils.encoding import smart_str

django.utils.encoding.smart_text = smart_str

from django.conf.urls import static

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'vt1!_$!!o4ka5gakevbar9u!fhsjmuw900lw_3)f&s3!6ke3ep'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'channels',  # channels应用
    'TaskChat',
    'TaskSaas.apps.TasksaasConfig',
    'web.apps.WebConfig',
    'rest_framework',  # django restframework
]

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ]
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'web.middleware.auth.AuthMiddleWare',
]

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
            # 或"hosts": [os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1')],
        },
    },
}

ROOT_URLCONF = 'TaskSaasAPP.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
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

WSGI_APPLICATION = 'TaskSaasAPP.wsgi.application'

# 设置ASGI应用
ASGI_APPLICATION = 'TaskChat.routing.application'

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'tasksaas',
        'USER': 'root',
        'PASSWORD': 'zhangqi1112',
        'HOST': 'localhost',
        'PORT': 3306,
        'CHARSET': 'utf8',
        'OPTIONS': {'charset': 'utf8mb4'},
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
# STATIC_ROOT = 'web/static'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'web/static/')
]

# 自己的短信模板相关配置
TENCENT_SMS_APP_ID = 00000000  # 应用ID
TENCENT_SMS_APP_KEY = "0000000000000"  # 应用Key
TENCENT_SMS_SIGN = "短信签名"  # 腾讯云创建签名时填写的签名内容（使用公众号的话这个值一般是公众号全称或简称）

TENCENT_SMS_TEMPLATES = {
    'register': 645735,
    'login': 645736,
}
# Django-redis配置
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://0.0.0.0:6379",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 1000,
                "encoding": "utf-8"
            },
            # "PASSWORD": '0'
        }
    }
}

# 登录白名单：无需登录就能访问的页面
WHITE_REGEX_URL_LIST = [
    '/register/',
    '/send/sms/',
    '/login/sms/',
    '/login/',
    '/image/code/',
    '/index/',
]

# COS文件存储相关ID/KEY
SECRET_ID = '替换为用户的 secretId'  # 替换为用户的 secretId
SECRET_KEY = '替换为用户的 secretKey'  # 替换为用户的 secretKey
REGION = 'ap-chengdu'

try:
    from .local_settings import *
except ImportError:
    pass

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="https://a77a9b368b455e0b34edb8b6f5061ef6@o4505836607766528.ingest.sentry.io/4505878319071232",
    integrations=[DjangoIntegration()],
    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True,
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
)
