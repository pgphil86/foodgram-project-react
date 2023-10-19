from django.contrib import admin
from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, Tag)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('measurement_unit', 'name',)
    list_filter = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('add_favorites', 'author', 'name',)
    list_filter = ('author', 'name', 'tags',)

    @staticmethod
    def add_favorites(obj):
        return obj.favorites.count()


admin.site.register(Favorite)
admin.site.register(IngredientInRecipe)
admin.site.register(Tag)
admin.site.register(ShoppingCart)
