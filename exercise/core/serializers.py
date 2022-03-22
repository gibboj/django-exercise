from rest_framework import serializers
from .models import Recipe, Ingredient


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredient model"""

    class Meta:
        model = Ingredient
        fields = [
            "name",
        ]


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipe model"""

    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = ["id", "name", "description", "ingredients"]
        read_only_fields = ("id",)

    def create(self, validated_data):
        ingredients = validated_data.pop("ingredients", None)
        recipe = Recipe.objects.create(**validated_data)

        if ingredients is not None:
            for ingredient in ingredients:
                Ingredient.objects.create(
                    name=ingredient["name"], recipe=recipe
                )

        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop("ingredients", None)

        if ingredients is not None:
            instance.ingredients.all().delete()
            for ingredient in ingredients:
                instance.ingredients.create(
                    name=ingredient["name"], recipe=instance
                )

        super().update(validated_data=validated_data, instance=instance)

        instance.description = validated_data.get(
            "description", instance.description
        )

        instance.save()
        return instance
