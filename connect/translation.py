from modeltranslation.translator import translator, TranslationOptions
from .models import *

class CategoryTranslationOptions(TranslationOptions):
    fields = ('name',)

translator.register(Category, CategoryTranslationOptions)