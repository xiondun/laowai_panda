from django.db import models
from django.utils.functional import cached_property
from accounts.models import *
from model_utils.models import TimeStampedModel
from colorfield.fields import ColorField
from notification.models import Notification
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.fields import GenericRelation


# Create your models here.


class QuestionReply(TimeStampedModel):
    reply = models.TextField(null=True, blank=True)
    permissions = None
    comment_image = models.ImageField(
        upload_to='comment_image/', null=True, blank=True)
    question = models.ForeignKey(
        'connect.Question', related_name='replies', on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, related_name='replies',
                             on_delete=models.CASCADE, null=True, blank=True)
    useful_by_users = models.ManyToManyField(
        User, related_name="my_useful_replies", blank=True)
    parent_reply = models.ForeignKey(
        'QuestionReply', related_name='replies', on_delete=models.CASCADE, null=True, blank=True)
    notifications = GenericRelation(Notification, related_query_name="replies")

    @property
    def usefuls(self):
        return self.useful_by_users.count()

    @property
    def reply_to_reply_count(self):
        return self.replies.count()

    def is_useful_by_user(self, user):
        if user in self.useful_by_users.all():
            return True
        else:
            return False

    @property
    def is_parent(self):
        if self.parent_reply is None:
            return True
        else:
            return False


    def delete(self, *args, **kwargs):
        Notification.objects.filter(
            object_id=self.id, content_type=ContentType.objects.get_for_model(self)).delete()
        super(QuestionReply, self).delete(*args, **kwargs)

class Category(models.Model):
    name = models.CharField(max_length=200)
    color = ColorField(default='#FF0000')
    order = models.IntegerField(_("Order Number"), default=1)


    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"
        verbose_name = "Category"


class Question(TimeStampedModel):
    text = models.TextField()
    permissions = None
    owner = models.ForeignKey(
        User, related_name='my_questions', on_delete=models.CASCADE, null=True, blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="questions")
    language = models.ForeignKey(
        Language, on_delete=models.SET_NULL, null=True, blank=True, related_name="questions")
    fav_by_users = models.ManyToManyField(
        User, related_name="my_fav_questions", blank=True)
    liked_by_users = models.ManyToManyField(
        User, related_name="my_liked_questions", blank=True)
    reported_by_users = models.ManyToManyField(
        User, related_name="my_reported_questions", blank=True)
    notifications = GenericRelation(Notification, related_query_name="questions")

    def __str__(self):
        return self.owner.username

    @property
    def likes(self):
        return self.liked_by_users.count()

    @property
    def replies_count(self):
        return self.replies.filter(parent_reply__isnull=True).count()

    @property
    def reports(self):
        return self.reported_by_users.count()

    @property
    def favourites(self):
        return self.fav_by_users.count()

    def is_reported(self, user):
        if user in self.reported_by_users.all():
            return True
        else:
            return False

    def is_favourite(self, user):
        if user in self.fav_by_users.all():
            return True
        else:
            return False

    def is_liked(self, user):
        if user in self.liked_by_users.all():
            return True
        else:
            return False

    def delete(self, *args, **kwargs):
        Notification.objects.filter(
            object_id=self.id, content_type=ContentType.objects.get_for_model(self)).delete()
        # delete the notifications manually as the on delete not woking with the cascade 
        Notification.objects.filter(
            object_id__in=self.replies.values_list('id', flat=True), content_type=ContentType.objects.get(app_label='connect', model='questionreply')).delete()
        super(Question, self).delete(*args, **kwargs)


class QuestionImage(models.Model):
    question = models.ForeignKey(
        Question, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField()
