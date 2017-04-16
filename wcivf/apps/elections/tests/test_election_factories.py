from django.test import TestCase

from elections.tests.factories import (
    ElectionFactory, PostFactory, VotingSystemFactory, PostElectionFactory)

from elections.models import Election, Post, VotingSystem, PostElection

class TestFactories(TestCase):
    """
    Meta tests to ensure that the factories are working
    """

    def _test_save(self, model, factory):
        self.assertEqual(model.objects.all().count(), 0)
        created_model = factory.create()
        self.assertEqual(model.objects.all().count(), 1)
        return created_model

    def test_election_factory(self):
        model = self._test_save(Election, ElectionFactory)
        self.assertEqual(model.name, "UK General Election 2015")

    def test_post_factory(self):
        model = self._test_save(Post, PostFactory)
        self.assertEqual(model.label, "copeland")

    def test_post_election_factory(self):
        self.assertEqual(Election.objects.all().count(), 0)
        self.assertEqual(Post.objects.all().count(), 0)
        model = self._test_save(PostElection, PostElectionFactory)
        self.assertEqual(Election.objects.all().count(), 1)
        self.assertEqual(Post.objects.all().count(), 1)


    def test_voting_system_factory(self):
        model = self._test_save(VotingSystem, VotingSystemFactory)
        self.assertEqual(model.name, "First Past The Post")
