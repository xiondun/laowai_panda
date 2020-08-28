from rest_framework import serializers
from .models import *
from accounts.serializers import GetProfileSerializer, simpleUserInfoSerializer
from drf_extra_fields.fields import Base64ImageField
from django.db.models import Avg
from django.urls import reverse


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'color',)


class LanguageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Language
        fields = ('id', 'name', 'image',)


class QuestionReplySerializer(serializers.ModelSerializer):
    comment_image = Base64ImageField(required=False)
    user = simpleUserInfoSerializer(read_only=True)
    question_id = serializers.PrimaryKeyRelatedField(write_only=True, required=False,
                                                     source='question', queryset=Question.objects.all())
    parent_reply_id = serializers.PrimaryKeyRelatedField(required=False,
                                                         source='parent_reply', queryset=QuestionReply.objects.filter(parent_reply__isnull=True))
    is_useful_by_user = serializers.SerializerMethodField()
    useful_count = serializers.SerializerMethodField()
    reply_count = serializers.SerializerMethodField()

    class Meta:
        model = QuestionReply
        fields = ('id', 'reply', 'created', 'user', 'question_id', 'parent_reply_id', 'comment_image',
                  'is_useful_by_user', 'useful_count', 'reply_count')

    def get_is_useful_by_user(self, obj):
        try:
            user = self.context['user']
            return obj.is_useful_by_user(user=user)
        except:
            return False

    def get_useful_count(self, obj):
        return obj.usefuls

    def get_reply_count(self, obj):
        return obj.reply_to_reply_count

    def validate(self, data):
        question_id = self.initial_data.get('question_id', None)
        parent_reply_id = self.initial_data.get('parent_reply_id', None)
        if not parent_reply_id and not question_id:
            raise serializers.ValidationError(
                "You have to add question_id or parent_reply_id")

        reply = data.get('reply', None)
        comment_image = data.get('comment_image', None)
        if not reply and not comment_image:
            raise serializers.ValidationError(
                "You have to add reply text or image")
        return data


class QuestionImageSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=False)
    question_id = serializers.PrimaryKeyRelatedField(write_only=True,
                                                     source='question', queryset=Question.objects.all())

    class Meta:
        model = QuestionImage
        fields = ('id', 'question_id', 'image',)


class QuestionSerializer(serializers.ModelSerializer):
    category_id = serializers.PrimaryKeyRelatedField(write_only=True,
                                                     source='category', queryset=Category.objects.all())

    lang_id = serializers.PrimaryKeyRelatedField(write_only=True,
                                                 source='language', queryset=Language.objects.all())

    is_reported_by_user = serializers.SerializerMethodField()
    is_favourite_by_user = serializers.SerializerMethodField()
    is_liked_by_user = serializers.SerializerMethodField()
    timestamp = serializers.SerializerMethodField()
    category = CategorySerializer(read_only=True)
    language = LanguageSerializer(read_only=True)
    owner = simpleUserInfoSerializer(read_only=True)
    images = QuestionImageSerializer(many=True, read_only=True)
    favourite_count = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    reply_count = serializers.SerializerMethodField()
    question_share_link = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ('id', 'text', 'language',  'owner', 'category', 'created', 'category_id', 'lang_id',
                  'is_reported_by_user', 'is_favourite_by_user', 'is_liked_by_user', 'images', 'timestamp',
                  'favourite_count', 'like_count', 'reply_count', 'question_share_link',)

    def get_timestamp(self, obj):
        return obj.modified.timestamp()

    def get_is_reported_by_user(self, obj):
        try:
            user = self.context['user']
            return obj.is_reported(user=user)
        except:
            return False

    def get_is_liked_by_user(self, obj):
        try:
            try:
                user = self.context['visitor']
            except:
                user = self.context['user']
            with open('/home/get_is_liked_by_user.log','w',encoding='utf-8') as f: #a是追加，w覆盖
                f.write(user.name)
            return obj.is_liked(user=user)
        except:
            return False

    def get_is_favourite_by_user(self, obj):
        try:
            try:
                user = self.context['visitor']
            except:
                user = self.context['user']
            return obj.is_favourite(user=user)
        except:
            return False

    def get_favourite_count(self, obj):
        return obj.favourites

    def get_like_count(self, obj):
        return obj.likes

    def get_reply_count(self, obj):
        return obj.replies_count

    def get_question_share_link(self, obj):
        return reverse('share_question', kwargs={'pk': obj.id})
