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
        patched_check.assert_called_once_with(database=['default'])  # checks if the check method in has been called
