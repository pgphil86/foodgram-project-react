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
        author_id = request.user.subscribes.all().values_list(
            'author_id', flat=True)
        self.queryset = User.objects.filter(id__in=author_id)
        self.serializer_class = SubscribeSerializer
        return super().list(request)

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
        try:
            Follow.objects.get(user=request.user, author_id=pk)
        except Follow.DoesNotExist:
            return Response({'error': 'Object not found'},
                            status=status.HTTP_404_NOT_FOUND)
        else:
            Follow.objects.get(user=request.user, author_id=pk).delete()
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
        try:
            Favorite.objects.get(user=request.user, recipe_id=pk)
        except Favorite.DoesNotExist:
            return Response({'error': 'Recipe not found'},
                            status=status.HTTP_404_NOT_FOUND)
        else:
            Favorite.objects.get(user=request.user, recipe_id=pk).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[permissions.IsAuthenticated])
    def shopping_cart(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])

        if request.method == 'POST':
            serializer = ShoppingCartSerializer(recipe, data=request.data,
                                                context={'request': request})
            serializer.is_valid(raise_exception=True)
            if not ShoppingCart.objects.filter(user=request.user,
                                               recipe=recipe).exists():
                ShoppingCart.objects.create(user=request.user, recipe=recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response({'errors': 'Recipe already in list.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            get_object_or_404(ShoppingCart, user=request.user,
                              recipe=recipe).delete()
            return Response(
                {'detail': 'Recipe was delete.'},
                status=status.HTTP_204_NO_CONTENT
            )

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
