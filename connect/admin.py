from django.contrib import admin
from .models import *

from modeltranslation.admin import TranslationAdmin


class QuestionReplyInline(admin.TabularInline):
    fields = ('user', 'reply','comment_image')
    model = QuestionReply
    extra = 0
    readonly_fields = ('useful_by_users', 'question',)


class QuestionAdmin(admin.ModelAdmin):
    inlines = [QuestionReplyInline, ]

    class Media:
        css = {
            "all": ("css/fix_jet.css",)
        }

    list_filter = ('category', 'language')
    search_fields = ('text',)
    list_display = ('text', 'owner', 'category', 'likes',
                    'replies_count', 'reports', 'favourites')
    readonly_fields = ('fav_by_users', 'liked_by_users', 'reported_by_users',)


class CategoryModelAdmin(TranslationAdmin):
    model = Category
    list_display = ('name', 'color', 'order',)



admin.site.register(Category, CategoryModelAdmin)
admin.site.register(Question, QuestionAdmin)
