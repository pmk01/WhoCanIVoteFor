from django.test import TestCase
from io import StringIO

import vcr
import requests

from django.conf import settings
from django.core.management import call_command

from elections.models import Election, Post, PostElection


class TestElectionAndPostImporter(TestCase):
    base_url = settings.YNR_BASE

    def _import_elections(self):
        command_stdout = StringIO(newline=None)
        call_command('import_elections', stdout=command_stdout)

    def _import_posts(self):
        url = self.base_url + '/api/v0.9/posts/'
        req = requests.get(url)
        results = req.json()
        # doing this is going to import
        # the first page of posts (10 records)
        # and then discard all the subsequent pages
        # so we only expect to import 10 posts
        # and their associated PostElections
        for post in results['results']:
            Post.objects.update_or_create_from_ynr(post)

    @vcr.use_cassette(
        'fixtures/vcr_cassettes/test_import_elections_from_ynr.yaml')
    def test_import_elections_from_ynr(self):
        assert Election.objects.count() == 0
        self._import_elections()
        assert Election.objects.count() == 385

    @vcr.use_cassette('fixtures/vcr_cassettes/test_import_posts_from_ynr.yaml')
    def test_import_posts_from_ynr(self):
        assert Election.objects.count() == 0
        self._import_elections()
        self._import_posts()
        assert Election.objects.count() == 925
        assert Post.objects.count() == 10
        assert PostElection.objects.count() == 21
