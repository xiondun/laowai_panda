from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import validate_email
from localflavor.us.us_states import STATE_CHOICES
from django.contrib.contenttypes.fields import GenericRelation

# Create your models here.


class Language(models.Model):
    name = models.CharField(max_length=200)
    lang_name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=200, default='en')
    image = models.ImageField(
        "Image", upload_to='Language/', null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Languages"
        verbose_name = "Language"


class User(AbstractUser):
    NO_SOCIAL = 0
    FACEBOOK = 1
    WECHAT = 2
    APPLE = 3

    SOCIAL_TYPES = ((NO_SOCIAL, "No social"), (FACEBOOK, "Facebook"), (WECHAT, "Wechat"),
                    (APPLE, "Apple"))

    photo = models.ImageField(upload_to='images/', null=True, blank=True)
    email = models.EmailField('email address', unique=True)
    permissions = None
    reset_pass_code = models.CharField(max_length=50, null=True, blank=True)
    social_type = models.IntegerField(
        choices=SOCIAL_TYPES, db_index=True, default=NO_SOCIAL)
    reset_pass_code_attemps = models.IntegerField(default=-1)
    email_verified = models.BooleanField(default=False)
    account_verified = models.BooleanField(default=False)
    verify_mail_code = models.CharField(max_length=50, null=True)
    name = models.CharField(max_length=50, null=True)
    likes = models.PositiveIntegerField(default=0)
    usefuls = models.PositiveIntegerField(default=0)
    show_my_questions = models.BooleanField(default=True)
    show_my_followup_questions = models.BooleanField(default=True)
    blocked_users = models.ManyToManyField(
        'User', related_name='blockers', blank=True)
    following_users = models.ManyToManyField(
        'User', related_name='followers', blank=True)
    default_lang = models.ForeignKey(
        Language, on_delete=models.SET_NULL, null=True, blank=True, related_name="user_lang")
    notifications = GenericRelation('notification.Notification', related_query_name="users")

    def is_following(self, user):
        if user in self.following_users.all():
            return True
        else:
            return False

    @property
    def followers_count(self):
        return self.followers.all().count()

    @property
    def full_name(self):
        return self.name if self.name else self.username 

    @property
    def following_count(self):
        return self.following_users.all().count()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email
