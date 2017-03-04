import vcr

from django.test import TestCase

from people.tests.factories import PersonFactory, PersonPostFactory
from elections.tests.factories import ElectionFactory, PostFactory


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

        # https://candidates.democracyclub.org.uk/upcoming-elections?postcode=EC1A%204EU

    @vcr.use_cassette(
        'fixtures/vcr_cassettes/test_postcode_view.yaml')
    def test_postcode_view(self):
        response = self.client.get("/elections/EC1A4EU", follow=True)
        self.assertEqual(response.status_code, 200)
        # self.assertTemplateUsed(response, 'people/person_detail.html')

