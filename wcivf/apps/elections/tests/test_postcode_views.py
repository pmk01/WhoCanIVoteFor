import vcr

from django.test import TestCase, override_settings

from elections.tests.factories import (
    ElectionFactory,
    PostFactory,
    PostElectionFactory,
)
from core.models import LoggedPostcode, write_logged_postcodes


@override_settings(
    STATICFILES_STORAGE="pipeline.storage.NonPackagingPipelineStorage",
    PIPELINE_ENABLED=False,
)
class PostcodeViewTests(TestCase):
    def setUp(self):
        self.election = ElectionFactory(
            name="City of London Corporation local election",
            election_date="2017-03-23",
            slug="local.city-of-london.2017-03-23",
        )
        self.post = PostFactory(ynr_id="LBW:E05009288", label="Aldersgate")

    @vcr.use_cassette("fixtures/vcr_cassettes/test_postcode_view.yaml")
    def test_postcode_view(self):
        response = self.client.get("/elections/EC1A4EU", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "elections/postcode_view.html")

    @vcr.use_cassette("fixtures/vcr_cassettes/test_postcode_view.yaml")
    @override_settings(REDIS_KEY_PREFIX="WCIVF_TEST")
    def test_logged_postcodes(self):
        assert LoggedPostcode.objects.all().count() == 0
        response = self.client.get("/elections/EC1A4EU", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "elections/postcode_view.html")
        assert LoggedPostcode.objects.all().count() == 0
        write_logged_postcodes()
        assert LoggedPostcode.objects.all().count() == 1

    @vcr.use_cassette("fixtures/vcr_cassettes/test_ical_view.yaml")
    def test_ical_view(self):
        election = ElectionFactory(slug="local.cambridgeshire.2017-05-04")
        post = PostFactory(
            ynr_id="CED:romsey", label="Romsey", elections=election
        )

        PostElectionFactory(post=post, election=election)
        response = self.client.get("/elections/CB13HU.ics", follow=True)
        self.assertEqual(response.status_code, 200)

    @vcr.use_cassette("fixtures/vcr_cassettes/test_mayor_elections.yaml")
    def test_mayor_election_postcode_lookup(self):
        election = ElectionFactory(slug="mayor.tower-hamlets.2018-05-03")
        post = PostFactory(
            ynr_id="tower-hamlets", label="Tower Hamlets", elections=election
        )

        PostElectionFactory(post=post, election=election)
        response = self.client.get("/elections/e32nx/", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["postelections"].count(), 1)
        self.assertContains(response, "Tower Hamlets")
