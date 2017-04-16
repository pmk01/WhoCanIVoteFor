import vcr

from django.test import TestCase

from elections.tests.factories import (
    ElectionFactory, PostFactory, PostElectionFactory)


class PostcodeViewTests(TestCase):
    def setUp(self):
        self.election = ElectionFactory(
            name="City of London Corporation local election",
            election_date="2017-03-23",
            slug="local.city-of-london.2017-03-23",
        )
        self.post = PostFactory(
            ynr_id="LBW:E05009288",
            label="Aldersgate"
        )

    @vcr.use_cassette(
        'fixtures/vcr_cassettes/test_postcode_view.yaml')
    def test_postcode_view(self):
        response = self.client.get("/elections/EC1A4EU", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'elections/postcode_view.html')

    @vcr.use_cassette(
        'fixtures/vcr_cassettes/test_ical_view.yaml')
    def test_ical_view(self):
        election = ElectionFactory(
            slug="local.cambridgeshire.2017-05-04",
        )
        post = PostFactory(
            ynr_id="CED:romsey",
            label="Romsey",
            elections=election
        )

        PostElectionFactory(
            post=post,
            election=election
        )
        response = self.client.get("/elections/CB13HU.ics", follow=True)
        self.assertEqual(response.status_code, 200)
