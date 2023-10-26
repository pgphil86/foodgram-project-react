import io

from django.db.models import Q, Sum
from django.http import HttpResponse
from django_filters import rest_framework
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.filters import IngredientFilter, RecipeFilter
from api.permissions import AuthorPermissions
from api.serializers import (FavoriteSerializer, IngredientSerializer,
                             RecipeCreateSerializer, RecipeSerializer,
                             ShoppingCartSerializer, SubscribeSerializer,
                             TagSerializer, UserPasswordSerializer,
                             UserSerializer)
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from users.models import Follow, User


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)
        return super().retrieve(request)

    @action(detail=False, methods=['GET'],
            permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        return Response(UserSerializer(request.user, context={
            'request': request}).data)

    @action(detail=False, methods=['POST'],
            permission_classes=[permissions.IsAuthenticated])
    def set_password(self, request):
        serializer = UserPasswordSerializer(data=request.data, context={
            'request': request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['GET'],
            permission_classes=[permissions.IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(following__user=user)
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[permissions.IsAuthenticated])
    def subscribe(self, request, **kwargs):
        author = get_object_or_404(User, id=kwargs['id'])
        user = request.user
        if request.method == 'POST':
            serializer = SubscribeSerializer(
                data={'user': user.id, 'author': author.id},
                context={'request': request})
            serializer.is_valid(raise_exception=True)
            Follow.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        subscribe = Follow.objects.filter(user=user, author=author)
        if not subscribe:
            return Response({'errors': 'No subscribe.'},
                            status=status.HTTP_400_BAD_REQUEST)
        subscribe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filterset_class = IngredientFilter
    pagination_class = None
    permission_classes = (permissions.AllowAny, )
    search_fields = ('^name',)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all().order_by('-id')
    serializer_class = RecipeSerializer
    filter_backends = (rest_framework.DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def create(self, request):
        self.permission_classes = (permissions.IsAuthenticated,
                                   AuthorPermissions,)
        self.check_permissions(request)
        serializer = RecipeCreateSerializer(data=request.data,
                                            context={'request': request})
        serializer.is_valid(raise_exception=True)
        recipe = serializer.save()
        return Response(RecipeSerializer(
            recipe, context={'request': request}
        ).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk, *args, **kwargs):
        self.permission_classes = (permissions.IsAuthenticated,
                                   AuthorPermissions,)
        self.check_permissions(request)
        obj = get_object_or_404(Recipe, pk=pk)
        self.check_object_permissions(request, obj)
        serializer = RecipeCreateSerializer(obj, data=request.data,
                                            context={'request': request})
        serializer.is_valid(raise_exception=True)
        recipe = serializer.save()
        return Response(
            RecipeSerializer(recipe, context={'request': request}).data)

    def destroy(self, request, pk, *args, **kwargs):
        self.permission_classes = (permissions.IsAuthenticated,
                                   AuthorPermissions,)
        self.check_permissions(request)
        obj = get_object_or_404(Recipe, pk=pk)
        self.check_object_permissions(request, obj)
        return super().destroy(request)

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        user = request.user
        if request.method == 'POST':
            serializer = FavoriteSerializer(
                data={'user': user.id, 'recipe': recipe.id})
            serializer.is_valid(raise_exception=True)
            Favorite.objects.create(user=user, recipe=recipe)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)

        favorite = Favorite.objects.filter(user=user.id, recipe=recipe.id)
        if not favorite:
            return Response({'errors': 'Recipe not in favorite.'},
                            status=status.HTTP_400_BAD_REQUEST)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[permissions.IsAuthenticated])
    def shopping_cart(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        user = request.user
        if request.method == 'POST':
            serializer = ShoppingCartSerializer(
                data={'user': user.id, 'recipe': recipe.id},
                context={'request': request})
            serializer.is_valid(raise_exception=True)
            ShoppingCart.objects.create(user=user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_200_OK)
        shopping_cart = ShoppingCart.objects.filter(
            recipe=recipe.id, user=user.id)
        if not shopping_cart:
            return Response({'errors': 'Object not found.'},
                            status=status.HTTP_400_BAD_REQUEST)
        shopping_cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['GET'],
            permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
        recipes_id = ShoppingCart.objects.filter(
            user=request.user).values_list('recipe__pk', flat=True)
        amounts = Recipe.objects.filter(
            id__in=recipes_id
        ).annotate(
            quantity=Sum(
                'ingredients__link_of_ingredients__amount',
                filter=Q(
                    ingredients__link_of_ingredients__recipe_id__in=recipes_id
                )
            )
        ).distinct().values_list(
            'quantity', 'link_of_ingredients__ingredient__name',
            'link_of_ingredients__ingredient__measurement_unit'
        )
        list = ''
        for i in amounts:
            list += f'{amounts[i][1]} ({amounts[i][2]}) -- {amounts[i][0]}\n'
        text = io.BytesIO()
        with io.TextIOWrapper(text, encoding="utf-8", write_through=True) as f:
            f.write(list)
            response = HttpResponse(text.getvalue(), content_type='text/plain')
            response['Content-Disposition'] = 'attachment; filename=shop.txt'
            return response
