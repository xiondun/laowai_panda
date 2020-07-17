from __future__ import absolute_import, unicode_literals

# import pymysql

# pymysql.install_as_MySQLdb()

from .base import *

import os

DEBUG = True

ALLOWED_HOSTS = ['*']
SYS_ADMINS = ['2596746097@qq.com', '357772807@qq.com']

EMAIL_HOST = 'smtp.laowaipanda.com'
EMAIL_PORT = 80
EMAIL_HOST_USER = 'info@laowaipanda.com'
EMAIL_HOST_PASSWORD = 'Maro2020'
EMAIL_USE_TLS = False
DEFAULT_FROM_EMAIL = 'info@laowaipanda.com'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'laowai_panda_db_laowai_panda',
        'USER': 'root',
        'PASSWORD': '123456',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'use_unicode': True,
        },
    },
}

FACEBOOK_CLIENT_ID = '3059550770728200'
FACEBOOK_CLIENT_SECRET = '6c604fec7b4f730e07024abf9bad5012'

WECHAT_TOKEN = u'your_token'
WECHAT_APP_ID = 'wxdc73f9e6049e6fe7'
WECHAT_APP_SECRET = '55c5c90ffe31922a1382a959da57e84b'

SOCIAL_AUTH_APPLE_PRIVATE_KEY = b'-----BEGIN PRIVATE KEY-----\nMIGTAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBHkwdwIBAQQgTsJp2WMezrFF/s/iFqc/qisHVZvzKbs41xXqwwEMLg6gCgYIKoZIzj0DAQehRANCAASijsAL6ncIhJM12LlVBgxlmhrayvjv/PZ3uoLgTGV5cOCPmsutnMcEr6CnAeCp4olei3LZ4uYVTxe5fFX5AFU1\n-----END PRIVATE KEY-----'
SOCIAL_AUTH_APPLE_KEY_ID = '39V5T7282Z'
SOCIAL_AUTH_APPLE_TEAM_ID = 'X2PL288BYD'
CLIENT_ID = 'com.Laowaipanda'

JET_MODULE_YANDEX_METRIKA_CLIENT_ID = 'd7a39dcbd86d4bbfb581f2dae047493a'
JET_MODULE_YANDEX_METRIKA_CLIENT_SECRET = '81317acb98c04a66a54cbbd26ebac6e6'
