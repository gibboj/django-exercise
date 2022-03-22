from django.test import TestCase
from core.serializers import RecipeSerializer


class TestSerializer(TestCase):
    def test_recipe_serializer(self):
        payload = {
            "name": "Jalapeno poppers",
            "description": "Very american",
            "ingredients": [
                {"name": "cheese"},
                {"name": "jalapeno"},
            ],
        }

        recipe = RecipeSerializer(data=payload)
        self.assertTrue(recipe.is_valid())
        self.assertEqual(len(recipe.data["ingredients"]), 2)
