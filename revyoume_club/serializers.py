import datetime
from rest_framework import serializers
from .models import *
from accounts.serializers import GetProfileSerializer
from drf_extra_fields.fields import Base64ImageField
from django.db.models import Avg
from django.urls import reverse


class ChannelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Channel
        fields = ('id', 'name', 'logo')


class PostSerializer(serializers.ModelSerializer):
    is_liked_by_user = serializers.SerializerMethodField()
    timestamp = serializers.SerializerMethodField()
    post_share_link = serializers.SerializerMethodField()
    media_link = serializers.SerializerMethodField()
    youko_url = serializers.SerializerMethodField()
    channel = ChannelSerializer(read_only=True)
    like_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('id', 'text', 'media', 'youko_url', 'channel', 'timestamp', 'like_count', 'show_in',
                  'created', 'post_share_link', 'media_link', 'is_liked_by_user', 'type')

    def get_like_count(self, obj):
        return obj.likes

    def get_youko_url(self, obj):
        return obj.get_youko_link

    def get_timestamp(self, obj):
        return obj.modified.timestamp()

    def get_post_share_link(self, obj):
        return reverse('share_post', kwargs={'pk': obj.id})

    def get_media_link(self, obj):
        if obj.get_youko_link:
            return reverse('show_post_media', kwargs={'pk': obj.id})
        else:
            return ""
    def get_is_liked_by_user(self, obj):
        try:
            user = self.context['user']
            return obj.is_liked(user)
        except:
            return False
