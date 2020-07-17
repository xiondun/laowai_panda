from django.urls import include, path, re_path
from django.conf.urls import url


urlpatterns = [
    # path('users/', include('users.urls')),
    path('accounts/', include('accounts.urls')),
    path('conenct/', include('connect.urls')),
    path('revyoume_club/', include('revyoume_club.urls')),
    path('notification/', include('notification.urls')),
    
]