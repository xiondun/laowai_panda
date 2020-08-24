from django.utils.translation import ugettext_lazy as _
from rest_framework.views import APIView
from rest_framework.response import Response

from .funcs import push_new_notification
from .models import Notification, PushyToken
from .serializers import NotificationSerializer
from rest_framework import status
from django.db.models import Q
from django.core.paginator import Paginator


def queryset_paginator(queryset, page, page_size=10):
    paginator = Paginator(queryset, page_size)
    number = int(paginator.num_pages)
    if int(page) > number:
        raise Http404()
    queryset = paginator.page(page)
    return queryset, number


class GetAllNotifications(APIView):
    def get(self, request, format=None):
        notifications = Notification.objects.filter(to_user=request.user)
        notifications = notifications.filter(Q(questions__isnull=False) | Q(
            users__isnull=False) | Q(replies__isnull=False))
        notifications = notifications.prefetch_related().order_by('-id')
        page = request.GET.get("page", 1)
        page_size = request.GET.get("page_size", 10)
        queryset, number = queryset_paginator(notifications, page, page_size)
        serializer = NotificationSerializer(
            queryset, context={'user': request.user}, many=True)
        return Response({"data": serializer.data, "pages_num": number}, status=status.HTTP_200_OK)


class SetNotificationSeen(APIView):
    def post(self, request, format=None):
        user = request.user
        notification_id = request.data.get("notification_id", "")
        try:
            notification = Notification.objects.get(id=notification_id)
            notification.seen = True
            notification.save()
            push_new_notification(notification)
            return Response({"detail": _("Notification updated successfully.")}, status=status.HTTP_200_OK)
        except Notification.DoesNotExist:
            return Response({"detail": _("Notification updated successfully.")}, status=status.HTTP_200_OK)


class PushyLogin(APIView):
    def post(self, request, format=None):
        if request.data.get("pushy_token") is None:
            return Response({"detail": _("pushy_token is required.")}, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        token = request.data.get("pushy_token")
        PushyToken.objects.update_or_create(token=token, defaults={
            'active': True,
            'user': user,
        })
        return Response({'detail': _("Pushy Token added successfully.")})


class PushyLogout(APIView):
    def post(self, request, format=None):
        if request.data.get("pushy_token") is None:
            return Response({"detail": _("pushy_token is required.")}, status=status.HTTP_400_BAD_REQUEST)
        token = request.data.get("pushy_token")
        try:
            pushy_token = PushyToken.objects.get(token=token)
            pushy_token.delete()
            return Response({'detail': _("Pushy Token loged out successfully.")})
        except PushyToken.DoesNotExist:
            return Response({'detail': _("Pushy Token loged out successfully.")}, status=status.HTTP_400_BAD_REQUEST)
