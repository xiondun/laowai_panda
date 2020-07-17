from django.core.mail import send_mail
from dbmail import send_db_mail
from accounts.models import User
from django.contrib.sites.models import Site
from django.conf import settings
from crequest.middleware import CrequestMiddleware

class Mail(object):
    """
    Send class has all mails templates needed in laowai_Panda software
    """

    @staticmethod
    def send_temp_password_email(user, temp_code):
        try:
            app_name = 'Laowai Panda'
            request = CrequestMiddleware.get_request()
            base_url = ("{0}://{1}").format(request.scheme , request._get_raw_host())
            send_db_mail(
                'reset-passcode',
                user.email,
                {
                    'app_name':app_name,
                    'base_url':base_url,
                    'temp_code': temp_code,
                },
                user = user,
            )
        except:
            pass
    

    @staticmethod
    def verify_email(user, verification_url):
        try:
            app_name = 'Laowai Panda'
            request = CrequestMiddleware.get_request()
            base_url = ("{0}://{1}").format(request.scheme , request._get_raw_host())
            send_db_mail(
                'verify-mail',
                user.email,
                {
                    'base_url':base_url,
                    'app_name': app_name,
                    'verification_url': verification_url,
                },
                user = user,
            )
        except:
            pass

    @staticmethod
    def send_report_question(reporter_user, question_url):
        try:
            app_name = 'Laowai Panda'
            request = CrequestMiddleware.get_request()
            base_url = ("{0}://{1}").format(request.scheme , request._get_raw_host())
            send_db_mail(
                'laowai_panda-question-report',
                settings.SYS_ADMINS,
                {
                    'app_name':app_name,
                    'base_url':base_url,
                    'email': reporter_user.email,
                    'username': reporter_user.username,
                    'question_url': question_url,
                },
            )
        except:
            pass