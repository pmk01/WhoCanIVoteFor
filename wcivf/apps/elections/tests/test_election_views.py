from django.test import TestCase
from django.test.utils import override_settings
from elections.tests.factories import ElectionFactory, PostFactory
from elections.models import PostElection


@override_settings(
    STATICFILES_STORAGE="pipeline.storage.NonPackagingPipelineStorage",
    PIPELINE_ENABLED=False,
)
class ElectionViewTests(TestCase):
    def setUp(self):
        self.election = ElectionFactory(
            name="City of London Corporation local election",
            election_date="2017-03-23",
            slug="local.city-of-london.2017-03-23",
        )
        self.post = PostFactory(
            ynr_id="LBW:E05009288", label="Aldersgate", elections=self.election
        )
        PostElection.objects.get_or_create(
            election=self.election,
            post=self.post,
            ballot_paper_id="local.city-of-london.aldersgate.2017-03-23",
        )

    def test_election_list_view(self):
        # TODO Use reverse here
        with self.assertNumQueries(2):
            response = self.client.get("/elections/", follow=True)
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, "elections/elections_view.html")
            self.assertContains(response, self.election.nice_election_name)

    def test_election_detail_view(self):
        response = self.client.get(self.election.get_absolute_url(), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "elections/election_view.html")
        self.assertContains(response, self.election.nice_election_name)
