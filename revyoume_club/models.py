from django.db import models
from django.utils.functional import cached_property
from accounts.models import User
from solo.models import SingletonModel
from model_utils.models import TimeStampedModel

# Create your models here.


class Channel(models.Model):
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='channels/')
    
    def __str__(self):
        return self.name


class Post(TimeStampedModel):
    TXT_VIDEO = 0
    TXT_IMAGE = 1
    ONLY_TEXT = 2

    TYPES = ((TXT_VIDEO, "Text and video"), (TXT_IMAGE, "Text and image"),
             (ONLY_TEXT, "Only text"))

    MEDIA = 1
    ARTICLES = 2
    SHOW_TYPES = ((MEDIA, "Media"), (ARTICLES, "Articles"))
    permissions = None
    text = models.TextField()
    type = models.IntegerField(choices=TYPES, db_index=True, default=ONLY_TEXT)
    show_in = models.IntegerField(choices=SHOW_TYPES, db_index=True, default=ARTICLES)
    media = models.FileField(upload_to="posts/media/", null=True, blank=True)
    youko_link = models.URLField("youko url", null=True, blank=True,max_length=5000)
    # sina_link = models.URLField("sina url", null=True, blank=True)
    channel = models.ForeignKey(
        Channel, on_delete=models.SET_NULL, null=True, blank=True, related_name="posts")
    liked_by_users = models.ManyToManyField(
        'accounts.User', related_name="my_liked_posts", blank=True)

    def __str__(self):
        return self.text

    def is_liked(self, user):
        if user in self.liked_by_users.all():
            return True
        else:
            return False
    @property
    def likes(self):
        return self.liked_by_users.count()

    @property
    def get_youko_link(self):
        if 'youku.com' in str(self.youko_link):
            firstDelPos = str(self.youko_link).find("id_")
            secondDelPos = str(self.youko_link).find(".html")
            video_id = str(self.youko_link)[firstDelPos+3:secondDelPos]
            yoko_url = RevyoumeClubSetting.load().youko_link
            return "{0}{1}".format(yoko_url, video_id)
        else:
            return str(self.youko_link)
    # @property
    # def get_sina_link(self):
    #     return str(self.sina_link)
        # firstDelPos = str(self.sina_link).find("id_")
        # secondDelPos = str(self.sina_link).find(".html")
        # video_id = str(self.sina_link)[firstDelPos+3:secondDelPos]
        # yoko_url = RevyoumeClubSetting.load().sina_link
        # return "{0}{1}".format(yoko_url, video_id)


class RevyoumeClubSetting(SingletonModel):
    revyoume_club_link = models.URLField("Revyoume Club Link", max_length=200, null=True)
    youko_link = models.URLField("youko url")
    # sina_link = models.URLField("sina url")
    revyoume_club_enabled = models.BooleanField("Enable Revyoume Club", default=True)

    def __str__(self):
        return self.revyoume_club_link
    
    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
