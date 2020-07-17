from django.contrib import admin
from .models import *
from solo.admin import SingletonModelAdmin
from django import forms
from django.contrib import messages


# Register your models here.

class PostInline(admin.TabularInline):
    model = Post
    extra = 0
    readonly_fields = ('text', 'type',
                       'media', 'channel', 'liked_by_users',)

    def has_add_permission(self, request):
        return False


class PostAdmin(admin.ModelAdmin):
    list_filter = ('type', 'show_in', 'channel')
    search_fields = ('text',)
    list_display = ('text', 'type', 'show_in', 'channel', 'likes')
    readonly_fields = ('liked_by_users',)

    def save_model(self, request, obj, form, change):
        error = ""
        if obj.type == Post.TXT_IMAGE and obj.media == "":
            error = "Please upload an image to the media."
        elif obj.type == Post.TXT_VIDEO and obj.media == "" and not obj.youko_link:
            error = "Please upload an video to the media or add youko url."
        else:
            super().save_model(request, obj, form, change)
            return obj

        self.message_user(request, error, messages.ERROR)
        return obj


class ChannelAdmin(admin.ModelAdmin):
    inlines = [PostInline, ]
    list_display = ('name',)


admin.site.register(RevyoumeClubSetting, SingletonModelAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Channel, ChannelAdmin)
