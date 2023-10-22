from django_filters.rest_framework import FilterSet, filters
from recipes.models import Ingredient, Recipe, Tag
from rest_framework.filters import SearchFilter


class RecipeFilter(FilterSet):
    author__name = filters.CharFilter()
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug'
    )
    is_favorited = filters.BooleanFilter(
        method='get_favorite', field_name='is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_shopping', field_name='is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_favorited', 'is_in_shopping_cart']

    def get_favorite(self, queryset, field_name, value):
        if value:
            return queryset.filter(favorite__user=self.request.user)
        return queryset

    def get_shopping(self, queryset, field_name, value):
        if value:
            return queryset.filter(shopping__user=self.request.user)
        return queryset


class IngredientFilter(SearchFilter):
    search_param = 'name'

    class Meta:
        model = Ingredient
        fields = ('name',)
