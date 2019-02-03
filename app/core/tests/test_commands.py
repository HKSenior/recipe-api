from unittest.mock import patch

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import TestCase


class CommandTests(TestCase):

    def test_wait_for_db_ready(self):
        """
            Test waiting for the database when it is available.
        """
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            # Set the function to return True
            gi.return_value = True

            # Call the management command
            call_command('wait_for_db')

            # Assertions
            self.assertEqual(gi.call_count, 1)

    @patch('time.sleep', return_value=True)
    def test_wait_for_db(self, ts):
        """
            Test waiting for the database.
        """
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            # Raise the OperationalError on the first 5 attempts
            # and then allow django to connect to the database on
            # the 5 attempt.
            gi.side_effect = [OperationalError] * 5 + [True]

            # Call the management command
            call_command('wait_for_db')

            # Assertion
            self.assertEqual(gi.call_count, 6)
