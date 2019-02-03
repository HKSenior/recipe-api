import time
import logging

from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S',
    level=logging.DEBUG
)


class Command(BaseCommand):
    """
        Django command that will pause execution
        unitl the database is available.
    """

    def handle(self, *args, **options):
        logging.info(self.style.WARNING('Waiting for database...'))

        db_conn = None
        while not db_conn:
            try:
                db_conn = connections['default']
            except OperationalError:
                logging.debug(
                    self.style.WARNING(
                        'Database unavailable, waiting 1 second...'
                    )
                )
                time.sleep(1)

        logging.info(self.style.SUCCESS('Database available!'))
