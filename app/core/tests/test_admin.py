from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTests(TestCase):

    def setUp(self):
        """
            Set up function that creates a test client,
            with a new user and a regular user that will
            be listed in the admin page.
        """

        # Create client
        self.client = Client()

        # Create the admin user
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@gmail.com',
            password='adminTesting123'
        )

        # Login the admin user
        self.client.force_login(self.admin_user)

        # Create the reqular user
        self.user = get_user_model().objects.create_user(
            email='user@gmail.com',
            password='userTesting123',
            name='Test user full name'
        )

    def test_users_listed(self):
        """
            Test whether users are listed on the users page.
        """

        # Get the admin url and send a GET request
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        # Assertions
        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_user_change_page(self):
        """
            Test whether the user edit page works.
        """

        # Get the admin url with the user id and send a GET request
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)

        # Assertion
        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """
            Test if the create user page works.
        """

        # Get the admin url and send a GET request
        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        # Assertions
        self.assertEqual(res.status_code, 200)
