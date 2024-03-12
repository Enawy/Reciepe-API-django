# test for django management commands

from unittest.mock import patch

from psycopg2 import OperationalError as Psy2Error

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase


@patch('core.management.commands.wait_for_db.Command.check')  # mocking the methode of base command check methode
class CommandTest(SimpleTestCase):
    # test commands

    def test_wait_for_db_ready(self, patched_check):  # parameter of @patch that contain the mocked value
        # To test when will be the database ready
        patched_check.return_value = True

        call_command('wait_for_db')  # checks if the command "wait_for_db" is there.
        patched_check.assert_called_once_with(databases=['default'])  # checks if the check method in has been called

    @patch('time.sleep')  # override the sleep function so doesn't stop test module till it finishes
    def test_wait_for_db_delay(self, patched_sleep, patched_check):  # patched is the methode used for patch decorator
        # waiting for data when getting db operation error
        patched_check.side_effect = [Psy2Error] * 2 + \
                                    [OperationalError] * 3 + [True]

        """
        this will return an exception using side_effect instead of returning
        a bool value like the example above, the multiply indicate how many
        times we will raise the error so the Psy2error will be called the
        first 2 times then the OperationalError for the 2nd 3 times.

        In the 6th time it will return a bool value of true and side_effect
        will return that value cause it know that it's not an exception.

        postgres before it even start can't establish any connection which
        can be raises the psycopg2.OperationalError.
        if it started but it still didn't load the dev DB used in testing
        then it will raise the django's db.utils OperationalError.
        """

        call_command('wait_for_db')
        self.assertEqual(patched_check.call_count, 6)
        patched_check.assert_called_with(databases=['default'])
