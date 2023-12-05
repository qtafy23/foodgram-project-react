from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import FavoriteList, Ingredient, Recipe, ShoppingList, Tag
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from users.models import Subscribe, User
from .filters import IngredientFilter, RecipeFilter
from .mixins import (CreateListRetrieveViewSetMixin,
                     ModelMultiSerializerViewSetMixin)
from .paginations import CustomPaginator
from .permissions import IsAuthorOrReadOnly
from .serializers import (FavoriteListSerializer, IngredientSerializer,
                          RecipeCreateSerializer, RecipeSerializer,
                          SetPasswordSerializer, ShoppingListSerializer,
                          SubscribeSerializer, SubscriptionSerializer,
                          TagSerializer, UserCreateSerializer,
                          UserReadSerializer)
from .utils import create_shoping_list


class UserViewSet(CreateListRetrieveViewSetMixin):
    """Вьюсет для работы с пользователями."""

    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    pagination_class = CustomPaginator
    serializer_class = UserCreateSerializer
    serializer_classes = {
        'list': UserReadSerializer,
        'retrieve': UserReadSerializer,
        'set_password': SetPasswordSerializer,
        'subscribe': SubscribeSerializer,
    }

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request):
        """Информация о своем аккаунте."""
        serializer = UserReadSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=('post',),
        serializer_class=SetPasswordSerializer,
        permission_classes=(IsAuthenticated,),
    )
    def set_password(self, request):
        """Страница смены пароля."""
        user = request.user
        serializer = self.get_serializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        old_password = serializer.validated_data.get('current_password')
        new_password = serializer.validated_data.get('new_password')
        if not user.check_password(old_password):
            return Response(
                'Неверный пароль',
                status=status.HTTP_400_BAD_REQUEST
            )
        user.set_password(new_password)
        user.save()
        return Response(
            'Пароль успешно изменен', status=status.HTTP_204_NO_CONTENT
        )

    @action(
        methods=('get',),
        detail=False,
        serializer_class=SubscriptionSerializer,
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        """Просмотр подписок пользователя."""
        paginated_queryset = self.paginate_queryset(
            User.objects.filter(
                subscribing__user=self.request.user
            ).annotate(recipes_count=Count('recipes'))
        )
        serializer = self.serializer_class(
            paginated_queryset,
            context={'request': request},
            many=True
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=('post', 'delete'),
        serializer_class=SubscribeSerializer,
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, pk=None):
        """Добавление и удаление подписок пользователя."""
        user = request.user
        author = get_object_or_404(User, pk=pk)

        if request.method == 'POST':
            serializer = SubscribeSerializer(
                author, data=request.data, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            Subscribe.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            deleted_tuple = Subscribe.objects.filter(
                user=user, author=author
            ).delete()
            if deleted_tuple[0] == 0:
                return Response(status=status.HTTP_404_NOT_FOUND)
            return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для тега."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для ингредиента."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(ModelMultiSerializerViewSetMixin):
    """Вьюсет для рецепта."""

    queryset = Recipe.objects.select_related(
        'author'
    ).prefetch_related('ingredients', 'tags')
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = CustomPaginator
    serializer_class = RecipeCreateSerializer
    serializer_classes = {
        'list': RecipeSerializer,
        'retrieve': RecipeSerializer,
        'favorite': FavoriteListSerializer,
        'shopping_cart': ShoppingListSerializer,
    }

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=('POST',),
        permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        """Добавление рецепта в избранное."""
        context = {'request': request}
        recipe = get_object_or_404(Recipe, id=pk)
        data = {
            'user': request.user.id,
            'recipe': recipe.id
        }
        serializer = FavoriteListSerializer(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def destroy_favorite(self, request, pk):
        """Удаление рецепта из избранного."""
        deleted_tuple = FavoriteList.objects.filter(
            user=request.user, recipe=pk
        ).delete()
        if deleted_tuple[0] == 0:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=('post', 'delete',),
        serializer_class=ShoppingListSerializer,
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk=None):
        """Добавление/удаление рецепта из корзины."""
        if self.request.method == 'POST':
            return self.add_recipe_to_cart(request, pk)
        elif self.request.method == 'DELETE':
            return self.remove_recipe_from_cart(request, pk)

    def add_recipe_to_cart(self, request, pk):
        serializer = self.get_serializer(
            data=request.data,
            context={'request': request, 'recipe_id': pk}
        )
        serializer.is_valid(raise_exception=True)
        response_data = serializer.save(id=pk)
        return Response(
            {'message': 'Рецепт успешно добавлен в список покупок',
             'data': response_data},
            status=status.HTTP_201_CREATED
        )

    def remove_recipe_from_cart(self, request, pk):
        ShoppingList.objects.filter(user=request.user, recipe=pk).delete()

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        """Скачивание списка покупок."""
        shopping_cart = ShoppingList.objects.filter(user=self.request.user)
        buy_list_text = create_shoping_list(shopping_cart)
        response = HttpResponse(buy_list_text, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename=shopping-list.txt'
        )
        return response
