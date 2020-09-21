# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views import View
from rest_framework.views import APIView
from .serializers import *
from rest_framework.response import Response
from rest_framework import status
from django.contrib import auth
from django.utils.translation import ugettext as _
from rest_framework.authtoken.models import Token
from rest_framework import permissions
import uuid
from helpers._mails import Mail
import random
import string
from django.contrib.auth.models import update_last_login
from rest_framework import status, generics, request
import urllib.request
from django.core.files import File
from django.core.files.base import ContentFile
from .auth import Auth
from django.urls import reverse
from notification.funcs import create_and_push_notification
from notification.models import NotificationTemplate
from random import randint
from django.contrib.auth.hashers import make_password


def slugify(str):
    str = str.lower()
    str = str.replace(" ", "-")
    str = str.replace(",", "-")
    str = str.replace("(", "-")
    str = str.replace(")", "")
    str = str.replace("؟", "")
    return str


def randomized_code(l):
    from random import randint
    range_start = 10**(l-1)
    range_end = (10**l)-1
    return randint(range_start, range_end)


def randomString(stringLength=20):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


class Logout(APIView):

    def post(self, request, format=None):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)


class Signup(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        context = dict()
        serializer = SignupSerializer(data=request.data)
        serializer.initial_data['email'] = serializer.initial_data['email'].lower(
        ).strip()
        if serializer.is_valid():
            username = slugify(serializer.validated_data['name'])
            while True:
                try:
                    User.objects.get(username=username)
                    username = (
                        "{0}-{1}").format(slugify(serializer.validated_data['name']), randint(0, 999999))
                except User.DoesNotExist:
                    break
            serializer.validated_data['username'] = username
            serializer.validated_data['password'] = make_password(
                serializer.initial_data['password'])
            serializer.validated_data['verify_mail_code'] = randomString(50)
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            verification_url = reverse('accounts:email_verification',  args=(
                user.email, user.verify_mail_code,))
            Mail.verify_email(user, verification_url)
            context['detail'] = _("Signup Succsesfuly")
            return Response(context, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResendVerificationEmail(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        context = dict()
        serializer = TempPasswordSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = User.objects.get(email=serializer.data['email'])
                if user.email_verified:
                    context['detail'] = _("Email already verified")
                else:
                    user.verify_mail_code = randomString(50)
                    user.save()
                    verification_url = reverse('accounts:email_verification',  args=(
                        user.email, user.verify_mail_code,))
                    Mail.verify_email(user, verification_url)
                    context['detail'] = _("Verification e-mail sent")
            except User.DoesNotExist:
                context['error'] = _("Email doesn't exist.")
                Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(context, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Login(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        context = dict()
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        email = serializer.data['email']
        password = serializer.data['password']
        user = auth.authenticate(email=email, password=password)
        if user is None:
            context['error'] = _(
                "Please enter the correct email and password.")
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        token, created = Token.objects.get_or_create(user=user)
        # context['detail']="Login Succsesfuly"
        #if user.email_verified:
        context['token'] = token.key
        #context['email_verified'] = user.email_verified
        update_last_login(None, user)
        return Response(context, status=status.HTTP_200_OK)
        context['error'] = _("Please verify your email.")
        return Response(context, status=status.HTTP_400_BAD_REQUEST)


class SocialLogin(APIView):
    '''
    social_id will be saved in the email by this format social_id@social_type.com
    social_token will be saved in the password
    '''
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        social_token = request.data.get('social_token')
        social_type = request.data.get('social_type')
        social_id = request.data.get('social_id')
        context = dict()
        serializer = SocialLoginSerializer(data=request.data)
        if serializer.is_valid():
            if social_type == 'facebook':
                auth = Auth.facebook_auth(social_token, social_id)
            elif social_type == 'wechat':
                auth = Auth.wechat(social_token, social_id)
            elif social_type == 'apple':
                auth = Auth.apple(social_token, social_id)
            else:
                return Response({"detail": _('Social type not supported')}, status=status.HTTP_400_BAD_REQUEST)
            if auth['Valid'] == True:
                if social_type == 'twitter':
                    email = '{0}@{1}.com'.format(
                        auth['userdata']['id_str'], social_type)
                else:
                    email = auth['userdata']['email']
                try:
                    user = User.objects.get(email=email)
                except User.DoesNotExist:
                    if social_type == 'facebook':
                        user = User.objects.create_user(social_type=User.FACEBOOK,
                                                        username=email, email=email, password=social_token, email_verified=True, name=auth['userdata']['name'])
                    elif social_type == 'apple':
                        user = User.objects.create_user(social_type=User.APPLE,
                                                        username=email, email=email, password=social_token, email_verified=True)
                    elif social_type == 'wechat':
                        name = auth['userdata']['name']
                        user = User.objects.create_user(social_type=User.WECHAT,
                                                        name=name, username=email, email=email, password=social_token, email_verified=True)
                        if auth['userdata']['image']:
                            user.photo.save(
                                name+'.jpg', auth['userdata']['image'], save=True)
                    user.save()
                token, created = Token.objects.get_or_create(user=user)
                return Response({"token": token.key})
            else:
                return Response({"detail": _('Social Auth Failed')}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class SendTempPasswordApi(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        baseURL = request.get_host()
        context = dict()
        serializer = TempPasswordSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = User.objects.get(email=serializer.data['email'])
                user.reset_pass_code = randomized_code(6)
                user.reset_pass_code_attemps = 0
                user.save()
                Mail.send_temp_password_email(user, user.reset_pass_code)
            except User.DoesNotExist:
                context['detail'] = _("User doesn't exist")
                return Response(context, status=status.HTTP_404_NOT_FOUND)
            context['detail'] = _(
                'Check your {} to reset the password').format(user.email)
            return Response(context, status=status.HTTP_200_OK)
        else:
            return Response({"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class AppVerifyCodeApi(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        context = dict()
        serializer = AppVerifyCodeApiSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = User.objects.get(email=serializer.data['email'])
                if user.reset_pass_code_attemps == -1 or user.reset_pass_code == None:
                    return Response(context, status=status.HTTP_404_NOT_FOUND)
                elif user.reset_pass_code_attemps >= 5:
                    context['detail'] = _(
                        "Too much trials, please generate new code.")
                    return Response(context, status=status.HTTP_400_BAD_REQUEST)
                else:
                    user.reset_pass_code_attemps += 1
                    user.save()
                    if user.reset_pass_code == serializer.data['code']:
                        context['detail'] = _("Correct code")
                        context['attemps'] = user.reset_pass_code_attemps
                    else:
                        context['detail'] = _("Wrong code")
                        context['attemps'] = user.reset_pass_code_attemps
                        return Response(context, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                context['detail'] = _("Wrong email")
                return Response(context, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response(context, status=status.HTTP_200_OK)


class ChangePasswordApi(APIView):

    def post(self, request, format=None):
        context = dict()
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if(user.check_password(serializer.data['old_password'])):
                user.set_password(serializer.data['new_password'])
                user.save()
                context['detail'] = "Password changed successfuly"
                return Response(context, status=status.HTTP_200_OK)
            else:
                context['detail'] = _("Wrong password")
                return Response(context, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response(context, status=status.HTTP_200_OK)


class RestPasswordApi(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        context = dict()
        serializer = RestPasswordSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = User.objects.get(email=serializer.data['email'])
                if user.reset_pass_code_attemps >= 5:
                    context['detail'] = _(
                        "Too much trials, please generate new code.")
                else:
                    user.reset_pass_code_attemps += 1
                    if user.reset_pass_code == serializer.data['code']:
                        user.set_password(serializer.data['new_password'])
                        user.reset_pass_code = None
                        user.email_verified = True
                        user.reset_pass_code_attemps = -1
                        context['detail'] = _("password reseted successfuly")
                    else:
                        context['detail'] = _("Wrong code")
                        context['attemps'] = user.reset_pass_code_attemps
                    user.save()
            except User.DoesNotExist:
                context['detail'] = _("Wrong email")
        else:
            return Response({"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response(context, status=status.HTTP_200_OK)


class EmailVerification(View):
    def get(self, request, email, code, *args, **kwargs):
        user = User.objects.get(email=email)
        if user:
            if user.email_verified and user.verify_mail_code == code:
                return render(request, "mail_verification_verified.html")
            # user = User.objects.get(verify_mail_code=code)
            if user.verify_mail_code == code:
                user.email_verified = True
                user.save()
                return render(request, "mail_verification_success.html")
        return render(request, "mail_verification_fail.html")


class Profile(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()

    def retrieve(self, request):
        serializer = GetProfileSerializer(request.user)
        # return Response({"profile": serializer.data}, status=status.HTTP_200_OK)
        return Response({"profile": 1}, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        serializer = UpdateProfileSerializer(
            request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            json_response = dict(serializer.data)
            return Response(json_response, status=status.HTTP_200_OK)
        else:
            return Response({"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        return super(Profile, self).retrieve(request, pk)


class OtherUserProfile(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, user_id, *args, **kwargs):
        try:
            serializer = GetProfileSerializer(User.objects.get(
                id=user_id), context={'user': request.user})
            return Response({"profile": serializer.data}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            context = dict()
            context['detail'] = _("User doesn't exist")
            return Response(context, status=status.HTTP_404_NOT_FOUND)


class MyBlockedUsersView(APIView):

    def get(self, request, format=None):
        serializer = BasicUserInfoSerializer(
            request.user.blocked_users.all(), many=True)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)


class BlockUnBlockUsers(APIView):

    def post(self, request, format=None):
        context = dict()
        user_id = request.data.get("user_id", "")
        if not user_id:
            context['user_id'] = _("This field is required.")
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        try:
            if request.user.blocked_users.filter(id=user_id).exists():
                request.user.blocked_users.remove(user_id)
                context['detail'] = _(
                    "User removed from your block list successfully.")
            else:
                user = User.objects.get(id=user_id)
                request.user.blocked_users.add(user_id)
                request.user.following_users.remove(user_id)
                user.following_users.remove(request.user)
                context['detail'] = _(
                    "User added to your block list successfully.")
            return Response(context, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            context['user_id'] = _("User does not exist.")
            return Response(context, status=status.HTTP_400_BAD_REQUEST)


class FollowUnFollowUsers(APIView):

    def post(self, request, format=None):
        context = dict()
        user_id = request.data.get("user_id", "")
        if not user_id:
            context['user_id'] = "This field is required."
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        if request.user.id is user_id:
            context['detail'] = _("Can't follow/unfollow yourself.")
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(id=user_id)
            if request.user.following_users.filter(id=user_id).exists():
                request.user.following_users.remove(user_id)
                context['detail'] = _("User removed from your follow list successfully.")
            else:
                if user in request.user.blockers.all() or user in request.user.blocked_users.all():
                    context['detail'] = _("Can't follow this user regarding the blocking.")
                    return Response(context, status=status.HTTP_400_BAD_REQUEST)
                else:
                    request.user.following_users.add(user_id)
                    create_and_push_notification(
                        request.user, NotificationTemplate.USER_FOLLOW, request.user, [user])
                    context['detail'] = _("User added to your follow list successfully.")
            context['followers_count'] = request.user.followers_count
            context['following_count'] = request.user.following_count
            return Response(context, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            context['user_id'] = _("User does not exist.")
            return Response(context, status=status.HTTP_400_BAD_REQUEST)


class FollowersView(APIView):

    def get(self, request, id=None, format=None):
        users = request.user.followers.all()
        serializer = BasicUserInfoSerializer(
            users, context={'user': request.user}, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MyFollowingUsersView(APIView):

    def get(self, request, format=None):
        users = request.user.following_users.all()
        serializer = BasicUserInfoSerializer(
            users, context={'user': request.user}, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LanguageView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, format=None):
        serializer = DefaultLanguageSerializer(
            Language.objects.all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
