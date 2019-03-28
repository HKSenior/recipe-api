import tempfile
from os import path

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from PIL import Image

from core.models import Recipe, Tag, Ingredient
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


RECIPE_URL = reverse('recipe:recipe-list')


def image_upload_url(recipe_id):
    """
        Return url for recipe image.
    """
    return reverse('recipe:recipe-upload-image', args=[recipe_id])


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

    def test_partial_update_recipe(self):
        """
            Test updating a recipe with PATCH.
        """
        # Create sample data
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, name="Italian")

        # Payload
        payload = {
            'title': 'Pizza',
            'tags': [new_tag.id]
        }

        # Get URL and make a PATCH request
        url = detail_url(recipe.id)
        self.client.patch(url, payload)

        # Refresh the database
        recipe.refresh_from_db()

        # Assertions
        self.assertEqual(recipe.title, payload['title'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_full_updated_recipe(self):
        """
            Test updating a recipe with PUT.
        """
        # Create sample data
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))

        # Payload
        payload = {
            'title': 'Chicken Pasta',
            'time_minutes': 25,
            'price': 12.00
        }

        # Get URL and make a PUT request
        url = detail_url(recipe.id)
        self.client.put(url, payload)

        # Refresh the database
        recipe.refresh_from_db()

        # Assertions
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.time_minutes, payload['time_minutes'])
        self.assertEqual(recipe.price, payload['price'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 0)


class RecipeImageUploadTests(TestCase):
    """
        Testing recipe image uploads.
    """
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'testing@gmail.com',
            'santa4521!'
        )
        self.client.force_authenticate(self.user)
        self.recipe = sample_recipe(user=self.user)

    def tearDown(self):
        self.recipe.image.delete()

    def test_upload_image_to_recipe(self):
        """
            Test uploading an image to recipe.
        """
        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as f:
            img = Image.new('RGB', (20, 20))
            img.save(f, format='JPEG')
            f.seek(0)
            res = self.client.post(url, {'image': f}, format='multipart')

            # Assertions
            self.recipe.refresh_from_db()
            self.assertEqual(res.status_code, status.HTTP_200_OK)
            self.assertIn('image', res.data)
            self.assertTrue(path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        """
            Test uploading an invalid image/
        """
        url = image_upload_url(self.recipe.id)
        res = self.client.post(url, {'image': 'notimage'}, format='multipart')

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_recipes_by_tags(self):
        """
            Test returning recipes with specific tags.
        """
        recipe1 = sample_recipe(user=self.user, title='Sicilian Pizza')
        recipe2 = sample_recipe(user=self.user, title='Ravioli')
        recipe3 = sample_recipe(user=self.user, title='Caesar Salad')
        tag1 = sample_tag(user=self.user, name='Italian')
        tag2 = sample_tag(user=self.user, name='Pasta')
        recipe1.tags.add(tag1)
        recipe2.tags.add(tag2)

        res = self.client.get(RECIPE_URL, {'tags': f'{tag1.id}, {tag2.id}'})
        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serialized3 = RecipeSerializer(recipe3)

        # Assertions
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serialized3.data, res.data)

    def test_filter_recipes_by_ingredients(self):
        """
            Test returning recipes with specific ingredients.
        """
        recipe1 = sample_recipe(user=self.user, title='Chicken over rise')
        recipe2 = sample_recipe(user=self.user, title='Oxtail and rice')
        recipe3 = sample_recipe(user=self.user, title='Steak and bread')
        ingredient1 = sample_ingredient(user=self.user, name='chicken')
        ingredient2 = sample_ingredient(user=self.user, name='rice')
        recipe1.ingredients.add(ingredient1)
        recipe2.ingredients.add(ingredient2)

        res = self.client.get(
            RECIPE_URL,
            {'ingredients': f'{ingredient1.id}, {ingredient2.id}'}
        )
        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serialized3 = RecipeSerializer(recipe3)

        # Assertions
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serialized3.data, res.data)
