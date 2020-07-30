import datetime
import os
import threading

import requests
from django.shortcuts import render
from django.db.models import Count
from django.core.paginator import Paginator
from django.utils.translation import ugettext as _
from django.http import Http404
from django.urls import reverse
from django.db.models import Avg, Q
from django.views import generic, View
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from alphabet_detector import AlphabetDetector
from helpers._mails import Mail
from notification.funcs import create_and_push_notification
from notification.models import NotificationTemplate
from .serializers import *
from .models import *
import json
import time
import base64
import pytz
from datetime import datetime


def queryset_paginator(queryset, page, num=10):
    paginator = Paginator(queryset, num)
    number = int(paginator.num_pages)
    if int(page) > number:
        raise Http404()
    queryset = paginator.page(page)
    return queryset, number


class GetTimeZoneInfo(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, format=None):
        if 'HTTP_X_FORWARDED_FOR' in request.META.keys():
            ip = request.META['HTTP_X_FORWARDED_FOR']
        else:
            ip = request.META['REMOTE_ADDR']
        time_zone_info = self.getIpTimeZone(ip)
        return Response({"data": json.loads(time_zone_info), "ip": ip}, status=status.HTTP_200_OK)

    def getIpTimeZone(self, ip):
        try:
            ips = [ip]
            url = 'http://ip-api.com/batch'
            res = requests.post(url, json.dumps(ips))
            if res.status_code == 200:
                return res.text
            else:
                return False
        except Exception:
            return False


class Search(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, format=None):
        if 'HTTP_X_FORWARDED_FOR' in request.META.keys():
            ip = request.META['HTTP_X_FORWARDED_FOR']
        else:
            ip = request.META['REMOTE_ADDR']
        request_query_string = (request.GET).dict()
        page = request.GET.get("page", 1)
        questions = Question.objects.all()
        try:
            text_arr = request_query_string['text'].split()
            search_text_arr = []
            for text in text_arr:
                lower = text.lower()
                capitalized = text.capitalize()
                search_text_arr.append(lower)
                search_text_arr.append(capitalized)
            if len(search_text_arr) > 0:
                condition = Q(text__contains=search_text_arr[0])
                condition1 = Q(replies__reply__contains=search_text_arr[0])
                for string in search_text_arr[1:]:
                    condition |= Q(text__contains=string)
                    condition1 |= Q(replies__reply__contains=string)
                questions = questions.filter(condition | condition1).distinct()
        except:
            pass
        # exclude the blocked user data
        if request.user.id:
            questions = questions.exclude(
                owner__in=request.user.blocked_users.all())
        queryset, number = queryset_paginator(
            questions.distinct().order_by('-created'), page)
        serializer = QuestionSerializer(
            queryset, many=True, context={'user': request.user})

        # threading.Thread(target=self.getRemoteImg,args=(serializer.data,)).start()
        return Response({"data": self.changeToLocalTime(serializer.data, ip), "pages_num": number}, status=status.HTTP_200_OK)
        # return Response({"data": serializer.data, "pages_num": number}, status=status.HTTP_200_OK)
        # return Response({"data": "", "pages_num": ""}, status=status.HTTP_200_OK)

    def changeToLocalTime(self, data, ip):
        for i, d in enumerate(data):
            data[i]['timestamp'] = self.timestampToLocaltime(data[i]['timestamp'], ip)
        return data

    def timestampToLocaltime(self, timestamp, ip):
        dt_str = self.time_to_str(timestamp)
        t_timezone = self.getIpTimeZone(ip)
        return self.__datetime_to_utc_epoch(dt_str, 'UTC', t_timezone)

    def time_to_str(self, shijian):
        try:
            return time.strftime(r"%Y-%m-%d %H:%M:%S", time.localtime(shijian))
        except Exception:
            return '时间转换错误'

    def __datetime_to_utc_epoch(self, dt_str, l_timezone, t_timezone, time_format="%Y-%m-%d %H:%M:%S"):
        """
        __datetime_to_utc_epoch("2019-07-14 11:23:36", "UTC", "Asia/Tokyo", "%Y-%m-%d %H:%M:%S")
        """
        local_tz = pytz.timezone(l_timezone)
        target_tz = pytz.timezone(t_timezone)
        dt = datetime.strptime(dt_str, time_format)
        dt = local_tz.localize(dt)
        t_dt_str = str(dt.astimezone(tz=target_tz))[0:19]
        # print("UTC 时间: {0}".format(t_dt_str))
        epoch = time.strptime(t_dt_str, "%Y-%m-%d %H:%M:%S")
        return epoch

    def getIpTimeZone(self, ip):
        try:
            ips = [ip]
            url = 'http://ip-api.com/batch'
            res = requests.post(url, json.dumps(ips))
            if res.status_code == 200:
                time_zone_info = json.loads(res.text)
                return time_zone_info['timezone']
            else:
                return False
        except Exception:
            return False

    def getRemoteImg(self, data):
        for items in data:
            for item in items['images']:
                if (not os.path.exists(os.getcwd() + item['image'])):
                    downloadImgUrlList = [
                        'http://45.13.199.57' + item['image'],  # 德國
                        'http://121.40.208.210' + item['image'],  # 杭州
                    ]
                    for imgUrl in downloadImgUrlList:
                        threading.Thread(target=self.down_load_img, args=(imgUrl, item['image'])).start()

    def mkdir(self, path):
        path = path.strip()
        path = path.rstrip("\\")
        isExists = os.path.exists(path)
        if not isExists:
            os.makedirs(path)
            return True
        else:
            return False

    def down_load_img(self, imgUrl, imgName):
        save_path = '/'.join(imgName.split('/')[1:-1])
        imgName = imgName.split('/')[-1]
        self.mkdir(save_path)
        save_img_path = save_path + '/' + str(imgName)
        # print(save_img_path)
        try:
            header = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
            }
            res = requests.get(imgUrl, headers=header, timeout=120)
            if res.status_code != 200:
                print(imgUrl, '下载网络错误：', res.status_code)
                return False
            with open(save_img_path, 'wb') as f:
                f.write(res.content)
            print(imgUrl, '下载成功')
            return save_img_path
        except Exception as e:
            print(imgUrl, "下载图片错误XXXX", e)
            try:
                os.remove(save_img_path)
            except Exception as e:
                pass
            return False


