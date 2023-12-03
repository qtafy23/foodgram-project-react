from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Subscribe, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username', 'pk', 'email', 'password', 'first_name', 'last_name',
    )
    fields = (
        ('is_active',),
        ('username', 'email',),
        ('first_name', 'last_name', 'password'),
    )
    required_fields = ('username', 'email',
                       'first_name', 'last_name', 'password')
    search_fields = ('username', 'email',)
    list_filter = ('is_active', 'first_name', 'email',)
    save_on_top = True


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'author')
    list_editable = ('user', 'author')
    empty_value_display = '-пусто-'
