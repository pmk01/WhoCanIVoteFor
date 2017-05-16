from rest_framework import serializers

from people.models import Person, PersonPost
from parties.models import Party


class PersonSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Person
        fields = ('ynr_id', 'name')


class PartySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Party
        fields = ('party_id', 'party_name')


class PersonPostSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PersonPost
        fields = (
            'list_position',
            'party',
            'person',
            )

    person = PersonSerializer(many=False, read_only=True)
    party = PartySerializer(many=False, read_only=True)