class FollowedUsersQuestions(APIView):

    def get(self, request, format=None):
        request_query_string = (request.GET).dict()
        page = request.GET.get("page", 1)
        questions = Question.objects.filter(
            owner__in=request.user.following_users.all())
        # exclude the blocked user data
        if request.user.id:
            questions = questions.exclude(
                owner__in=request.user.blocked_users.all())
        queryset, number = queryset_paginator(
            questions.distinct().order_by('-created'), page)
        serializer = QuestionSerializer(
            queryset, many=True, context={'user': request.user})
        return Response({"data": serializer.data, "pages_num": number}, status=status.HTTP_200_OK)


class Filter(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, format=None):
        required_key_list = ['lang_id', 'category_id']
        request_query_string = (request.GET).dict()
        for key in required_key_list:
            if not key in list(request_query_string):
                return Response({'detail': key + _(' is required')}, status=status.HTTP_400_BAD_REQUEST)
        page = request.GET.get("page", 1)
        questions = Question.objects.all()
        if not request_query_string['category_id'] == "-1":
            questions = questions.filter(
                category_id=request_query_string['category_id'])

        if not request_query_string['lang_id'] == '-1':
            questions = questions.filter(
                language=request_query_string['lang_id'])

        try:
            questions = questions.filter(
                text__contains=request_query_string['text'])
        except:
            pass

        # exclude the blocked user data
        if request.user.id:
            questions = questions.exclude(
                owner__in=request.user.blocked_users.all())

            if (request_query_string.get("is_following", None)):
                if (request_query_string["is_following"] == "True"):
                    questions = questions.filter(
                        owner__in=request.user.following_users.all())
                else:
                    return Response({"detail": 'Enter vaild format'}, status=status.HTTP_400_BAD_REQUEST)

        queryset, number = queryset_paginator(
            questions.distinct().order_by('-created'), page)
        serializer = QuestionSerializer(
            queryset, many=True, context={'user': request.user})
        return Response({"data": serializer.data, "pages_num": number}, status=status.HTTP_200_OK)


