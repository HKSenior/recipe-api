from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


RECIPE_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """
        Return recipe detail URL.
    """
    return reverse('recipe:recipe-detail', args=[recipe_id])


def sample_tag(user, name='Casserole'):
    """
        Create and return a sample tag.
    """
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name='Butter'):
    """
        Create and return a sample tag.
    """
    return Ingredient.objects.create(user=user, name=name)


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

    def test_view_recipe_detail(self):
        """
            Test viewing a recipe detail.
        """
        # Add a sample recipe with a tag and ingredient
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        # Generate the url & make a GET Request
        url = detail_url(recipe.id)
        res = self.client.get(url)

        # Serialize the data
        serializer = RecipeDetailSerializer(recipe)

        # Assertion
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_recipe(self):
        """
            Test creating a recipe.
        """
        payload = {
            'title': 'Curry Chicken',
            'time_minutes': 45,
            'price': 16.00
        }

        # Make a POST Request
        res = self.client.post(RECIPE_URL, payload)

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        """
            Test creating a recipe with tags.
        """
        # Create tags
        tag1 = sample_tag(user=self.user, name='indian')
        tag2 = sample_tag(user=self.user, name='dinner')

        # Create payload and make a POST Request
        payload = {
            'title': 'curry chicken',
            'tags': [tag1.id, tag2.id],
            'time_minutes': 55,
            'price': 21.99
        }
        res = self.client.post(RECIPE_URL, payload)

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        """
            Test creating recipe with ingredients.
        """
        # Create ingredients
        ingredient1 = sample_ingredient(user=self.user, name='bluberry')
        ingredient2 = sample_ingredient(user=self.user, name='suger')

        # Create payload and make a POST Request
        payload = {
            'title': 'Blueberry Pie',
            'ingredients': [ingredient1.id, ingredient2.id],
            'time_minutes': 35,
            'price': 12
        }
        res = self.client.post(RECIPE_URL, payload)

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)
