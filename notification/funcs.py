from .models import *
from accounts.models import Language
from .pushy import PushyAPI
from laowai_panda import settings
from django.utils.translation import ugettext_lazy as _
import json
import threading


def push_new_notification(notification):
    try:
        tokens = PushyToken.objects.filter(
            user=notification.to_user, active=True)
        with open('/root/PushyAPI.log','a',encoding='utf-8') as f: #a是追加，w覆盖
            f.write(str(tokens))
        if len(tokens) == 0:
            notification.status = Notification.FALIED_User_Has_No_Token
            notification.fb_response = _("user has no pushy token")
        else:

            data_message = {
                "content_type": notification.content_type.name,
                "object_id": notification.object_id,
                "action_name": str(dict(NotificationTemplate.ACTION_CHOICES)[notification.action])
            }
            if notification.extra_data:
                data_message.update(json.loads(notification.extra_data))

            notification_title = notification.title
            notification_message = notification.message

            if notification.to_user.default_lang:
                if notification.to_user.default_lang.short_name == 'id':
                    notification_title = getattr(
                        notification, "title_ind")
                    notification_message = getattr(
                        notification, "message_ind")
                else:
                    # notification_title = getattr(notification, "title_"+notification.to_user.default_lang.short_name)
                    # notification_message = getattr(notification, "message_"+notification.to_user.default_lang.short_name)
                    notification_title = getattr(notification, "title")
                    notification_message = getattr(notification, "message")

            data = {
                "to": [token.token for token in tokens],
                "data": {
                    "title": notification_title,
                    "id": notification.object_id,
                    "action": notification.action,
                    "message": notification_message,
                    "extra_data": data_message
                },
                "notification": {
                    "body": notification_message,
                    "badge": 1,
                    "sound": "ping.aiff"
                }
            }
            with open('/root/PushyAPI.log','a',encoding='utf-8') as f: #a是追加，w覆盖
                f.write(json.dumps(data))
            result = PushyAPI.sendPushNotification(data)

            if result['success'] == True:
                notification.status = Notification.DELIVERED
            else:
                notification.status = Notification.FALIED_FIREBASE
            notification.fb_response = str(result['results'])
    except Exception as e:
        with open('/root/PushyAPI.log','a',encoding='utf-8') as f: #a是追加，w覆盖
            f.write('发送消息异常：' + str(e))
        notification.status = Notification.FALIED_UNKNOWN
        notification.fb_response = str(e)

    notification.save()


def create_and_push_notification_sync(notification_object, action, from_user, to_users, extra_data=None):
    to_users = [user for user in to_users if user.id != from_user.id]
    if len(to_users) == 0:
        return
    languages = list(Language.objects.values_list('short_name', flat=True))
    languages.append("")
    try:
        notification_template = NotificationTemplate.objects.get(action=action)
        for to_user in to_users:
            notification_data = {}
            for lang in languages:
                if lang != "":
                    if lang == "id":
                        lang = "ind"
                    lang = "_"+lang.replace('-', '_')

                if getattr(notification_template, "title_template"+lang):
                    title = getattr(notification_template,
                                    "title_template"+lang)
                else:
                    title = notification_template.title_template

                if getattr(notification_template, "message_template"+lang):
                    message = getattr(notification_template,
                                      "message_template"+lang)
                else:
                    message = notification_template.message_template

                notification_data["title" +
                                  lang] = title
                if action == NotificationTemplate.FOLLOWED_USER_ADDED_NEW_QUESTION:
                    notification_data["message"+lang] = message.format(
                        from_user.full_name, notification_object.text[:30])
                else:
                    notification_data["message"+lang] = message.format(
                        from_user.full_name)

            notification = Notification(notification_object=notification_object,
                                        action=action, extra_data=json.dumps(
                                            extra_data) if extra_data else None,
                                        from_user=from_user, to_user=to_user, **notification_data)
            notification.save()
            push_new_notification(notification)
    except NotificationTemplate.DoesNotExist:
        error = "Notification Template For Action {0} Not Found".format(action)
        notification = Notification(notification_object=notification_object,
                                    action=action, fb_response=error,
                                    status=Notification.TEMPLATE_ACTION_NOT_FOUND,
                                    from_user=from_user, to_user=to_users[0])
        notification.save()


def create_and_push_notification(notification_object, action, from_user, to_users, extra_data=None):
    threading.Timer(0, create_and_push_notification_sync, [
                    notification_object, action, from_user, to_users, extra_data]).start()
