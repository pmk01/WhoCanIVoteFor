from django.test import TestCase

from people.models import Person, PersonPost
from people.tests.factories import PersonFactory, PersonPostFactory
from elections.tests.factories import (
    ElectionFactory, PostFactory, PostElectionFactory)


class PersonManagerTests(TestCase):
    def setUp(self):
        self.election = ElectionFactory()
        self.post = PostFactory()
        self.pe = PostElectionFactory(
            election=self.election,
            post=self.post,
        )
        people = [PersonFactory() for p in range(5)]
        for person in people:
            PersonPostFactory(
                post_election=self.pe,
                election=self.election,
                post=self.post,
                person=person,
            )

    def test_counts_by_post(self):
        assert Person.objects.all().count() == 5
        assert PersonPost.objects.all().counts_by_post().count() == 1
