from django.test import TestCase

from parties.tests.factories import PartyFactory
from people.tests.factories import PersonPostFactory
from elections.tests.factories import ElectionFactory, PostFactory
from parties.models import Party


class PartyViewTests(TestCase):
    def setUp(self):
        self.party = PartyFactory()
        election = ElectionFactory()
        post = PostFactory()
        PersonPostFactory(
            party=self.party,
            election=election,
            post=post,
        )

    def test_party_list_view(self):
        assert Party.objects.all().count() == 1
        # TODO Use reverse here
        response = self.client.get("/parties/", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'parties/party_list.html')
        self.assertContains(response, self.party.party_name)

    def test_party_detail_view(self):
        # TODO Use reverse here
        response = self.client.get(
            "/parties/{}/london".format(self.party.party_id),
            follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'parties/party_detail.html')
        self.assertContains(response, self.party.party_name)
