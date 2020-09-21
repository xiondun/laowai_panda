from rest_framework import serializers
from .models import *
from drf_extra_fields.fields import Base64ImageField
from django.utils.translation import ugettext as _


class SignupSerializer(serializers.ModelSerializer):
    photo = Base64ImageField(required=False)

    class Meta:
        model = User
        exclude = ('reset_pass_code', 'username')

    def validate(self, data):
        if len(data['password']) < 8:
            raise serializers.ValidationError(
                "This password is too short. It must contain at least 8 characters.")

        try:
            int(data['name'])
            raise serializers.ValidationError(_("Name can't be number"))
        except ValueError:
            pass

        return data


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=256)
    password = serializers.CharField(max_length=256)


class TempPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=256)


class SocialLoginSerializer(serializers.Serializer):
    social_type = serializers.CharField(max_length=256)
    social_token = serializers.CharField(max_length=256)
    social_id = serializers.CharField(max_length=256)

    def validate(self, data):
        if not data['social_type'] in ['facebook', 'wechat', 'apple']:
            raise serializers.ValidationError(
                "social_type can only be 'facebook','wechat','apple'")
        return data


class RestPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(max_length=256)

    def validate(self, data):
        """
        Check that start is before finish.
        """
        if len(data['new_password']) < 8:
            raise serializers.ValidationError(
                "Password must be more than 7 characters.")

        return data


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=80)
    new_password = serializers.CharField(max_length=80)

    def validate(self, data):
        """
        Check that start is before finish.
        """
        if len(data['new_password']) < 8:
            raise serializers.ValidationError(
                "Password must be more than 7 characters.")

        return data


class AppVerifyCodeApiSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)


class DefaultLanguageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Language
        fields = ('id', 'name', 'lang_name', 'short_name', 'image')


class BasicUserInfoSerializer(serializers.ModelSerializer):
    photo = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'name', 'username', 'email', 'photo',
                  'is_following', 'account_verified')

    def get_photo(self, obj):
        if obj.photo:
            return str(obj.photo.url)
        return None

    def get_is_following(self, obj):
        try:
            user = self.context['user']
            return user.is_following(obj)
        except:
            return False


class simpleUserInfoSerializer(serializers.ModelSerializer):
    photo = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'name', 'photo', 'is_following', 'account_verified')

    def get_photo(self, obj):
        if obj.photo:
            return str(obj.photo.url)
        return None

    def get_is_following(self, obj):
        try:
            user = self.context['user']
            return user.is_following(obj)
        except:
            return False


class UpdateProfileSerializer(serializers.ModelSerializer):
    photo = Base64ImageField(required=False)
    lang_id = serializers.PrimaryKeyRelatedField(write_only=True,
                                                 source='default_lang', queryset=Language.objects.all())
    default_lang = DefaultLanguageSerializer(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'photo', 'email', 'name', 'username', 'lang_id', 'default_lang',
                  'show_my_questions', 'show_my_followup_questions')


class GetProfileSerializer(serializers.ModelSerializer):
    is_following = serializers.SerializerMethodField()
    default_lang = DefaultLanguageSerializer(read_only=True)
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()
    usefuls = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'name', 'username', 'social_type', 'photo', 'likes', 'usefuls','show_my_questions', 'show_my_followup_questions', 'is_following', 'default_lang', 'followers_count', 'following_count', 'account_verified')

        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'read_only': True},
        }

    def get_likes(self, obj):
        return 3

    def get_usefuls(self, obj):
        return obj.usefuls

    def get_followers_count(self, obj):
        return obj.followers_count

    def get_following_count(self, obj):
        return obj.following_count

    def get_is_following(self, obj):
        try:
            user = self.context['user']
            return user.is_following(obj)
        except:
            return False
