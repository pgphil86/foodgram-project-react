from django.contrib import admin
from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, Tag)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('measurement_unit', 'name',)
    list_filter = ('name',)


class RecipeIngredientInLine(admin.TabularInline):
    model = IngredientInRecipe
    min_num = 1
    list_display = ('id', 'amount', 'ingredient', 'recipe')
    list_editable = ('amount', 'ingredient', 'recipe')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientInLine,)
    list_display = ('add_favorites', 'author', 'name',)
    list_filter = ('author', 'name', 'tags',)

    @staticmethod
    def add_favorites(obj):
        return obj.favorites.count()


admin.site.register(Favorite)
admin.site.register(IngredientInRecipe)
admin.site.register(Tag)
admin.site.register(ShoppingCart)
