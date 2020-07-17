
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import Notification, PushyToken, NotificationTemplate
from .funcs import push_new_notification

# Register your models here.

class NotificationAdmin(admin.ModelAdmin):
    search_fields = ('from_user', 'to_user')
    list_filter = ('status', 'action',)
    list_display = ('from_user', 'to_user', 'title','created', 'status', 'action')
    readonly_fields = ([field.name for field in Notification._meta.fields])
    actions = ['duplicate_resend_notification']

    def duplicate_resend_notification(self, request, queryset):
        for notification in queryset.all():
            notification.pk = None
            notification.status = Notification.CREATED
            notification.save()
            push_new_notification(notification)
        self.message_user(request, "Notification successfully sent, new records added to it.")
    
    duplicate_resend_notification.short_description = "Duplicate and resend notification to selected items"


class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ('title_template', 'message_template')


class PushyTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'active')


admin.site.register(NotificationTemplate, NotificationTemplateAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(PushyToken, PushyTokenAdmin)
