import django_filters
from django_filters import FilterSet, filters, rest_framework
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag


class RecipeFilter(FilterSet):
    author = rest_framework.CharFilter(field_name='author__username',
                                       method='filter_author')
    is_favorited = rest_framework.BooleanFilter(field_name='favourites__user',
                                                method='filter_is_favorited')
    is_in_shopping_cart = rest_framework.BooleanFilter(
        field_name='shoppingcard__user', method='filter_is_in_shopping_cart')
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),)

    class Meta:
        model = Recipe
        fields = ('author', 'is_favorited', 'is_in_shopping_cart', 'tags',)

    def filter_is_favorited(self, queryset, name, value):
        request = self.request
        if value:
            recipe_pk_list = Favorite.objects.filter(
                user=request.user).values_list('recipe_id', flat=True)
            return queryset.filter(pk__in=recipe_pk_list)
        return queryset

    def filter_author(self, queryset, name, value):
        if value:
            return queryset.filter(author__pk=int(value))
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        request = self.request
        if value:
            recipe_pk_list = ShoppingCart.objects.filter(
                user=request.user).values_list('recipe__pk', flat=True)
            return queryset.filter(pk__in=recipe_pk_list)
        return queryset


class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name')

    class Meta:
        model = Ingredient
        fields = ('name', )
