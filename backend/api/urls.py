from api.views import CustomTokenCreateView, IngredientViewSet, RecipeViewSet, TagViewSet, UserViewSet
from django.urls import include, path
from rest_framework.routers import DefaultRouter

app_name = 'api'

router = DefaultRouter()

router.register('users', UserViewSet, basename='users')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/token/login/', CustomTokenCreateView.as_view()),
    path('auth/', include('djoser.urls.authtoken')),
]
