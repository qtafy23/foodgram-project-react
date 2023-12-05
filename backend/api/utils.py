from django.db.models import Sum

from recipes.models import RecipeIngredient


def create_shoping_list(shopping_cart):
    recipes = shopping_cart.values_list('recipe_id', flat=True)
    buy_list = RecipeIngredient.objects.filter(
        recipe__in=recipes
    ).values(
        'ingredient__name',
        'ingredient__measurement_unit',
    ).annotate(
        amount=Sum('amount')
    )
    buy_list_text = 'Foodgram\nСписок покупок:\n'
    for item in buy_list:
        amount = item['amount']
        name = item['ingredient__name']
        measurement_unit = item['ingredient__measurement_unit']
        buy_list_text += (
            f'{name}, {amount} '
            f'{measurement_unit}\n'
        )
    return buy_list_text
