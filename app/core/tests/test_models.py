from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(email='testing@gmail.com', password='santa4521!'):
    """
        Create a sample user.
    """
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):

    def test_create_user_with_email(self):
        """
            Test whether or not creating a new user
            with an email is successful.
        """
        # User information
        email = 'testing@gmail.com'
        password = 'testingModels123'

        # Create a new user
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        # Assertions
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """
            Test whether or no the email for a new user
            is normalized.
        """
        # User information
        email = 'testing@GMAIL.COM'

        # Create a new user
        user = get_user_model().objects.create_user(
            email=email,
            password='testingModels123'
        )

        # Assertion
        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """
            Test whether an error is raised when a user
            is created without an email.
        """
        # Test for the ValueError being raised
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                email=None,
                password='testingModels123'
            )

    def test_create_new_superuser(self):
        """
            Test creating a new superuser.
        """
        # Create a superuser
        user = get_user_model().objects.create_superuser(
            email='testing@gmail.com',
            password='testingModels123'
        )

        # Assertions
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str_(self):
        """
            Test the tag string representation.
        """
        # Create a tag
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='halal'
        )

        # Assertion
        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """
            Test the ingredient string representation.
        """
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name='banana'
        )

        # Assertion
        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_str(self):
        """
            Test the recipe str representation.
        """
        recipe = models.Recipe.objects.create(
            user=sample_user(),
            title='Mac and Cheese',
            time_minutes=90,
            price=19.99
        )

        # Assertion
        self.assertEqual(str(recipe), recipe.title)

    @patch('uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        """
            Test the image is saved in the correct location.
        """
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, 'MyImage.jpg')

        # Assertion
        self.assertEqual(file_path, f'uploads/recipe/{uuid}.jpg')
