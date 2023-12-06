from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    RegexValidator)
from django.db import models

from users.models import User


class Tag(models.Model):
    """Модель тега."""

    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Название тега'
    )
    color = models.CharField(
        max_length=7,
        null=True,
        validators=[
            RegexValidator(
                '^#([a-fA-F0-9]{6})',
                message='Поле должно содержать HEX-код выбранного цвета.'
            )
        ],
        verbose_name='Цвет тега'
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name='Слаг тега'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиента."""

    name = models.CharField(
        max_length=200,
        db_index=True,
        verbose_name='Название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Еденица измерения'
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='uq_name_measurement_unit'
            )
        ]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта."""

    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        help_text='Выберите тэги',
        verbose_name='Тэги рецепта'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=False,
        related_name='recipes',
        verbose_name='Автор рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингредиенты рецепта',
        help_text='Выберите ингредиенты'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта'
    )
    text = models.TextField(
        verbose_name='Описание рецепта'
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                1,
                message='Время приготовления должно быть больше 1 минуты!'
            ),
            MaxValueValidator(
                720,
                message='Время приготовления должно быть меньше 720 минут!'
            )
        ],
        verbose_name='Время приготовления',
        help_text='Время приготовления в минутах!'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )
    image = models.ImageField(
        upload_to='media/',
        help_text='Прикрепите изображение',
        verbose_name='Изображение рецепта'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['text', 'author'],
                name='uq_text_author'
            )
        ]

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Модель для связи рецепта и ингредиента."""

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Ингредиент'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Рецепт'
    )
    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                1,
                message='Количество должно быть больше 1!'
            ),
            MaxValueValidator(
                10000,
                message='Количество должно быть меньше 10000!'
            )
        ],
        verbose_name='Количество'
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте',
        verbose_name_plural = 'Ингредиенты в рецепте'

    def __str__(self):
        return f'{self.recipe} + {self.ingredient}'


class FavoriteList(models.Model):
    """Модель для добавления рецептов в избранное."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self):
        return f'Рецепты из избранных {self.user}'


class ShoppingList(models.Model):
    """Модель для добавления рецептов в корзину."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shoppings',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shoppings',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='uq_user_recipe'
            ),
        ]

    def __str__(self):
        return f'Рецепты из корзины покупок {self.user}'
