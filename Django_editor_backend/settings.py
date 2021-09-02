import os,sqlite3
# from mongoengine import connect
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNdcING: keep the secret key used in production secret!
SECRET_KEY = ')!-z(9n^yts=@wa080pf+rb=(*!@7s5)g!k&8r7axe286surg$'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*',]
"""
Django 缓存系统 by Shay
节省数据 渲染时间
"""
CACHES = {
    'default':{
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'cache_table_home',
        'TIMEOUT': 600, #超市时间
        'OPTIONS': {
            'MAX_ENTRIES': 5000   #最大并发量
        }
    }
}

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'homeApp', #新加主页
    'courseApp',
    'commitApp',
    'execriseApp',
    'online_editor',
    'DjangoUeditor',
    # 'haystack',
    'identity',
]

# HAYSTACK_CONNECTIONS = {
#     'default' : {
#         'ENGINE' : 'courseApp.whoosh_backend.WhooshEngine',
#         'PATH' : os.path.join(BASE_DIR, 'whoosh_index')
#     },
# }
# HAYSTACK_SEARCH_RESULT_PER_PAGE = 10
# HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor' #更新索引的条件： 每有一个新的课程更新的时候

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
#    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Django_editor_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')], #设置共享路径
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

WSGI_APPLICATION = 'Django_editor_backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {

'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
#use the SQLite
# connect('db.sqlite3')


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'zh-Hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)

# Code files
SOURCE_FILE_PATH = os.path.abspath("/tmp/code.py")
INPUT_FILE_PATH = os.path.abspath("/tmp/input.txt")
OUTPUT_FILE_PATH = os.path.abspath("/tmp/code.out")
RUN_IN_DOCKER_SH_PATH = os.path.abspath("./run_in_docker.sh")

MEDIA_URL = '/media/' #设置保存路径
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')