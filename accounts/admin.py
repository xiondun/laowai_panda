from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin
# Register your models here.


class MyUserAdmin(UserAdmin):
    list_filter = ('is_superuser', 'account_verified','email_verified','social_type')
    list_display = ('name','username', 'email','email_verified')
    fieldsets = (
        ('Personal Information', {
         'fields': ('name','email','social_type','username','photo','default_lang','account_verified','is_superuser','is_staff', 'email_verified',)}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
            (None, {
                'classes': ('wide',),
                'fields': ('name','username', 'password1', 'password2', 'email')}
            ),
        )


class LanguageModelAdmin(admin.ModelAdmin):
    model = Language
    list_display = ('name', 'short_name', 'lang_name',)

admin.site.register(Language, LanguageModelAdmin)

admin.site.register(User, MyUserAdmin)
