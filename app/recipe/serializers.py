"""Serials for recipe APIs"""

from rest_framework import serializers
from core.models import Recipe, Tag, Ingredient  # noqa


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredients"""

    class Meta:
        model = Ingredient
        fields = ['id', 'name']
        read_only_fields = ['id']


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for tags"""
    tags = TagSerializer(many=True, required=False)
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link', 'tags', 'ingredients']
        read_only_fields = ['id']

    def _get_or_create_tags(self, tags, recipe):  # underscore in the beginning means it's internal only
        """Handle getting or creating tags as needed"""
        auth_user = self.context['request'].user  # context is the request payload of the view, this will get the user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(  # will not create duplicate tags in system
                user=auth_user,
                **tag,  # instead of name=tag['name'] use this in case there is future model fields
            )
            recipe.tags.add(tag_obj)  # connects the new created or founded tags to the objects

    def _get_or_create_ingredients(self, ingredients, recipe):
        """Handle getting or creating ingredients as needed"""
        auth_user = self.context['request'].user
        for ingredient in ingredients:
            ingredient_obj, created = Ingredient.objects.get_or_create(
                user=auth_user,
                **ingredient,
            )
            recipe.ingredients.add(ingredient_obj)

    def create(self, validated_data):
        """Create recipe with tags and ingredients custom logic """
        tags = validated_data.pop('tags', [])  # if tags exists in valid_data...remove it, if return empty list
        ingredients = validated_data.pop('ingredients', [])
        recipe = Recipe.objects.create(**validated_data)  # models expect data of the Recipe only (no tags, ingredients)
        self._get_or_create_tags(tags, recipe)
        self._get_or_create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):  # instance is the object that is getting update
        """Custom update logic for tags and ingredients"""
        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredients', None)

        if tags is not None:  # if the tags are empty list, empty list is not None then clear it. if None then keep it
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        if ingredients is not None:  # don't use if ingredients as it won't run if it's empty str or list as well.
            instance.ingredients.clear()
            self._get_or_create_ingredients(ingredients, instance)

        for attr, value in validated_data.items():  # update other fields normally.
            setattr(instance, attr, value)

        instance.save()
        return instance


class RecipeDetailSerializer(RecipeSerializer):
    """serializer for recipe detail view, is extension to base RecipeSerializer"""

    class Meta(RecipeSerializer.Meta):
        fields = None
        exclude = ['user']  # cannot be used with fields, also will take __all__ except the excluded list or tuple


class RecipeImageSerializer(serializers.ModelSerializer):
    """Serializer to upload image in recipes."""

    class Meta:
        model = Recipe
        fields = ['id', 'image']
        read_only_fields = ['id']
        extra_kwargs = {'image': {'required': 'true'}}  # the Value of the image is required, if there is image