class CategoriesView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, format=None):
        serializer = CategorySerializer(
            Category.objects.all().order_by('-order'), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OtherUserFavQuestionsView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, user_id, *args, **kwargs):
        try:
            user = User.objects.get(id=user_id)
            if not user.show_my_followup_questions:
                return Response({}, status=status.HTTP_404_NOT_FOUND)
            page = request.GET.get("page", 1)
            queryset, number = queryset_paginator(
                user.my_fav_questions.order_by('-id').all(), page)
            serializer = QuestionSerializer(
                queryset, many=True, context={'user': user})
            return Response({"data": serializer.data, "pages_num": number}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            context = dict()
            context['detail'] = _("User doesn't exist")
            return Response(context, status=status.HTTP_404_NOT_FOUND)


class OtherUserQuestionsView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, user_id, *args, **kwargs):
        try:
            user = User.objects.get(id=user_id)
            if not user.show_my_questions:
                return Response({}, status=status.HTTP_404_NOT_FOUND)
            page = request.GET.get("page", 1)
            queryset, number = queryset_paginator(
                user.my_questions.order_by('-id').all(), page)
            serializer = QuestionSerializer(
                queryset, many=True, context={'user': user})
            return Response({"data": serializer.data, "pages_num": number}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            context = dict()
            context['detail'] = _("User doesn't exist")
            return Response(context, status=status.HTTP_404_NOT_FOUND)


class MyFavQuestionsView(APIView):

    def get(self, request, format=None):
        page = request.GET.get("page", 1)
        queryset, number = queryset_paginator(
            request.user.my_fav_questions.exclude(owner__in=request.user.blockers.all()).exclude(owner__in=request.user.blocked_users.all()).order_by('-id').all(), page)
        serializer = QuestionSerializer(
            queryset, many=True, context={'user': request.user})
        return Response({"data": serializer.data, "pages_num": number}, status=status.HTTP_200_OK)


class MyQuestionsView(APIView):

    def get(self, request, format=None):
        page = request.GET.get("page", 1)
        queryset, number = queryset_paginator(
            request.user.my_questions.order_by('-id').all(), page)
        serializer = QuestionSerializer(
            queryset, many=True, context={'user': request.user})
        return Response({"data": serializer.data, "pages_num": number}, status=status.HTTP_200_OK)


class FavUnfavQuestion(APIView):

    def post(self, request, format=None):
        context = dict()
        question_id = request.data.get("question_id", "")
        if not question_id:
            context['question_id'] = _("This field is required.")
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        try:
            question = Question.objects.get(id=question_id)
            if request.user.my_fav_questions.filter(id=question_id).exists():
                request.user.my_fav_questions.remove(question_id)
                context['detail'] = _(
                    "Question removed from your favourite list successfully.")
            else:
                request.user.my_fav_questions.add(question_id)
                create_and_push_notification(
                    question, NotificationTemplate.QUESTION_FAV, request.user, [question.owner])
                context['detail'] = _(
                    "Question added to your favourite list successfully.")
            return Response(context, status=status.HTTP_200_OK)
        except Question.DoesNotExist:
            context['question_id'] = _("Question does not exist.")
            return Response(context, status=status.HTTP_400_BAD_REQUEST)


class LikeUnlikeQuestion(APIView):

    def post(self, request, format=None):
        context = dict()
        question_id = request.data.get("question_id", "")
        if not question_id:
            context['question_id'] = _("This field is required.")
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        try:
            question = Question.objects.get(id=question_id)
            if question.liked_by_users.filter(id=request.user.id).exists():
                question.liked_by_users.remove(request.user.id)
                question.owner.likes -= 1
                context['detail'] = _("Unlike successfully.")
            else:
                question.liked_by_users.add(request.user.id)
                create_and_push_notification(
                    question, NotificationTemplate.QUESTION_LIKED, request.user, [question.owner])
                question.owner.likes += 1
                context['detail'] = _("Like successfully.")
            question.owner.save()
            return Response(context, status=status.HTTP_200_OK)
        except Question.DoesNotExist:
            context['question_id'] = _("Question does not exist.")
            return Response(context, status=status.HTTP_400_BAD_REQUEST)


class UserNotifyShareQuestion(APIView):

    def post(self, request, format=None):
        context = dict()
        question_id = request.data.get("question_id", "")
        if not question_id:
            context['question_id'] = _("This field is required.")
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        try:
            question = Question.objects.get(id=question_id)
            create_and_push_notification(
                question, NotificationTemplate.QUESTION_SHARED, request.user, [question.owner])
            context['detail'] = _("notify successfully.")
            return Response(context, status=status.HTTP_200_OK)
        except Question.DoesNotExist:
            context['question_id'] = _("Question does not exist.")
            return Response(context, status=status.HTTP_400_BAD_REQUEST)


class UsefulUnusefulReply(APIView):

    def post(self, request, format=None):
        context = dict()
        reply_id = request.data.get("reply_id", "")
        if not reply_id:
            context['reply_id'] = _("This field is required.")
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        try:
            reply = QuestionReply.objects.get(id=reply_id)
            if reply.useful_by_users.filter(id=request.user.id).exists():
                reply.useful_by_users.remove(request.user.id)
                reply.user.usefuls -= 1
                context['detail'] = _("Unuseful successfully.")
            else:
                reply.useful_by_users.add(request.user.id)
                extra_data = {
                    "is_parent": reply.is_parent,
                    "question_id": reply.question.id,
                    "reply_id": reply.id if reply.is_parent else reply.parent_reply.id,
                }
                create_and_push_notification(
                    reply, NotificationTemplate.COMMENT_USEFUL, request.user, [reply.user], extra_data)
                reply.user.usefuls += 1
                context['detail'] = _("Useful successfully.")
            reply.user.save()
            return Response(context, status=status.HTTP_200_OK)
        except QuestionReply.DoesNotExist:
            context['reply_id'] = _("QuestionReply does not exist.")
            return Response(context, status=status.HTTP_400_BAD_REQUEST)


class ReportUnreportQuestion(APIView):

    def post(self, request, format=None):
        context = dict()
        question_id = request.data.get("question_id", "")
        if not question_id:
            context['question_id'] = _("This field is required.")
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        try:
            if request.user.my_reported_questions.filter(id=question_id).exists():
                request.user.my_reported_questions.remove(question_id)
                context['detail'] = _("Question report is cancelled.")
            else:
                request.user.my_reported_questions.add(question_id)
                question_url = request.build_absolute_uri(
                    reverse('admin:%s_%s_change' % ('connect', 'question'), args=(question_id,)))
                Mail.send_report_question(request.user, question_url)
                context['detail'] = _("Your report is submitted successfully.")
            return Response(context, status=status.HTTP_200_OK)
        except Question.DoesNotExist:
            context['question_id'] = _("Question does not exist.")
            return Response(context, status=status.HTTP_400_BAD_REQUEST)


class Questions(APIView):

    def get_permissions(self):
        if self.request.method == 'GET':
            self.permission_classes = (permissions.AllowAny,)
        else:
            self.permission_classes = (permissions.IsAuthenticated,)
        return super(Questions, self).get_permissions()

    def get(self, request, id, *args, **kwargs):
        try:
            serializer = QuestionSerializer(Question.objects.get(
                id=id), context={'user': request.user})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Question.DoesNotExist:
            context = dict()
            context['detail'] = _("Question doesn't exist")
            return Response(context, status=status.HTTP_404_NOT_FOUND)

    # def post(self, request, format=None):
    #     serializer = QuestionSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.validated_data['owner'] = request.user
    #
    #         question = serializer.save()
    #         arr = []
    #         try:
    #             for image in request.data['images']:
    #                 image["question_id"] = question.id
    #                 arr.append(image)
    #             request.data['images'] = arr
    #             images_serializer = QuestionImageSerializer(
    #                 data=request.data['images'], many=True)
    #             if images_serializer.is_valid():
    #                 images_serializer.save()
    #                 serializer.data['images'] = images_serializer.data
    #         except KeyError:
    #             pass
    #         create_and_push_notification(
    #             question, NotificationTemplate.FOLLOWED_USER_ADDED_NEW_QUESTION, request.user, request.user.followers.all())
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        # print(request.META)
        with open('/var/www/api/request_post_body.log', 'a', encoding='utf-8') as f:  # a是追加，w覆盖
            f.write(str(request._request.body, encoding='utf-8') + "\n")
        serializer = QuestionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['owner'] = request.user

            question = serializer.save()
            try:
                for image in request.data['images']:
                    QuestionImage.objects.create(image=image['image'], question_id=question.id)

            except Exception as e:
                print(e)

            create_and_push_notification(
                question, NotificationTemplate.FOLLOWED_USER_ADDED_NEW_QUESTION, request.user,
                request.user.followers.all())
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id, format=None):
        context = dict()
        try:
            question = request.user.my_questions.get(id=id)
            question.delete()
            context['detail'] = ("Question removed successfully.")
            return Response(context, status=status.HTTP_200_OK)
        except Question.DoesNotExist:
            context['error'] = _("Question does not exist.")
            return Response(context, status=status.HTTP_400_BAD_REQUEST)


