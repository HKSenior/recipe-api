from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """
        Test the unauthenticated uses API.
    """

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user(self):
        """
            Test whether creating a user with a
            valid payload is successful.
        """
        # Payload
        payload = {
            'email': 'testing@gmail.com',
            'password': 'santa4521!',
            'name': 'Test name'
        }

        # Make a POST request
        res = self.client.post(CREATE_USER_URL, payload)

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """
            Test creating a user that already exists fails.
        """
        # Payload
        payload = {
            'email': 'testing@gmail.com',
            'password': 'santa4521!',
        }

        # Create a user and make the POST request
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        # Assertion
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """
            Test that the password is more than 8 characters.
        """
        # Payload
        payload = {
            'email': 'testing@gmail.com',
            'password': 'apass',
        }

        # Make a POST request
        res = self.client.post(CREATE_USER_URL, payload)

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token(self):
        """
            Test if a token is successful created for the user.
        """
        # Payload
        payload = {
            'email': 'testing@gmail.com',
            'password': 'santa4521!',
        }

        # Create the user and send a POST request
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        # Assertions
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """
            Test if a token is not created when invalid
            credentials are given.
        """
        # Create the user and incorrect payload
        create_user(email='testing@gmail.com', password='santa4521!')
        payload = {
            'email': 'testing@gmail.com',
            'password': 'wrong',
        }

        # Make a POST request with incorrect credentials
        res = self.client.post(TOKEN_URL, payload)

        # Assertions
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """
            Test that a token is not created if
            the user doesn't exist.
        """
        # Payload
        payload = {
            'email': 'testing@gmail.com',
            'password': 'santa4521!',
        }

        # Make a POST request
        res = self.client.post(TOKEN_URL, payload)

        # Assertions
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """
            Make the email and password required.
        """
        # Send PoST request with bad payload
        res = self.client.post(TOKEN_URL, {'email': 'one', 'password': ''})

        # Assetions
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """
            Test authentication is required for users.
        """
        # Make a POST request
        res = self.client.get(ME_URL)

        # Assertion
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """
        Test API requests that require authentication.
    """
    def setUp(self):
        # Create the user
        self.user = create_user(
            email='testing@gmail.com',
            password='santa4521!',
            name='test'
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """
            Test retrieving profile of a logged in user.
        """
        # Make a POST request
        res = self.client.get(ME_URL)

        # Assertion
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email
        })

    def test_post_me_not_allowed(self):
        """
            Test that POST is not allowed on the me url.
        """
        # Make a POST request
        res = self.client.post(ME_URL, {})

        # Assertion
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """
            Test updating the user profile for authenticated users.
        """
        # Payload
        payload = {
            'name': 'Brian',
            'password': 'briansnewpassword'
        }

        # Make a PATCH request and update database
        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()

        # Assertions
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
