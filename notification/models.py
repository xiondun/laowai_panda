from django.db import models
from accounts.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from model_utils.models import TimeStampedModel


class PushyToken(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="pushy_tokens")
    token = models.CharField(max_length=100)
    active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.user)


class NotificationTemplate(models.Model):

    NO_ACTION = 0
    QUESTION_LIKED = 1
    QUESTION_SHARED = 2
    QUESTION_COMMENT = 3
    COMMENT_USEFUL = 4
    USER_FOLLOW = 5
    QUESTION_FAV = 6
    FOLLOWED_USER_ADDED_NEW_QUESTION = 7
    FOLLOWED_QUESTION_COMMENT = 8
    COMMENT_REPLY = 9

    ACTION_CHOICES = (
        (NO_ACTION, _("No action")),
        (QUESTION_LIKED, _("Question liked")),
        (QUESTION_SHARED, _("Question shared")),
        (QUESTION_COMMENT, _("Got a comment")),
        (FOLLOWED_QUESTION_COMMENT, _("New comment on followed question")),
        (COMMENT_USEFUL, _("Useful comment")),
        (USER_FOLLOW, _("Got followed")),
        (QUESTION_FAV, _("Question favourite")),
        (FOLLOWED_USER_ADDED_NEW_QUESTION, _("Followed user added new question")),
        (COMMENT_REPLY, _("Got a reply to your comment")),
    )

    title_template = models.CharField(max_length=100, null=True)
    message_template = models.TextField(null=True)
    action = models.IntegerField(
        choices=ACTION_CHOICES, unique=True, default=NO_ACTION)


class Notification(TimeStampedModel):

    CREATED = 0
    PASSED_2_FIREBASE = 1
    DELIVERED = 2
    FALIED_User_Has_No_Token = 3
    FALIED_FIREBASE = 4
    FALIED_UNKNOWN = 5
    TEMPLATE_ACTION_NOT_FOUND = 6

    STATUS_CHOICES = (
        (CREATED, _("Created")),
        (PASSED_2_FIREBASE, _("Passed to pushy")),
        (DELIVERED, _("Delivered")),
        (FALIED_User_Has_No_Token, _("Faild as user hasn't notification token")),
        (FALIED_FIREBASE, _("Pushy Faild")),
        (FALIED_UNKNOWN, _("Unknown Error")),
        (TEMPLATE_ACTION_NOT_FOUND, _("Template action not exist please add one")),
    )

    title = models.CharField(max_length=200, null=True)
    message = models.TextField(null=True)
    action = models.IntegerField(
        choices=NotificationTemplate.ACTION_CHOICES, default=NotificationTemplate.NO_ACTION)
    status = models.IntegerField(
        choices=STATUS_CHOICES, default=CREATED)
    fb_response = models.TextField(null=True)
    seen = models.BooleanField(default=False)
    to_user = models.ForeignKey(
        User, related_name="my_notifications", on_delete=models.CASCADE, null=True)
    from_user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True)
    extra_data = models.CharField(max_length=100, null=True)
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=True)
    object_id = models.PositiveIntegerField(null=True)
    notification_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return self.get_action_display()
