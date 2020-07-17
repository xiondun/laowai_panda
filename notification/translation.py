from modeltranslation.translator import translator, TranslationOptions

from .models import *


class NotificationTranslation(TranslationOptions):
    fields = ('message','title')


class NotificationTemplateTranslation(TranslationOptions):
    fields = ('message_template','title_template')


translator.register(NotificationTemplate, NotificationTemplateTranslation)
translator.register(Notification, NotificationTranslation)
