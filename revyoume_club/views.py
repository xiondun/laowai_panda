import datetime
import json
import time

import requests
from django.shortcuts import render
from django.views import generic, View
from django.core.paginator import Paginator
from django.utils.translation import ugettext as _
from django.http import Http404

from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from revyoume_club.models import RevyoumeClubSetting
from .serializers import *
from .models import *
from connect.models import Question
from notification.models import Notification


def queryset_paginator(queryset, page, num=10):
    paginator = Paginator(queryset, num)
    number = int(paginator.num_pages)
    if int(page) > number:
        raise Http404()
    queryset = paginator.page(page)
    return queryset, number


class GetRevSettingView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, format=None):
        context = dict()
        setting = RevyoumeClubSetting.get_solo()
        context['revyoume_club_link'] = setting.revyoume_club_link
        context['revyoume_club_enabled'] = setting.revyoume_club_enabled
        return Response(context, status=status.HTTP_200_OK)

class ChangeTime(object):
    def changeToLocalTime(self, data, ip):
        t_timezone = self.getIpTimeZone(ip)
        if t_timezone == 'CN':
            delta_time = 8 * 3600
        elif t_timezone == 'EG':
            delta_time = 2 * 3600
        else:
            delta_time = 0

        for i, d in enumerate(data):
            data[i]['timestamp_orgin'] = data[i]['timestamp']
            data[i]['timestamp'] += delta_time
            data[i]['created'] = time.strftime(r"%Y-%m-%dT%H:%M:%S.000000Z", time.localtime(data[i]['timestamp']))
            # data[i]['text'] += ' hellow world'
            # data[i]['timestamp'] = self.str_to_time(self.time_to_str(data[i]['timestamp']))
            data[i]['timezone'] = t_timezone
            data[i]['ip'] = ip
        return data

    def getIpTimeZone(self, ip):
        try:
            ips = [ip]
            url = 'http://ip-api.com/batch'
            res = requests.post(url, json.dumps(ips))
            if res.status_code == 200:
                time_zone_info = json.loads(res.text)
                return time_zone_info[0]['countryCode']
            else:
                return False
        except Exception:
            return False

class PostsView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, format=None):
        if 'HTTP_X_FORWARDED_FOR' in request.META.keys():
            ip = request.META['HTTP_X_FORWARDED_FOR']
        else:
            ip = request.META['REMOTE_ADDR']
        page = request.GET.get("page", 1)
        posts = Post.objects.all()
        queryset, number = queryset_paginator(
            posts.order_by('-modified'), page)
        serializer = PostSerializer(
            queryset, many=True, context={'user': request.user})
        for index,value  in enumerate(serializer.data):
            serializer.data[index]['media_link'] = serializer.data[index]['youko_url'] if serializer.data[index]['youko_url'] and serializer.data[index]['youko_url'] != 'None' and str(serializer.data[index]['youko_url']).replace('https://player.youku.com/embed/','') != 'n' else serializer.data[index]['media_link']

            if serializer.data[index]['media'] == None and 'player.youku.com' not in serializer.data[index]['media_link'] and 'weibo.com' not in serializer.data[index]['youko_url'] and 'weibocdn.com' not in serializer.data[index]['youko_url'] :
                serializer.data[index]['media_link'] = '/media/posts/media/loading6.jpg'

        # return Response({"data": ChangeTime().changeToLocalTime(serializer.data,ip), "pages_num": number}, status=status.HTTP_200_OK)
        return Response({"data": serializer.data, "pages_num": number}, status=status.HTTP_200_OK)


class PostsHaveUpdatesView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, posts_timestamp, followers_questions_timestamp, notifications_timestamp, format=None):
        context = dict()
        context['new_revume_posts'] = False
        context['new_followers_questions_count'] = 0
        context['new_notifications_count'] = 0
        posts_date = datetime.datetime.fromtimestamp(float(posts_timestamp))
        followers_questions_date = datetime.datetime.fromtimestamp(
            float(followers_questions_timestamp))
        notifications_date = datetime.datetime.fromtimestamp(
            float(notifications_timestamp))
        if Post.objects.filter(modified__gt=posts_date).exists():
            context['new_revume_posts'] = True
        if request.user.is_authenticated:
            new_followers_questions_count = Question.objects.filter(
                modified__gt=followers_questions_date, owner__in=request.user.following_users.all()).count()
            if new_followers_questions_count > 0:
                context['new_followers_questions_count'] = new_followers_questions_count
            new_notifications_count = Notification.objects.filter(seen=False,
                modified__gt=notifications_date, to_user=request.user).count()
            if new_notifications_count > 0:
                context['new_notifications_count'] = new_notifications_count
        return Response(context, status=status.HTTP_200_OK)


class ChannelPostsView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, format=None):
        channel_id = request.GET.get("channel_id", None)
        if not channel_id:
            return Response({'detail': _(' channel_id is required')}, status=status.HTTP_400_BAD_REQUEST)
        post_query = Post.objects.all()
        post_query = post_query.filter(channel_id=channel_id)
        show_in = request.GET.get("show_in", None)
        if show_in:
            post_query = post_query.filter(show_in=show_in)
        post_query = post_query.order_by('-created')
        page = request.GET.get("page", 1)
        queryset, number = queryset_paginator(post_query, page)
        serializer = PostSerializer(
            queryset, many=True, context={'user': request.user})
        return Response({"data": serializer.data, "pages_num": number}, status=status.HTTP_200_OK)


class LikeUnlikePost(APIView):

    def post(self, request, format=None):
        context = dict()
        post_id = request.data.get("post_id", "")
        if not post_id:
            context['post_id'] = _("This field is required.")
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        try:
            post = Post.objects.get(id=post_id)
            if post.liked_by_users.filter(id=request.user.id).exists():
                post.liked_by_users.remove(request.user.id)
                context['detail'] = _("Unlike successfully.")
            else:
                post.liked_by_users.add(request.user.id)
                context['detail'] = _("Like successfully.")
            return Response(context, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            context['post_id'] = _("Post does not exist.")
            return Response(context, status=status.HTTP_400_BAD_REQUEST)


class SharePost(generic.TemplateView):
    template_name = 'share_post.html'

    def get_context_data(self, **kwargs):
        try:
            post = Post.objects.get(pk=self.kwargs.get('pk'))
        except:
            raise Http404
        context = super(SharePost, self).get_context_data(**kwargs)
        ctx = {'post': post}
        context.update(ctx)
        return context

class MediaPost(generic.TemplateView):
    template_name = 'post_media.html'

    def get_context_data(self, **kwargs):
        try:
            post = Post.objects.get(pk=self.kwargs.get('pk'))
        except:
            raise Http404
        context = super(MediaPost, self).get_context_data(**kwargs)
        ctx = {'post': post}
        context.update(ctx)
        return context
