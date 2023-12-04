from django.contrib import admin

from .models import (
    Tag,
    Ingredient,
    Recipe,
    RecipeIngredient,
    FavoriteList,
    ShoppingList
)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug',)
    search_fields = ('name', 'color')
    save_on_top = True


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)
    list_filter = ('name',)
    save_on_top = True


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    readonly_fields = ('added_in_favorites',)
    inlines = (RecipeIngredientInline,)
    search_fields = ('name', 'author__username', 'tags__slug',)
    list_filter = ('name', 'author__username', 'tags__slug')
    save_on_top = True

    @admin.display(description='Количество в избранных')
    def added_in_favorites(self, obj):
        return obj.favorites.count()

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related(
            'author'
        ).prefetch_related('ingredients', 'tags')


@admin.register(FavoriteList)
class FavoriteListAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related(
          'recipe', 'user'
        )


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related(
          'recipe', 'user'
        )
