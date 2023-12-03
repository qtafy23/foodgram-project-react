from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Subscribe, User


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = (
        'is_active', 'username',
        'first_name', 'last_name', 'email',
    )
    fields = (
        ('is_active',),
        ('username', 'email',),
        ('first_name', 'last_name',),
    )
    fieldsets = []
    search_fields = ('username', 'email',)
    list_filter = ('is_active', 'first_name', 'email',)
    save_on_top = True


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'author')
    list_editable = ('user', 'author')
    empty_value_display = '-пусто-'
