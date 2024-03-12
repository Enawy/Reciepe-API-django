"""
Views for Recipe APIs
"""
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter, OpenApiTypes

from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe, Tag, Ingredient  # noqa
from . import serializers


@extend_schema_view(  # updates swagger OpenAPI schema for documentation which extend the generated DRF-S
    list=extend_schema(  # define 'list' endpoints
        parameters=[  # define parameters than can be passed in the list
            OpenApiParameter(  # define parameter in the list api for the view
                'tags',  # param name
                OpenApiTypes.STR,  # param type is str, so it can accept separate strings using ','
                description='Comma Separated list of IDs to filter',
            ),
            OpenApiParameter(
                'ingredients',
                OpenApiTypes.STR,
                description='Comma Separated list of IDs to filter',
            )
        ]
    )
)
class RecipeViewsSet(viewsets.ModelViewSet):  # ModelViewSet works directly on a model
    """view for manage recipe APIs"""
    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def _params_to_ints(self, qs):
        """Convert list of strings to integers."""
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """Retrieve recipes list for auth user"""
        tags = self.request.query_params.get('tags')  # get json keys better in a comma separated list
        ingredients = self.request.query_params.get('ingredients')
        queryset = self.queryset
        if tags:
            tags_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tags_ids)
        if ingredients:
            ingredients_id = self._params_to_ints(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredients_id)

        return queryset.filter(user=self.request.user).order_by('-id').distinct()

    def get_serializer_class(self):
        """return serializer class for request."""
        if self.action == 'list':  # action list is defined automatically by the view set
            return serializers.RecipeSerializer
        elif self.action == 'upload_image':  # custom action
            return serializers.RecipeImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new Recipe."""
        serializer.save(user=self.request.user)  # connect the recipe object to the auth user

    @action(methods=['POST'], detail=True, url_path='upload-image')  # detail=true means the ID or PK of inst-endpoint
    def upload_image(self, request, pk=None):
        """upload an image to recipe"""
        recipe = self.get_object()  # uses pk to get instance of the request
        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'assigned_only',
                OpenApiTypes.INT, enum=[0, 1],  # enum gives integer option in the documentation
                description='filter by item assigned to recipes.',
            )
        ]
    )
)
class BaseRecipeAttrViewSet(mixins.UpdateModelMixin, mixins.ListModelMixin,
                            mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """Base ViewSet for recipe attributes like Tags and Ingredients"""

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """filter queryset to objects related authenticated user."""
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))  # zero is a default value
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(recipe__isnull=False)

        return queryset.filter(user=self.request.user).order_by('-name').distinct()


class TagViewSet(BaseRecipeAttrViewSet):
    """Manage Tags in the database"""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()  # list model mixin will edit the behaviour of list query set


class IngredientViewSet(BaseRecipeAttrViewSet):
    """Manage ingredients in the database"""
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()
