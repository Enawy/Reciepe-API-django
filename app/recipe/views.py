"""
Views for Recipe APIs
"""
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe  # noqa
from . import serializers


class RecipeViewsSet(viewsets.ModelViewSet):  # ModelViewSet works directly on a model
    """view for manage recipe APIs"""
    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve recipes list for auth user"""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """return serializer class for request."""
        if self.action == 'list':  # action list is defined automatically by the view set
            return serializers.RecipeSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new Recipe."""
        serializer.save(user=self.request.user)  # connect the recipe object to the auth user
