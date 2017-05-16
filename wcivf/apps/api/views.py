from rest_framework import viewsets
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from api import serializers

from people.models import Person
from elections.views import mixins


class PostcodeNotProvided(APIException):
    status_code = 400
    default_detail = 'A postcode is GET parameter required'
    default_code = 'postcode_required'


class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = serializers.PersonSerializer


class CandidatesAndElectionsForPostcodeViewSet(
        viewsets.ViewSet, mixins.PostcodeToPostsMixin,
        mixins.PostelectionsToPeopleMixin):

    def list(self, request, *args, **kwargs):
        postcode = request.GET.get('postcode', None)
        if not postcode:
            raise PostcodeNotProvided()
        postcode = self.clean_postcode(postcode)

        results = []

        postelections = self.postcode_to_posts(postcode, compact=True)
        for postelection in postelections:
            candidates = []
            personposts = self.postelections_to_people(postelection)
            for personpost in personposts:
                candidates.append(
                    serializers.PersonPostSerializer(personpost).data)


            election = {
                'election_date': postelection.election.election_date,
                'election_name': postelection.election.name,
                'election_id': postelection.election.slug,
                'post': {
                    'post_name': postelection.post.label,
                    'post_slug': postelection.post.ynr_id,
                },
                'candidates': candidates

            }
            results.append(election)
        return Response(results)
