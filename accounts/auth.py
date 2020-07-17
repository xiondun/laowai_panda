
from laowai_panda import settings
import requests
import jwt
from datetime import timedelta
from django.utils import timezone
from wechat_django.models import WeChatApp
from wechatpy.exceptions import WeChatOAuthException
from django.core.files.base import ContentFile
import urllib.request
from django.http import JsonResponse
import json


def request_vpn(link):
    proxies = {'http': "socks5://myproxy:9191"}
    return requests.get(link, proxies=proxies)

class Auth(object):

    def facebook_auth(social_token, social_id):
        appLink = 'https://graph.facebook.com/oauth/access_token?client_id=' + settings.FACEBOOK_CLIENT_ID + \
            '&client_secret=' + settings.FACEBOOK_CLIENT_SECRET + \
            '&grant_type=client_credentials'
        appToken = request_vpn(appLink).json()['access_token']
        link = 'https://graph.facebook.com/debug_token?input_token=' + \
            social_token + '&access_token=' + appToken
        context = dict()
        try:
            userId = request_vpn(link).json()['data']['user_id']
            data = request_vpn('https://graph.facebook.com/v4.0/' +
                               userId + '?access_token=' + social_token).json()

            context['Valid'] = True
            try:
                email = data['email']
            except Exception:
                data['email'] = data['id']+'@laowaipanda.com'

            context['userdata'] = data
        except (ValueError, KeyError, TypeError) as error:
            context['Valid'] = False
        return context

    def wechat(social_token, social_id):

        initRes = requests.get('https://api.weixin.qq.com/sns/oauth2/access_token?appid=' + settings.WECHAT_APP_ID +
                               '&secret=' + settings.WECHAT_APP_SECRET + '&code=' + social_token + '&grant_type=authorization_code')
        jsonRes = json.loads(initRes.content)
        access_token = jsonRes['access_token']
        openid = jsonRes['openid']
        context = dict()
        try:
            finalRes = requests.get(
                'https://api.weixin.qq.com/sns/userinfo?access_token=' + access_token + '&openid=' + openid)

            jsonFinalRes = json.loads(finalRes.content)
            data = dict()
            data['name'] = jsonFinalRes['nickname']
            data['email'] = jsonFinalRes['unionid']+'@laowaipanda.com'

            # app = WeChatApp.objects.get_by_name("Laowai Panda")
            # user, data = app.auth(social_token)
            # user_data = app._oauth.get_user_info()
            # data['name'] = user_data['nickname']
            # data['email']= data['username'] = user_data['unionid']+'@laowaipanda.com'
            context['Valid'] = True
            try:
                data['image'] = ContentFile(urllib.request.urlopen(jsonFinalRes['headimgurl']).read())
            except Exception:
                data['image'] = None   
            context['userdata'] = data     
        except requests.exceptions.RequestException as errror:
            context['Valid'] = False   
        # except Exception as error:
        #         passUser
        #     context['Valid'] = True
        #     context['userdata'] = data
        # except (WeChatOAuthException) as error:
        #     context['Valid'] = False
        # except Exception as error:
        #     context['Valid'] = False
        # except (ValueError, KeyError, TypeError) as error:
        #     context['Valid'] = False
        return context

    def apple(social_token, social_id):
        appLink = 'https://appleid.apple.com/auth/token'

        headers = {
            'kid': settings.SOCIAL_AUTH_APPLE_KEY_ID
        }

        payload = {
            'iss': settings.SOCIAL_AUTH_APPLE_TEAM_ID,
            'iat': timezone.now(),
            'exp': timezone.now() + timedelta(days=180),
            'aud': 'https://appleid.apple.com',
            'sub': settings.CLIENT_ID,
        }

        client_secret = jwt.encode(
            payload,
            key=settings.SOCIAL_AUTH_APPLE_PRIVATE_KEY,
            algorithm='ES256',
            headers=headers
        ).decode("utf-8")

        headers = {'content-type': "application/x-www-form-urlencoded"}
        data = {
            'client_id': settings.CLIENT_ID,
            'client_secret': client_secret,
            'code': social_token,
            'grant_type': 'authorization_code',
        }

        context = dict()
        try:
            res = requests.post(appLink, data=data, headers=headers)
            response_dict = res.json()
            id_token = response_dict.get('id_token', None)

            response_data = {}
            if id_token:
                decoded = jwt.decode(id_token, '', verify=False)
                response_data.update(
                    {'email': decoded['email']}) if 'email' in decoded else None
                response_data.update(
                    {'uid': decoded['sub']}) if 'sub' in decoded else None
                context['Valid'] = True
                try:
                    email = response_data['email']
                except Exception:
                    response_data['email'] = response_data['uid'] + \
                        '@laowaipanda.com'

                context['userdata'] = response_data
            else:
                context['Valid'] = False
        except (ValueError, KeyError, TypeError) as error:
            context['Valid'] = False
        return context
