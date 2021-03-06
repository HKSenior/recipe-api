from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient, Recipe

from recipe.serializers import IngredientSerializer


INGREDIENT_URL = reverse('recipe:ingredient-list')


class PublicIngredientApiTests(TestCase):
    """
        Test the publicly available ingredients API.
    """

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """
            Test that login is required to access the endpoint.
        """
        # Make a GET request
        res = self.client.get(INGREDIENT_URL)

        # Assertion
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientApiTests(TestCase):
    """
        Test the private indgredients API.
    """

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test@gmail.com',
            password='santa4521!'
        )
        self.client.force_authenticate(self.user)

    def test_retrieving_indgredient_list(self):
        """
            Test retrieving the indgredient list.
        """
        # Create ingredients
        Ingredient.objects.create(user=self.user, name='asparagus')
        Ingredient.objects.create(user=self.user, name='bell peppers')

        # Make a GET request
        res = self.client.get(INGREDIENT_URL)

        # Serialize the data
        indgredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(indgredients, many=True)

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_indgredients_limited_to_user(self):
        """
            Test the indgredients returned are for the authenticated
            user.
        """
        # Create another user
        user2 = get_user_model().objects.create_user(
            email='testing@gmail.com',
            password='santa4521_2!'
        )

        # Create ingredients
        Ingredient.objects.create(user=user2, name='tumeric')
        i = Ingredient.objects.create(user=self.user, name='kale')

        # Make a GET request
        res = self.client.get(INGREDIENT_URL)

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], i.name)

    def test_create_ingredient_successful(self):
        """
            Test creating a new ingredient.
        """
        # Payload
        payload = {'name': 'tumeric'}

        # Make a POST request
        self.client.post(INGREDIENT_URL, payload)

        # Check if the ingredient exists
        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()

        # Assertion
        self.assertTrue(exists)

    def test_create_ingredient_invalid(self):
        """
            Test creating an invalid ingredient fails.
        """
        # Payload
        payload = {'name': ''}

        # Make a POST request
        res = self.client.post(INGREDIENT_URL, payload)

        # Assertion
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_ingredients_assigned_to_recipes(self):
        """
            Test filtering ingredients by those assigned to recipes.
        """
        ingredient1 = Ingredient.objects.create(user=self.user, name='Apples')
        ingredient2 = Ingredient.objects.create(user=self.user, name='Turkey')
        recipe = Recipe.objects.create(
            title='Apple Cumble',
            time_minutes=45,
            price=19.99,
            user=self.user
        )
        recipe.ingredients.add(ingredient1)

        res = self.client.get(INGREDIENT_URL, {'assigned_only': 1})
        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)

        # Assertions
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_ingredients_assigned_unique(self):
        """
            Test filtering ingredients by assigned returns unique items.
        """
        ingredient = Ingredient.objects.create(user=self.user, name='Eggs')
        Ingredient.objects.create(user=self.user, name='Cheese')
        recipe1 = Recipe.objects.create(
            title='Eggs on toast',
            time_minutes=14,
            price=8.00,
            user=self.user
        )
        recipe1.ingredients.add(ingredient)
        recipe2 = Recipe.objects.create(
            title='Eggs benedict',
            time_minutes=10,
            price=5.99,
            user=self.user
        )
        recipe2.ingredients.add(ingredient)
        res = self.client.get(INGREDIENT_URL, {'assigned_only': 1})

        # Assertion
        self.assertEqual(len(res.data), 1)
