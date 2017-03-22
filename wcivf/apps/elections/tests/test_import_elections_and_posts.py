from django.test import TestCase

import vcr
import requests

from django.conf import settings
from django.core.management import call_command

from elections.models import Election, Post


class TestElectionAndPostImporter(TestCase):
    base_url = settings.YNR_BASE

    def _import_elections(self):
        call_command('import_elections')

    def _import_posts(self):
        url = self.base_url + '/api/v0.9/posts/'
        req = requests.get(url)
        results = req.json()
        for post in results['results']:
            Post.objects.update_or_create_from_ynr(post)

    @vcr.use_cassette(
        'fixtures/vcr_cassettes/test_import_elections_from_ynr.yaml')
    def test_import_elections_from_ynr(self):
        assert Election.objects.count() == 0
        self._import_elections()
        assert Election.objects.count() == 295

    @vcr.use_cassette('fixtures/vcr_cassettes/test_import_posts_from_ynr.yaml')
    def test_import_posts_from_ynr(self):
        assert Election.objects.count() == 0
        self._import_elections()
        self._import_posts()
        assert Election.objects.count() == 297
