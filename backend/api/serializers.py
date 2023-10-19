from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, Tag)
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from users.models import Follow, User


class CustomDjoserUsersGetSerializer(UserSerializer):
    '''
    Serializer to djoser in /users/ and /users/me/.
    '''

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username',
                  'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        request = self.context['request']
        if request is None or request.user.is_anonymous:
            return False
        return Follow.objects.filter(reader=request.user,
                                     author=obj).exists()


class CustomDjoserUserCreateSerializer(UserCreateSerializer):
    '''
    Serializer for djoser in registration of users.
    '''

    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'username',
                  'first_name', 'last_name', 'password')


class UserSerializer(serializers.ModelSerializer):
    '''
    Serializer for model of User.
    '''

    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username',
                  'first_name', 'last_name',
                  'password', 'is_subscribed',
                  'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        request = self.context['request']
        if request.user.is_anonymous:
            return False
        return Follow.objects.filter(reader=request.user, author=obj).exists()

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class UserListSerializer(UserSerializer):
    '''
    Serializer for author in favorite.
    '''
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name',
                  'is_subscribed', 'recipes',
                  'recipes_count')
        read_only_fields = ('email', 'username',
                            'first_name', 'last_name',
                            'is_subscribed', 'recipes',
                            'recipes_count')

    def get_recipes(self, obj):
        request = self.context['request']
        recipes = Recipe.objects.filter(author=obj)
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        return FavoriteRecipeSerializer(recipes,
                                        many=True,
                                        context={'request': request}).data


class TagSerializer(serializers.ModelSerializer):
    '''
    Serilaizer for /tags/.
    '''

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    '''
    Serilaizer for /ingredients/.
    '''
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientRecipeGetSerializer(serializers.ModelSerializer):
    '''
    Serializer for watching recipe.
    '''

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'amount', 'measurement_unit')


class IngredientRecipePostSerializer(serializers.ModelSerializer):
    '''
    Serializer for creating recipe.
    '''

    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')


class RecipeListSerializer(serializers.ModelSerializer):
    '''
    Serializer for watching created recipe.
    '''

    author = CustomDjoserUsersGetSerializer(read_only=True)
    image = Base64ImageField(required=False, allow_null=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'name', 'image',
                  'text', 'ingredients', 'tags',
                  'cooking_time', 'is_favorited',
                  'is_in_shopping_cart')

    def get_ingredients(self, obj):
        ingredients = IngredientInRecipe.objects.filter(recipe=obj)
        return IngredientRecipeGetSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        request = self.context['request']
        if request.user.is_anonymous:
            return False
        return Favorite.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context['request']
        if request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(user=request.user,
                                           recipe=obj).exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    '''
    Serializer for working with recipes.
    '''

    ingredients = IngredientRecipePostSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    image = Base64ImageField(required=False)
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = ('name', 'image', 'text',
                  'ingredients', 'tags', 'cooking_time')

    def validate_tags(self, value):
        if not value:
            raise serializers.ValidationError('No tags.')
        tag_list = []
        for tag in value:
            if tag in tag_list:
                raise serializers.ValidationError('Already used.')
            tag_list.append(tag)
        return tag_list

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError('No ingredients.')
        ingredients_list = []
        for ingredient in value:
            if ingredient['id'] in ingredients_list:
                raise serializers.ValidationError(
                    'This ingredient already used.')
            if ingredient['amount'] == 0:
                raise serializers.ValidationError(
                    'Amount should be more than 0.')
            ingredients_list.append(ingredient['id'])
        return value

    def validate_cooking_time(self, value):
        if value == 0:
            raise serializers.ValidationError('Time should be more than 0.')
        return value

    def create(self, validated_data):
        request = self.context.get('request')
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=request.user, **validated_data)
        recipe.tags.set(tags)
        ingredients_list = []
        for ingredient in ingredients:
            current_ingredient = Ingredient.objects.get(id=ingredient['id'])
            amount = ingredient['amount']
            ingredient_recipe = IngredientInRecipe(
                recipe=recipe,
                ingredient=current_ingredient,
                amount=amount
            )
            ingredients_list.append(ingredient_recipe)
        IngredientInRecipe.objects.bulk_create(ingredients_list)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.tags.clear()
        instance.tags.set(tags)
        IngredientInRecipe.objects.filter(recipe=instance).delete()
        super().update(instance, validated_data)
        ingredients_list = []
        for ingredient in ingredients:
            current_ingredient = Ingredient.objects.get(id=ingredient['id'])
            amount = ingredient['amount']
            ingredient_recipe = IngredientInRecipe(
                recipe=instance,
                ingredient=current_ingredient,
                amount=amount
            )
            ingredients_list.append(ingredient_recipe)
        IngredientInRecipe.objects.bulk_create(ingredients_list)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        request = self.context['request']
        return RecipeListSerializer(instance,
                                    context={'request': request}).data


class SubscribeSerializer(serializers.ModelSerializer):
    '''
    Serializer for working with subscribe.
    '''

    class Meta:
        model = Follow
        fields = ('reader', 'author')
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('reader', 'author'),
                message='You already subscribe.'
            )
        ]

    def validate(self, data):
        if data['reader'] == data['author']:
            raise serializers.ValidationError(
                'It is impossible to subscribe to yourself.'
            )
        return data

    def to_representation(self, instance):
        request = self.context['request']
        return UserListSerializer(instance.author,
                                  context={'request': request}).data


class FavoriteRecipeSerializer(RecipeListSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteSerializer(serializers.ModelSerializer):
    '''
    Serializer for working with favorite.
    '''
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Recipe already in favorite.'
            )
        ]

    def to_representation(self, instance):
        request = self.context['request']
        return FavoriteRecipeSerializer(instance.recipe,
                                        context={'request': request}).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    '''
    Serilizer for shopping cart.
    '''
    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe'),
                message='Recipe already in shopping cart.'
            )
        ]

    def to_representation(self, instance):
        request = self.context['request']
        return FavoriteRecipeSerializer(instance.recipe,
                                        context={'request': request}).data
