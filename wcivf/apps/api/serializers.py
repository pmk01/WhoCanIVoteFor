from rest_framework import serializers

from people.models import Person, PersonPost
from parties.models import Party


class PersonSerializer(serializers.ModelSerializer):
    absolute_url = serializers.SerializerMethodField()

    def get_absolute_url(self, obj):
        if 'request' in self.context:
            return self.context['request'].build_absolute_uri(
                obj.get_absolute_url()
            )
        return obj.get_absolute_url()

    class Meta:
        model = Person
        fields = ('ynr_id', 'name', 'absolute_url')



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
