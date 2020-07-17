from modeltranslation.translator import translator, TranslationOptions
from .models import *

class LanguageTranslationOptions(TranslationOptions):
    fields = ('name',)

translator.register(Language, LanguageTranslationOptions)