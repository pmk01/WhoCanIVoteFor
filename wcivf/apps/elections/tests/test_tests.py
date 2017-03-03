import datetime

from django.test import TestCase

from elections.models import Election


class TestTests(TestCase):
    def test_election(self):
        e = Election(
            election_date=datetime.datetime.today(),
            current=True,
        )
        e.save()
