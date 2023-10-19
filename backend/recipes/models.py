from colorfield.fields import ColorField
from django.conf import settings
from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    RegexValidator)
from django.db import models
from users.models import User


class Ingredient(models.Model):
    '''
    Model of work with ingredients.
    '''

    measurement_unit = models.CharField(
        max_length=settings.SHORT_FIELD_LENGTH,
        verbose_name='Measurement unit',
    )
    name = models.CharField(
        max_length=settings.TITLE_LENGTH,
        unique=True,
        verbose_name='Name of ingredient',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'measurement_unit',),
                name='unique_ingredient'
            )
        ]
        ordering = ('name',)
        verbose_name = 'Ingredient',
        verbose_name_plural = 'Ingredients'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    '''
    Tags model.
    '''

    color = ColorField(
        max_length=settings.SHORT_FIELD_LENGTH,
        unique=True,
        verbose_name='Color'
    )
    name = models.CharField(
        max_length=settings.SMALL_FIELD_LENGTH,
        unique=True,
        blank=False,
        null=False,
        verbose_name='Name of tag'
    )
    slug = models.SlugField(
        max_length=settings.SHORT_FIELD_LENGTH,
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
    '''
    Model of work with recipes.
    '''
    REGEX = '.*[a-яA-ЯЁё].*'

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Author'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Cooking time',
        default=1,
        validators=(MinValueValidator(settings.MIN_COOKING_TIME),
                    MaxValueValidator(settings.MAX_COOKING_TIME))
    )
    image = models.ImageField(
        verbose_name='Image',
        upload_to='recipes/media',
        blank=False
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        verbose_name='Ingredients'
    )
    name = models.CharField(
        max_length=settings.TITLE_LENGTH,
        null=False,
        blank=False,
        verbose_name='Name of dish',
        validators=[RegexValidator(
            regex=REGEX,
            message='There are no letters in the name.')]
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Publications date'
    )
    tags = models.ForeignKey(
        Tag,
        verbose_name='Tags',
        on_delete=models.CASCADE
    )
    text = models.TextField(
        verbose_name='Description',
        blank=False,
        null=False
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'

    def __str__(self):
        return f'{self.name}, {self.author}'


class IngredientInRecipe(models.Model):
    '''
    Model of united ingredients and recipes.
    '''

    amount = models.PositiveSmallIntegerField(
        default=0,
        validators=((MinValueValidator(settings.MIN_QUANTITY),
                    MaxValueValidator(settings.MAX_QUANTITY))),
        verbose_name='Ingredient quantity'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ingredient'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Recipe'
    )

    class Meta:
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'
        ordering = ('ingredient',)

    def __str__(self):
        return f'{self.amount} {self.ingredient} {self.recipe}'


class UserRecipeModel(models.Model):
    '''
    Model of abstract recipe.
    '''

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='User'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Recipe'
    )

    class Meta:
        abstract = True


class Favorite(UserRecipeModel):
    '''
    Model of work with favorite recipes.
    '''

    class Meta:
        default_related_name = 'favorite'
        verbose_name = 'Favorite'
        verbose_name_plural = 'Favorites'

    def __str__(self):
        return f'{self.user.username} add {self.recipe.name}.'


class ShoppingCart(UserRecipeModel):
    '''
    Model work with users shopping list.
    '''

    class Meta:
        default_related_name = 'shopping'
        verbose_name = 'Shopping list'
        verbose_name_plural = 'Shopping lists'

    def __str__(self):
        return (f'{self.user.username} add'
                f'{self.recipe.name} to shopping list.')
