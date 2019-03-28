from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Recipe
from recipe.serializers import TagSerializer


TAGS_URL = reverse('recipe:tag-list')


class PublicTagsApiTests(TestCase):
    """
        Test the publicly available tags API.
    """

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """
            Test that login is required for retrieving tags.
        """
        res = self.client.get(TAGS_URL)

        # Assertion
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """
        Test the authorized user tags API.
    """

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='testing@gmail.com',
            password='santa4521!'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieving_tags(self):
        """
            Test retrieving tags.
        """
        # Create 2 tags
        Tag.objects.create(user=self.user, name='vegan')
        Tag.objects.create(user=self.user, name='halal')

        res = self.client.get(TAGS_URL)
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        # Assertion
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """
            Test that tags returned are for the authenticated user.
        """
        # Create the second user
        user2 = get_user_model().objects.create_user(
            email='testing2@gmail.com',
            password='santa4521!_2'
        )

        # Add a tag to user2 and authenticated user
        Tag.objects.create(user=user2, name='kosher')
        tag = Tag.objects.create(user=self.user, name='vegan')

        # Make a GET request for the tags
        res = self.client.get(TAGS_URL)

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag_successful(self):
        """
            Test creating a new tag.
        """
        payload = {'name': 'Test tag'}
        self.client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()

        # Assertions
        self.assertTrue(exists)

    def test_create_tag_invalid_name(self):
        """
            Test creating a new tag with an invalid payload.
        """
        payload = {'name': ''}
        res = self.client.post(TAGS_URL, payload)

        # Assertion
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_tags_assigned_to_recipes(self):
        """
            Test filtering tags by those assigned to recipes.
        """
        tag1 = Tag.objects.create(user=self.user, name='Breakfast')
        tag2 = Tag.objects.create(user=self.user, name='Lunch')
        recipe = Recipe.objects.create(
            title='Eggs on toast',
            time_minutes=14,
            price=8.00,
            user=self.user
        )
        recipe.tags.add(tag1)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})
        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)

        # Assertions
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_tags_assigned_unique(self):
        """
            Test if unique tags are returned when filtered.
        """
        tag = Tag.objects.create(user=self.user, name='Breakfast')
        Tag.objects.create(user=self.user, name='Lunch')
        recipe1 = Recipe.objects.create(
            title='Pancakes',
            time_minutes=5,
            price=3.00,
            user=self.user
        )
        recipe1.tags.add(tag)
        recipe2 = Recipe.objects.create(
            title='Porridge',
            time_minutes=4,
            price=4.00,
            user=self.user
        )
        recipe2.tags.add(tag)
        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        # Assertions
        self.assertEqual(len(res.data), 1)
