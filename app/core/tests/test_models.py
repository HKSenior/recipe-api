from django.test import TestCase
from django.contrib.auth import get_user_model


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
