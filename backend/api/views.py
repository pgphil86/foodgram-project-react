
from django.db.models import Sum
from django.http import HttpResponse
from django_filters import rest_framework
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.filters import IngredientFilter, RecipeFilter
from api.permissions import AuthorPermissions
from api.serializers import (FavoriteSerializer, IngredientInRecipe,
                             IngredientSerializer, RecipeCreateSerializer,
                             RecipeSerializer, ShoppingCartSerializer,
                             SubscribeSerializer, TagSerializer,
                             UserPasswordSerializer, UserSerializer)
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
        queryset = User.objects.filter(following__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(
            page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[permissions.IsAuthenticated])
    def subscribe(self, request, pk):
        serializer = SubscribeSerializer(
            data={'id': pk},
            context={'request': request, 'method': request.method})
        serializer.is_valid(raise_exception=True)
        if request.method == 'POST':
            subscribe = serializer.save()
            return Response(SubscribeSerializer(subscribe, context={
                'request': request,
                'recipes_limit': request.query_params.get('recipes_limit')
            }).data, status=status.HTTP_201_CREATED)
        follow = Follow.objects.get(user=request.user, author_id=pk)
        if not follow:
            return Response({'errors': 'No subscribe.'},
                            status=status.HTTP_400_BAD_REQUEST)
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (rest_framework.DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


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
    def favorite(self, request, pk):
        serializer = FavoriteSerializer(
            data={'id': pk},
            context={'request': request, 'method': request.method})
        serializer.is_valid(raise_exception=True)
        if request.method == 'POST':
            favorite = serializer.save()
            return Response(FavoriteSerializer(favorite, context={
                'request': request,
            }).data, status=status.HTTP_201_CREATED)
        favorite = Favorite.objects.get(user=request.user,
                                        recipe_id=pk)
        if not favorite:
            return Response({'error': 'Recipe not found'},
                            status=status.HTTP_404_NOT_FOUND)
        else:
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[permissions.IsAuthenticated])
    def shopping_cart(self, request, pk):
        serializer = ShoppingCartSerializer(
            data={'id': pk},
            context={'request': request, 'method': request.method})
        serializer.is_valid(raise_exception=True)
        if request.method == 'POST':
            shopping_list = serializer.save()
            return Response(ShoppingCartSerializer(shopping_list, context={
                'request': request,
            }).data, status=status.HTTP_201_CREATED)
        shopping_cart = ShoppingCart.objects.get(user=request.user,
                                                 recipe_id=pk)
        if not shopping_cart:
            return Response({'message': 'Object not found.'},
                            status=status.HTTP_404_NOT_FOUND)
        else:
            shopping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['GET'],
            permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
        shopping_cart = ShoppingCart.objects.filter(
            user=self.request.user
        )
        cart_list = IngredientInRecipe.objects.filter(
            recipe__in=[item.recipe.id for item in shopping_cart]
        ).values(
            'ingredient'
        ).annotate(
            amount=Sum('amount')
        )
        list_text = []
        for item in cart_list:
            ingredient = Ingredient.objects.get(pk=item['ingredient'])
            amount = item['amount']
            list_text += (
                f'{ingredient.name}, {amount}, {ingredient.measurement_unit}\n'
            )
        response = HttpResponse(list_text, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename=shopping_list.txt'
        )
        return response
