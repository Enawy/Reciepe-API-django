#  django command to wait for db to be available
import time

from psycopg2 import OperationalError as Psy2error
from django.db.utils import OperationalError

from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        # Entrypoint for command
        self.stdout.write('waiting for database...')
        db_up = False
        while db_up is False:
            try:
                self.check(databases=['default'])
                db_up = True
            except (Psy2error, OperationalError):
                self.stdout.write('data not available, wait 1 second')
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('Database available'))
