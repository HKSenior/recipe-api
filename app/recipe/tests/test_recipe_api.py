from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe

from recipe.serializers import RecipeSerializer


RECIPE_URL = reverse('recipe:recipe-list')


def sample_recipe(user, **params):
    """
        Create and return a sample recipe.
    """
    # Default parameters of the recipe
    defaults = {
        'title': 'Sample Recipe',
        'time_minutes': 30,
        'price': 5.00
    }

    # Update the default dict
    defaults.update(params)

    # Create the recipe
    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeApiTests(TestCase):
    """
        Test unauthenticated recipe API access.
    """
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """
            Test that authentication is required.
        """
        # Make a GET Request
        res = self.client.get(RECIPE_URL)

        # Assertion
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """
        Test authenticated recipe API access.
    """
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'testing@gmail.com',
            'santa4521!'
        )

        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """
            Test retrieving a list of recipes.
        """
        # Create recipes
        sample_recipe(user=self.user)
        sample_recipe(user=self.user, title='Pizza')

        # Make a GET Request
        res = self.client.get(RECIPE_URL)

        # Get the recipes and serialize the data
        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        """
            Test retrieving recipes for user.
        """
        # Create second user
        user2 = get_user_model().objects.create_user(
            'testing2@gmail.com',
            'santa4521!_2'
        )

        # Create recipes
        sample_recipe(user=user2)
        sample_recipe(user=self.user)

        # Make a GET Request
        res = self.client.get(RECIPE_URL)

        # Get the recipe for the authenticated user
        # and serialize the data
        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)
