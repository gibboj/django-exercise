from django.test import TestCase
from core.models import Recipe, Ingredient


class ModelTests(TestCase):
    def setUp(self):
        self.recipe = Recipe.objects.create(name="Foo", description="bar")

    def test_recipe_model_str(self):
        """Test that recipe model string is the name"""
        name = "Apple Pie"
        description = "The best of all Thanksgiving desserts"
        recipe = Recipe.objects.create(
            name=name,
            description=description,
        )

        self.assertEqual(str(recipe), name)

    def test_ingredient_model_str(self):

        name = "Butter"
        recipe = self.recipe
        ingredient = Ingredient.objects.create(name=name, recipe=recipe)
        self.assertEqual(str(ingredient), name)
