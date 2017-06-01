import datetime

from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
import vcr

from people.tests.factories import PersonFactory, PersonPostFactory
from parties.tests.factories import PartyFactory
from elections.tests.factories import (
    ElectionFactory, PostFactory, PostElectionFactory)


class TestAPI(APITestCase):
    API_BASE = reverse('api:api-root')

    def setUp(self):
        self.election = ElectionFactory(
            name="2017 General Election",
            election_date="2017-06-08",
            slug="parl.2017-06-08",
        )
        self.post = PostFactory(
            ynr_id="WMC:E14000639",
            label="Cities of London and Westminster"
        )
        self.post_election = PostElectionFactory(
            post=self.post,
            election=self.election
        )

    def test_200_on_api_base(self):
        req = self.client.get(self.API_BASE)
        assert req.status_code == 200

    def test_person_view(self):
        req = self.client.get(reverse('api:person-list'))
        assert req.status_code == 200
        assert req.data == []

        PersonFactory()  # Make a person

        req = self.client.get(reverse('api:person-list'))
        assert req.status_code == 200
        assert len(req.data) == 1

    def test_candidates_for_postcode_view_raises_error(self):
        req = self.client.get(reverse('api:candidates-for-postcode-list'))
        assert req.status_code == 400
        assert req.data == {'detail': 'A postcode is GET parameter required'}

    @vcr.use_cassette(
        'fixtures/vcr_cassettes/test_postcode_view.yaml')
    def test_candidates_for_postcode_view(self):
        person = PersonFactory()  # Make a person
        PersonPostFactory(
            election=self.election,
            person=person,
            post=self.post,
            party=PartyFactory()
        )
        url = reverse('api:candidates-for-postcode-list')
        with self.assertNumQueries(3):
            req = self.client.get("{}?postcode=EC1A4EU".format(url))
        assert req.status_code == 200
        assert req.data == [{
            'election_date': datetime.date(2017, 6, 8),
            'election_id': 'parl.2017-06-08',
            'election_name': '2017 General Election',
            'post': {
                'post_name': 'Cities of London and Westminster',
                'post_slug': 'WMC:E14000639'
            },
            'candidates': [{
                'list_position': None,
                'party': {
                    'party_id': 'PP01',
                    'party_name': 'Test Party'
                },
                'person': {
                    'ynr_id': '0',
                    'name': 'Candidate 0'
                }
            }],
        }]
