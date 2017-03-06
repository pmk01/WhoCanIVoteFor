from django.test import TestCase

from people.tests.factories import PersonFactory, PersonPostFactory
from elections.tests.factories import ElectionFactory, PostFactory


class TestPersonInMultipleElections(TestCase):
    def test_more_than_one_election(self):
        person = PersonFactory()
        election1 = ElectionFactory()
        election2 = ElectionFactory(slug="parl.2010")

        post2 = PostFactory(
            ynr_id="WMC:E14000645",
            label="Southwark",
            elections=election2)
        person.elections.add(election1)
        person.elections.add(election2)

        PersonPostFactory(person=person, election=election1)
        PersonPostFactory(
            person=person, elections=election2, post=post2)
        assert person.posts.all().count() == 2
