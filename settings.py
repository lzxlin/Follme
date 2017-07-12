# -*- coding: utf-8 -*-
# Django settings for note project.
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

WEB_PATH = (os.path.dirname(os.path.abspath(__file__)))

DEBUG = True

ALLOWED_HOSTS = ['172.18.234.133','125.88.24.16','127.0.0.1',]


ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE =''           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
DATABASE_NAME = ''         # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://www.postgresql.org/docs/8.1/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
# although not all variations may be possible on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Asia/Shanghai'


# 网站信息设置
APP_DOMAIN = 'http://127.0.0.1:8000/'
APP_NAME = 'Follme'
APP_VERSION = '0.1.0'
APP_COMPANY = 'Lin Zhenxi'
APP_LICENSE = 'GNU General Public License v2'

# 全局分页的每页条数
PAGE_SIZE = 8
# 管理后台列表每页条数
ADMIN_PAGE_SIZE = 20

# 网友空间的好友列表个数限制
FRIEND_LIST_MAX = 10

# Feed 相关的设置
FEED_ITEM_MAX = 20

# Email 服务器设置
EMAIL_HOST = 'smtp.foxmail.com'
EMAIL_HOST_PASSWORD = '123123'
EMAIL_HOST_USER = '786450794@qq.com'
EMAIL_SUBJECT_PREFIX = '[Follme]'

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
#LANGUAGE_CODE = 'zh-Hans'
LANGUAGE_CODE = 'zh-Hans'

DEFAULT_CHARSET = "utf-8"

LOCALE_PATHS = (
    '/conf/locale',    # /home/lynn/project/tmitter/conf/locale
)

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

ugettext = lambda s: s
LANGUAGES = (
  ('zh-Hans', u'简体中文'),
  ('en', u'English'),
)

WSGI_APPLICATION = 'wsgi.application'

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT =  '%s/statics/uploads/' % WEB_PATH 

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = '/statics/uploads/'

CKEDITOR_UPLOAD_PATH = "article_images"

# Default user face
DEFAULT_FACE = '/statics/images/face%d.png'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

CACHE_BACKEND = 'locmem:///'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '&a*2eokltx!i@0ohfk=gp(98z^8po#poq2g8r__d2b)-^gvmn0'

# List of callables that know how to import templates from various sources.

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
#    'django.middleware.doc.XViewMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    ########################自定义中间件#######################
    'mvc.middle.CommonMiddleware'

)


ROOT_URLCONF = 'urls'

##############2016-02-21############################
# STATIC_ROOT = '/statics'
STATIC_URL = '/statics/'
STATICFILES_DIRS = [os.path.join(WEB_PATH,'statics'),]#['/statics',]   #/home/lynn/project/tmitter/statics
########################################

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
        'DIRS' :[
            # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
            # Always use forward slashes, even on Windows.
            '%s/templates' % WEB_PATH ,
            # Don't forget to use absolute paths, not relative paths.
        ],

        # 'LOADERS' : [
        #     'django.template.loaders.filesystem.load_template_source',
        #     'django.template.loaders.app_directories.load_template_source',
        #     #     'django.template.loaders.eggs.load_template_source',
        # ]

    },
]


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mvc',
    'utils',
#    'tmitter',
#    'mvc',
)



DATABASES = {
    'default': {

        'ENGINE': 'django.db.backends.postgresql_psycopg2', #'django.db.backends.',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'follme',  # Or path to database file if using sqlite3.
        'USER': 'postgres',  # Not used with sqlite3.
        'PASSWORD': 'admin',  # Not used with sqlite3.
        'HOST': '127.0.0.1',  # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '5432',  # Set to empty string for default. Not used with sqlite3.

    }
}
