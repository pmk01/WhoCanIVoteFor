import factory

from parties.models import Party


class PartyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Party
        django_get_or_create = ('party_id',)


    party_id = 'PP01'
    party_name = "Test Party"


