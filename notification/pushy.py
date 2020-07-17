import json
from urllib.request import Request, urlopen
from urllib import parse, error, request


class PushyAPI:

    @staticmethod
    def sendPushNotification(data):
        apiKey = '9cb2d5be17b039b6b4f236589bb51490074d28d16f178159e4c6d7ca59bcee26'
        response = {
            "success": True,
            "results": "Deliverd"
        }
        pushy_url = 'https://api.pushy.me/push?api_key=' + apiKey
        data = json.dumps(data).encode('utf8')

        try:
            req = request.Request(pushy_url, data=data, headers={
                'content-type': 'application/json'})
            res = json.loads(request.urlopen(req).read())
            if not res['success']:
               response["success"] = False
               response["results"] = res['error']

        except Exception as e:
            response["success"] = False
            response["results"] = str(e)
        except error.HTTPError as e:
            response["success"] = False
            response["results"] = "Pushy API returned HTTP error " + \
                str(e.code) + ": " + e.read()
        return response
