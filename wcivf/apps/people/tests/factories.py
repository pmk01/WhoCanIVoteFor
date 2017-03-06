import factory

from people.models import Person, PersonPost
from elections.tests.factories import ElectionFactory, PostFactory


class PersonFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Person

    ynr_id = "502"
    name = "Jane Smith"
    elections = factory.RelatedFactory(ElectionFactory)
    posts = factory.RelatedFactory(PostFactory)


class PersonPostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PersonPost

    person = factory.SubFactory(PersonFactory)
    post = factory.SubFactory(PostFactory)
    party = None
    elections = factory.RelatedFactory(ElectionFactory)
    list_position = None
