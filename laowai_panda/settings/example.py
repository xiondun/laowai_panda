from __future__ import absolute_import, unicode_literals

from .base import *

import os

DEBUG = True

ALLOWED_HOSTS = []
SYS_ADMINS = ['ibrahim@excelcodes.com']

EMAIL_HOST = 'smtp.laowaipanda.com'
EMAIL_PORT = 465 
EMAIL_HOST_USER = 'info@laowaipanda.com'
EMAIL_HOST_PASSWORD = 'Maro2020'
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'info@laowaipanda.com'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

FACEBOOK_CLIENT_ID = '3059550770728200'
FACEBOOK_CLIENT_SECRET = '6c604fec7b4f730e07024abf9bad5012'

WECHAT_TOKEN = u'your_token'
WECHAT_APP_ID = u'your_app_id'
WECHAT_APP_SECRET = u'your_app_secret'

# SOCIAL_AUTH_APPLE_PRIVATE_KEY = b'-----BEGIN PRIVATE KEY-----\nMIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgwhdmCDqD8wtXvpnau/Y7ouIZDNWBuQWnaeIbxHNxquOhRANCAASAFFsjeFHOIYu4vheGrHbjJRYtecJglZov3LcBDq2lBtSG1itxNhccwmqojFx8C4R5VuO+CR+1SUaLgCNXUHnG\n-----END PRIVATE KEY-----'
SOCIAL_AUTH_APPLE_PRIVATE_KEY = b'-----BEGIN PRIVATE KEY-----\nMIGTAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBHkwdwIBAQQgTsJp2WMezrFF/s/iFqc/qisHVZvzKbs41xXqwwEMLg6gCgYIKoZIzj0DAQehRANCAASijsAL6ncIhJM12LlVBgxlmhrayvjv/PZ3uoLgTGV5cOCPmsutnMcEr6CnAeCp4olei3LZ4uYVTxe5fFX5AFU1\n-----END PRIVATE KEY-----'
SOCIAL_AUTH_APPLE_KEY_ID = '39V5T7282Z'
SOCIAL_AUTH_APPLE_TEAM_ID = 'X2PL288BYD'
CLIENT_ID = 'com.Laowai.Panda'

JET_MODULE_YANDEX_METRIKA_CLIENT_ID = 'd7a39dcbd86d4bbfb581f2dae047493a'
JET_MODULE_YANDEX_METRIKA_CLIENT_SECRET = '81317acb98c04a66a54cbbd26ebac6e6'