class UploadFileBase64(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        try:
            # with open('/var/www/api/request_body.log', 'a', encoding='utf-8') as f:  # a是追加，w覆盖
            #     f.write(str(request._request.body, encoding='utf-8') + "\n")
            file_strs = json.loads(request._request.body)['file']
            # file_strs = request._request.POST.get('file')
            ext = file_strs.split(',')[0].split('/')[-1].split(';')[0]
            img_strs = file_strs.split(',')[-1]
            folder = datetime.datetime.now().strftime("%Y%m%d")
            save_path = 'media/' + folder
            self.mkdir = self.mkdir(save_path)
            # print('file_strs: ' + file_strs)
            file_name = str(int(time.time() * 1000)) + '.' + ext  # 构造文件名以及文件路径
            with open(save_path + '/' + file_name, 'wb') as f:
                f.write(base64.b64decode(img_strs))
            ret_data = {
                'code': 200,
                'data': {'file_name': folder + '/' + file_name},
                'msg': 'success'
            }
        except Exception as e:
            with open('/var/www/api/error.log', 'a', encoding='utf-8') as f:  # a是追加，w覆盖
                f.write(str(e) + "\n")
            ret_data = {
                'code': 500,
                'data': '',
                'msg': '内部错误，' + str(e)
            }
        return Response(ret_data)

    def mkdir(self, path):
        path = path.strip()
        path = path.rstrip("\\")
        isExists = os.path.exists(path)
        if not isExists:
            os.makedirs(path)
            print(path + ' 创建成功')
            return True


class RequestInfo(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, format=None):
        if 'HTTP_X_FORWARDED_FOR' in request.META.keys():
            ip = request.META['HTTP_X_FORWARDED_FOR']
        else:
            ip = request.META['REMOTE_ADDR']
        print('用户的请求ip是', ip)

        # 此处编写的代码会在每个请求处理视图之后被调用。
        ret_data = {
            'code': 200,
            'data': ip,
            'msg': ''
        }
        return Response(ret_data)


class Reply(APIView):
    def get_object(self, request, id):
        try:
            return request.user.replies.get(id=id)
        except QuestionReply.DoesNotExist:
            raise Http404

    def post(self, request, format=None):
        serializer = QuestionReplySerializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['user'] = request.user
            if not serializer.validated_data.get('question', None):
                serializer.validated_data['question'] = serializer.validated_data['parent_reply'].question
            reply = serializer.save()
            extra_data = {
                "is_parent": reply.is_parent,
                "question_id": reply.question.id,
                "reply_id": reply.id if reply.is_parent else reply.parent_reply.id,
            }

            if reply.is_parent:
                create_and_push_notification(
                    reply, NotificationTemplate.QUESTION_COMMENT, request.user, [reply.question.owner], extra_data)
            else:
                create_and_push_notification(
                    reply, NotificationTemplate.COMMENT_REPLY, request.user, [reply.parent_reply.user], extra_data)

            create_and_push_notification(
                reply, NotificationTemplate.FOLLOWED_QUESTION_COMMENT, request.user, reply.question.fav_by_users.all(), extra_data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id, format=None):
        reply = self.get_object(request, id)
        serializer = QuestionReplySerializer(
            reply, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id, format=None):
        reply = self.get_object(request, id)
        if reply.is_parent:
            reply.replies.all().delete()
        reply.delete()
        context = dict()
        context['detail'] = _("Reply removed successfully.")
        return Response(context, status=status.HTTP_200_OK)


class QuestionReplies(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, id, format=None):
        context = dict()
        page = request.GET.get("page", 1)
        replies = QuestionReply.objects.filter(question_id=id, parent_reply__isnull=True).annotate(count=Count(
            'useful_by_users')).order_by('-id').order_by('-count')
        if request.user.id:
            replies = replies.exclude(
                user_id__in=request.user.blocked_users.all())
            replies = replies.exclude(user_id__in=request.user.blockers.all())
        queryset, number = queryset_paginator(replies, page)
        serializer = QuestionReplySerializer(
            queryset, many=True, context={'user': request.user})
        return Response({"data": serializer.data, "pages_num": number}, status=status.HTTP_200_OK)


class ReplyReplies(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, id, format=None):
        context = dict()
        page = request.GET.get("page", 1)
        replies = QuestionReply.objects.filter(parent_reply_id=id).annotate(count=Count(
            'useful_by_users')).order_by('-id').order_by('-count')
        if request.user.id:
            replies = replies.exclude(
                user_id__in=request.user.blocked_users.all())
            replies = replies.exclude(user_id__in=request.user.blockers.all())
        queryset, number = queryset_paginator(replies, page)
        serializer = QuestionReplySerializer(
            queryset, many=True, context={'user': request.user})
        return Response({"data": serializer.data, "pages_num": number}, status=status.HTTP_200_OK)


class ShareQuestion(generic.TemplateView):
    template_name = 'share_question.html'

    def get_context_data(self, **kwargs):
        try:
            question = Question.objects.get(
                pk=self.kwargs.get('pk'))
            replies = question.replies.filter(parent_reply__isnull=True).annotate(count=Count(
                'useful_by_users')).order_by('-id').order_by('-count')
        except:
            question = replies = None
        context = super(ShareQuestion, self).get_context_data(**kwargs)
        ctx = {'question': question, 'replies': replies}
        context.update(ctx)
        return context
