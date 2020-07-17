from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^get-all/$', GetAllNotifications.as_view(), name="get_all_notifications"),
    url(r'^seen/$', SetNotificationSeen.as_view(), name="get_all_notifications"),
    url(r'^pushy-login/', PushyLogin.as_view(), name="fb_login"),
    url(r'^pushy-logout/', PushyLogout.as_view(), name="fb_logout"),

]
