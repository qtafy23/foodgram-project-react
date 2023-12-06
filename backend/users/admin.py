from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Subscribe, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'is_active', 'username',
        'first_name', 'last_name', 'email',
    )
    list_display_links = ('is_active', 'username', 'email')
    fields = (
        ('is_active',),
        ('username', 'email',),
        ('first_name', 'last_name',),
    )
    fieldsets = []
    search_fields = ('username', 'email', 'first_name', 'last_name',)
    save_on_top = True


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    list_display_links = ('user', 'author')
    empty_value_display = '-пусто-'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related(
            'user', 'author'
        )
