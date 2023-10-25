import django_filters
from django_filters import FilterSet, filters, rest_framework
from recipes.models import Ingredient, Recipe, Tag


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
        if self.request.user.is_authenticated:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def filter_author(self, queryset, name, value):
        if value:
            return queryset.filter(author__pk=int(value))
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_authenticated:
            return queryset.filter(shopping_carts__user=self.request.user)
        return queryset


class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name')

    class Meta:
        model = Ingredient
        fields = ('name', )
