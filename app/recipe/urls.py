"""URL mapping for recipe app"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('recipes', views.RecipeViewsSet)  # <-- auto generates URL for the recipe ViewSet
router.register('tags', views.TagViewSet)
router.register('ingredients', views.IngredientViewSet)

app_name = 'recipe'  # used in reverse lookup of urls

urlpatterns = [
    path('', include(router.urls)),  # need include() to handle router
]
