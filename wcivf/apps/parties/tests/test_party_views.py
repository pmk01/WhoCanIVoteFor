from django.test import TestCase
from django.test.utils import override_settings
from parties.tests.factories import PartyFactory
from people.tests.factories import PersonFactory, PersonPostFactory
from elections.tests.factories import ElectionFactory, PostFactory
from parties.models import Party


@override_settings(
    STATICFILES_STORAGE='pipeline.storage.NonPackagingPipelineStorage',
    PIPELINE_ENABLED=False)
class PartyViewTests(TestCase):
    def setUp(self):
        self.party = PartyFactory()
        self.election = ElectionFactory()
        self.post = PostFactory()
        PersonPostFactory(
            party=self.party,
            election=self.election,
            post=self.post,
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

    def test_party_detail_candidate_count_view(self):
        # Make a 2nd candidate
        PersonPostFactory(
            party=self.party,
            election=ElectionFactory(slug="2010", name="2010 GE"),
            post=self.post,
        )
        p2 = PersonFactory(name="Test 3")
        PersonPostFactory(
            person=p2,
            post=self.post,
            election=self.election,
            party=self.party,
        )

        # TODO Use reverse here
        response = self.client.get(
            "/parties/{}/london".format(self.party.party_id),
            follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "3 candidates")
        x = response.context_data['object']
        assert len(x.personpost_set.all().counts_by_post()) == 2
