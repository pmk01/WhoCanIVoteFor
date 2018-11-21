from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
import vcr

from people.tests.factories import PersonFactory, PersonPostFactory
from parties.tests.factories import PartyFactory
from elections.tests.factories import (
    ElectionFactory, PostFactory, PostElectionFactory)


class TestAPIBasics(APITestCase):

    def test_200_on_api_base(self):
        req = self.client.get(reverse('api:api-root'))
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
        assert req.data == {'detail': 'postcode is a required GET parameter'}


class TestAPISearchViews(APITestCase):

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
            ballot_paper_id='parl.cities-of-london-and-westminster.2017-06-08',
            post=self.post,
            election=self.election
        )
        PersonFactory.reset_sequence()
        person = PersonFactory()
        pe = PostElectionFactory(
            election=self.election,
            post=self.post
        )
        PersonPostFactory(
            post_election=pe,
            election=self.election,
            person=person,
            post=self.post,
            party=PartyFactory()
        )
        self.expected_response = [{
            'ballot_paper_id': 'parl.cities-of-london-and-westminster.2017-06-08',
            'absolute_url': 'http://testserver/elections/parl.2017-06-08/post-WMC:E14000639/cities-of-london-and-westminster',
            'election_date': "2017-06-08",
            'election_id': 'parl.2017-06-08',
            'election_name': '2017 General Election',
            'post': {
                'post_name': 'Cities of London and Westminster',
                'post_slug': 'WMC:E14000639'
            },
            'cancelled': False,
            'replaced_by': None,
            'candidates': [{
                'list_position': None,
                'party': {
                    'party_id': 'PP01',
                    'party_name': 'Test Party'
                },
                'person': {
                    'absolute_url': 'http://testserver/person/0/candidate-0',
                    'ynr_id': 0,
                    'name': 'Candidate 0'
                }
            }],
        }]

    @vcr.use_cassette(
        'fixtures/vcr_cassettes/test_postcode_view.yaml')
    def test_candidates_for_postcode_view(self):
        url = reverse('api:candidates-for-postcode-list')
        with self.assertNumQueries(4):
            req = self.client.get("{}?postcode=EC1A4EU".format(url))
        assert req.status_code == 200
        assert req.json() == self.expected_response

    def test_candidates_for_ballots(self):
        url = reverse('api:candidates-for-ballots-list')
        with self.assertNumQueries(4):
            req = self.client.get(
                "{}?ballot_ids=parl.cities-of-london-and-westminster.2017-06-08".format(url)
            )
        assert req.status_code == 200
        assert req.json() == self.expected_response
