from colorfield.fields import ColorField
from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    RegexValidator)
from django.db import models

from users.models import User

MINIMUM_QUANTITY = 1
MAXIMUM_QUANTITY = 32000


class Ingredient(models.Model):
    """
    Model of work with ingredients.
    """

    name = models.CharField(
        max_length=200,
        verbose_name='Name of ingredient',
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Measurement unit',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('measurement_unit', 'name',),
                name='unique_ingredient'
            )
        ]
        ordering = ('name',)
        verbose_name = 'Ingredient',
        verbose_name_plural = 'Ingredients'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    """
    Tags model.
    """

    color = ColorField(
        max_length=7,
        unique=True,
        verbose_name='Color',
        validators=(
            RegexValidator(
                regex=r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
                message='Need only HEX.'
            ),
        )
    )
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Name of tag'
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name='Slug'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """
    Model of work with recipes.
    """
    REGEX = '.*[a-яA-ЯЁё].*'

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Author'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Cooking time',
        validators=(MinValueValidator(MINIMUM_QUANTITY),
                    MaxValueValidator(MAXIMUM_QUANTITY))
    )
    image = models.ImageField(
        verbose_name='Image',
        upload_to='recipes/media'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        through_fields=('recipe', 'ingredient'),
        verbose_name='Ingredients'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Name of dish',
        validators=[RegexValidator(
            regex=REGEX,
            message='There are no letters in the name.')]
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Publications date'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Tags'
    )
    text = models.TextField(
        verbose_name='Description'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'

    def __str__(self):
        return f'{self.name}, {self.author}'


class IngredientInRecipe(models.Model):
    """
    Model of united ingredients and recipes.
    """

    amount = models.PositiveSmallIntegerField(
        validators=((MinValueValidator(MINIMUM_QUANTITY),
                    MaxValueValidator(MAXIMUM_QUANTITY))),
        verbose_name='Ingredient quantity'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ingredient',
        related_name='ingridientinrecipe'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Recipe',
        related_name='ingridientinrecipe'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredientinrecipe'
            ),
        ]
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'

    def __str__(self):
        return f'{self.amount} {self.ingredient} {self.recipe}'


class Favorite(models.Model):
    """
    Model of work with favorite recipes.
    """

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Recipe',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='User',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite_recipe'
            ),
        ]
        verbose_name = 'Favorite'
        verbose_name_plural = 'Favorites'

    def __str__(self):
        return f'{self.user.username} add {self.recipe.name}.'


class ShoppingCart(models.Model):
    """
    Model work with users shopping list.
    """

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_list',
        verbose_name='Recipe',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_list',
        verbose_name='User',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_list'
            ),
        ]
        verbose_name = 'Shopping list'
        verbose_name_plural = 'Shopping lists'

    def __str__(self):
        return (f'{self.user.username} add'
                f'{self.recipe.name} to shopping list.')
