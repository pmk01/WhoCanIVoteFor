from django.test import TestCase
from io import StringIO
from unittest import mock

import vcr
import requests

from django.conf import settings
from django.core.management import call_command

from elections.helpers import JsonPaginator
from elections.models import Election, Post, PostElection
from elections.management.commands.import_posts import Command as ImportPosts


class TestElectionAndPostImporter(TestCase):
    base_url = settings.YNR_BASE

    def _import_elections(self):
        command_stdout = StringIO(newline=None)
        call_command("import_elections", stdout=command_stdout)

    def _import_posts(self):
        url = self.base_url + "/api/v0.9/posts/"
        req = requests.get(url)
        results = req.json()
        # doing this is going to import
        # the first page of posts (10 records)
        # and then discard all the subsequent pages
        # so we only expect to import 10 posts
        # and their associated PostElections
        for post in results["results"]:
            Post.objects.update_or_create_from_ynr(post)

    @vcr.use_cassette(
        "fixtures/vcr_cassettes/test_import_elections_from_ynr.yaml"
    )
    def test_import_elections_from_ynr(self):
        assert Election.objects.count() == 0
        self._import_elections()
        assert Election.objects.count() == 385

    @vcr.use_cassette("fixtures/vcr_cassettes/test_import_posts_from_ynr.yaml")
    def test_import_posts_from_ynr(self):
        assert Election.objects.count() == 0
        self._import_elections()
        self._import_posts()
        assert Election.objects.count() == 925
        assert Post.objects.count() == 10
        assert PostElection.objects.count() == 21


fake_cancelled_election_data = {
    "results": [
        {
            "id": 1,
            "label": "Election 1",
            "role": "foo",
            "group": "foo",
            "organization": {"name": "foo"},
            "elections": [
                {
                    "id": "fake.election.1",
                    "ballot_paper_id": "fake.election.post.1",
                    "candidates_locked": True,
                    "winner_count": "1",
                    "cancelled": True,
                }
            ],
            "memberships": [],
        },
        {
            "id": 2,
            "label": "Election 2",
            "role": "foo",
            "group": "foo",
            "organization": {"name": "foo"},
            "elections": [
                {
                    "id": "fake.election.2",
                    "ballot_paper_id": "fake.election.post.2",
                    "candidates_locked": True,
                    "winner_count": "1",
                    "cancelled": False,
                }
            ],
            "memberships": [],
        },
    ]
}


class FakeCancelledPager(JsonPaginator):
    def __iter__(self):
        yield fake_cancelled_election_data
        return


class CancelledBallotPostImporter(TestCase):
    @mock.patch(
        "elections.helpers.EEHelper.get_data",
        lambda x, y: {
            "replaced_by": "fake.election.post.2",
            "metadata": {"foo": "bar"},
        },
    )
    def test_cancelled_ballots_import(self):
        Election.objects.create(
            slug="fake.election.1", election_date="2018-01-01", current=False
        )
        Election.objects.create(
            slug="fake.election.2", election_date="2018-02-01", current=False
        )
        cmd = ImportPosts()
        cmd.stdout = StringIO()
        cmd.get_paginator = lambda x: FakeCancelledPager("", cmd.stdout)
        cmd.handle()
        cancelled = PostElection.objects.get(
            ballot_paper_id="fake.election.post.1"
        )
        replacement = PostElection.objects.get(
            ballot_paper_id="fake.election.post.2"
        )
        self.assertEqual(cancelled.cancelled, True)
        self.assertEqual(cancelled.replaced_by, replacement)
        self.assertDictEqual(cancelled.metadata, {"foo": "bar"})
        self.assertEqual(replacement.cancelled, False)
        self.assertEqual(replacement.replaced_by, None)
        self.assertEqual(replacement.metadata, None)


class FakeTerritoryPager(JsonPaginator):
    def __iter__(self):
        yield {
            "results": [
                {
                    "id": 1,
                    "label": "Election 1",
                    "role": "foo",
                    "group": "foo",
                    "organization": {"name": "foo"},
                    "elections": [
                        {
                            "id": "fake.election.1",
                            "ballot_paper_id": "fake.election.post.1",
                            "candidates_locked": True,
                            "winner_count": "1",
                            "cancelled": False,
                        }
                    ],
                    "memberships": [],
                }
            ]
        }
        return


class TerritoryImporter(TestCase):
    @mock.patch(
        "elections.helpers.EEHelper.get_data",
        lambda x, y: {"organisation": {"territory_code": "ENG"}},
    )
    def test_territory_import(self):
        Election.objects.create(
            slug="fake.election.1", election_date="2018-01-01", current=False
        )
        cmd = ImportPosts()
        cmd.stdout = StringIO()
        cmd.get_paginator = lambda x: FakeTerritoryPager("", cmd.stdout)
        cmd.handle()

        post_election = PostElection.objects.get(
            ballot_paper_id="fake.election.post.1"
        )
        self.assertEqual(post_election.post.territory, "ENG")

    @mock.patch(
        "elections.helpers.EEHelper.get_data", lambda x, y: {"organisation": {}}
    )
    def test_territory_import_without_territory_from_ee(self):
        Election.objects.create(
            slug="fake.election.1", election_date="2018-01-01", current=False
        )
        cmd = ImportPosts()
        cmd.stdout = StringIO()
        cmd.get_paginator = lambda x: FakeTerritoryPager("", cmd.stdout)
        cmd.handle()

        post_election = PostElection.objects.get(
            ballot_paper_id="fake.election.post.1"
        )
        self.assertEqual(post_election.post.territory, "-")
