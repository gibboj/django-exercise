from django.test import TestCase
from django.urls import reverse
from core.serializers import RecipeSerializer

from rest_framework import status
from rest_framework.test import APIClient
from core.models import Recipe, Ingredient
from django.core.exceptions import ObjectDoesNotExist


RECIPE_URL = reverse("recipe:recipe-list")


def recipe_detail_url(recipe_id):
    return reverse("recipe:recipe-detail", args=[recipe_id])


def sample_ingredient(name, recipe):
    return Ingredient.objects.create(name=name, recipe=recipe)


def sample_recipe(**params):
    default = {"name": "sample recipe", "description": "sample description"}
    default.update(**params)
    return Recipe.objects.create(**params)


class RecipeTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_recipe_list_retrieval(self):
        recipe_1 = sample_recipe(
            name="French Onion Soup", description="So delicious"
        )

        sample_recipe(
            name="Greek Salad", description="its all about the tomatoes"
        )
        sample_ingredient(name="Onion", recipe=recipe_1)
        sample_ingredient(name="Water", recipe=recipe_1)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all()
        serialize = RecipeSerializer(recipes, many=True)
        self.assertEqual(len(recipes), 2)
        self.assertEqual(res.data, serialize.data)

    def test_recipe_list_with_name_query(self):
        recipe_1 = sample_recipe(
            name="Meatloaf", description="Old-fashion american food"
        )
        recipe_2 = sample_recipe(name="Shashuka")
        recipe_3 = sample_recipe(name="Vegan Meatballs")

        res = self.client.get(RECIPE_URL, {"name": "meat"})

        serializer_1 = RecipeSerializer(recipe_1)
        serializer_2 = RecipeSerializer(recipe_2)
        serializer_3 = RecipeSerializer(recipe_3)
        self.assertIn(serializer_1.data, res.data)
        self.assertNotIn(serializer_2.data, res.data)
        self.assertIn(serializer_3.data, res.data)

    def test_recipe_detail_retrieval(self):
        recipe_1 = sample_recipe(
            name="Meatballs", description="Like your mom makes"
        )
        sample_ingredient(name="ground beef", recipe=recipe_1)

        res = self.client.get(recipe_detail_url(recipe_1.id))

        serializer_1 = RecipeSerializer(recipe_1)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer_1.data)

    def test_recipe_creation_no_ingredients(self):
        payload = {
            "name": "Butterscotch Cookies",
            "description": "Very meh",
        }

        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data["id"])

        for key in payload.keys():
            self.assertEqual(getattr(recipe, key), payload[key])

    def test_recipe_creation_with_ingredients(self):
        ingredient_1 = {"name": "Bun"}
        ingredient_2 = {"name": "Sausage"}
        payload = {
            "name": "Hot Dog",
            "description": "How sad",
            "ingredients": [ingredient_1, ingredient_2],
        }

        res = self.client.post(RECIPE_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data["id"])

        ingredients = recipe.ingredients.all().order_by("name")
        self.assertEqual(ingredient_1["name"], ingredients[0].name)
        self.assertEqual(ingredient_2["name"], ingredients[1].name)

    def test_recipe_update_ingredients(self):
        recipe = sample_recipe(name="Hamburger", description="The safe option")
        sample_ingredient(name="ground beef", recipe=recipe)
        sample_ingredient(name="tomato", recipe=recipe)

        ingredient_1 = {"name": "onion"}
        payload = {"ingredients": [ingredient_1]}

        res = self.client.patch(
            recipe_detail_url(recipe.id), payload, format="json"
        )

        recipe.refresh_from_db()
        ingredient = recipe.ingredients.all().order_by("-name")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(ingredient.count(), 1)
        self.assertEqual(ingredient_1["name"], ingredient[0].name)

    def test_recipe_update_to_zero_ingredients(self):
        recipe = sample_recipe(name="Hamburger", description="The safe option")
        sample_ingredient(name="ground beef", recipe=recipe)
        sample_ingredient(name="tomato", recipe=recipe)

        payload = {"ingredients": []}

        self.client.patch(recipe_detail_url(recipe.id), payload, format="json")

        recipe.refresh_from_db()

        self.assertEqual(recipe.ingredients.count(), 0)

    def test_recipe_update_name_and_description(self):
        recipe = sample_recipe(
            name="Indian Curry", description="So many kinds"
        )
        ingredient_1 = sample_ingredient(name="Aloo", recipe=recipe)
        sample_ingredient(name="Gobi", recipe=recipe)
        payload = {"name": "Thai Curry", "description": "Green is my favorite"}

        res = self.client.patch(
            recipe_detail_url(recipe.id), payload, format="json"
        )

        recipe.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(ingredient_1, recipe.ingredients.all())
        self.assertEqual(recipe.name, payload["name"])
        self.assertEqual(recipe.description, payload["description"])

    def test_recipe_delete(self):
        recipe_1 = sample_recipe(
            name="Lomo Saltado", description="why french fries"
        )

        recipe_2 = sample_recipe(name="Kangaroo Steak", description="Meaty")
        ingredient = sample_ingredient("Kangaroo Steak", recipe=recipe_1)
        sample_ingredient("Salt", recipe=recipe_2)

        res = self.client.delete(recipe_detail_url(recipe_1.id))

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Ingredient.objects.count(), 1)

        with self.assertRaises(ObjectDoesNotExist):
            Recipe.objects.get(id=recipe_1.id)
            Ingredient.objects.get(id=ingredient.id)
