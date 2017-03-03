from django.test import TestCase

from people.tests.factories import PersonFactory, PersonPostFactory
from elections.tests.factories import ElectionFactory



class PersonViewTests(TestCase):
    def setUp(self):
        self.person = PersonFactory()
        self.person_url = self.person.get_absolute_url()

    def test_person_view(self):
        response = self.client.get(self.person_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'people/person_detail.html')


    def test__correct_elections_listed(self):
        response = self.client.get(self.person_url, follow=True)

        election_name = "FooBar Election 2017"

        self.assertNotContains(response, election_name)
        election = ElectionFactory(
            name=election_name,
            current=True,
            slug="foobar")
        PersonPostFactory(election=election, person=self.person)

        response = self.client.get(self.person_url, follow=True)
        self.assertContains(response, election_name)
