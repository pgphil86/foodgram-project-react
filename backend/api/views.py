from api.filters import IngredientFilter
from api.pagination import StandartPaginator
from api.permissions import AdminOrReadOnly, AuthorOrReadOnly
from api.serializers import (FavoriteSerializer, IngredientSerializer,
                             RecipeCreateSerializer, RecipeListSerializer,
                             ShoppingCartSerializer, TagSerializer)
from django.db.models import F, Sum
from django.shortcuts import HttpResponse, get_object_or_404
from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, Tag)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response


class TagViewSet(viewsets.ModelViewSet):
    '''
    Viewset for model Tags.
    '''

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminOrReadOnly,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    '''
    Viewset for model Ingredients.
    '''

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientFilter,)
    permission_classes = (AllowAny,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    '''
    Viewset for watching recipes.
    '''

    queryset = Recipe.objects.all()
    filter_backends = (AuthorOrReadOnly,)
    http_method_names = ['get', 'post', 'patch', 'delete']
    pagination_class = StandartPaginator
    lookup_field = 'username'

    def get_serializer_class(self):
        if self.action in ('list', 'retrive'):
            return RecipeListSerializer
        return RecipeCreateSerializer

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, **kwargs):
        '''
        Add recipe in favorite.
        '''

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
            return Response({'errors': 'Recipe is not favorite.'},
                            status=status.HTTP_400_BAD_REQUEST)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        '''
        Watching shopping cart.
        '''

        items = IngredientInRecipe.objects.select_related('recipe',
                                                          'ingredient')
        items = items.filter(recipe__shopping_carts__user=request.user).all()
        shopping_cart = items.values('ingredient__name',
                                     'ingredient__measurement_unit').annotate(
            name=F('ingredient__name'),
            units=F('ingredient__measurement_unit'),
            amount=Sum('amount')
        ).order_by('-amount')
        text = '\n'.join(
            [f"{item.get('name')} ({item.get('units')}) - {item.get('amount')}"
             for item in shopping_cart]
        )
        filename = 'foodgram_shopping_cart.txt'
        response = HttpResponse(text, content_type='text/plan')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, **kwargs):
        '''
        Working under recipe.
        '''

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
            return Response({'errors': 'Recipe is not in shopping cart.'},
                            status=status.HTTP_400_BAD_REQUEST)
        shopping_cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
