from django.test import TestCase
from django.db import connections
from django.db.utils import OperationalError

class DefaultDatabaseConnectionTestCase(TestCase):
    db_connection = None

    def setUp(self):
        self.db_connection = connections['default']

    def test_default_database_connection_successful(self):
        try:
            cursor = self.db_connection.cursor()
        except OperationalError:
            self.fail('Default database not configured or connected')
        else:
            self.assertIsNotNone(cursor)