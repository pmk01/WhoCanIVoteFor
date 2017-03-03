import factory

from elections.models import Election, Post, VotingSystem


class ElectionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Election
        django_get_or_create = ('slug',)


    slug = 'parl.2015'
    election_date = "2015-05-07"
    current = True
    name = "UK General Election 2015"


class PostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Post
        django_get_or_create = ('ynr_id',)

    ynr_id = "WMC:E14000647"
    label = "copeland"
    election = factory.SubFactory(ElectionFactory)

class VotingSystemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = VotingSystem

    slug = "FPTP"
    name = "First Past The Post"
    wikipedia_url = "https://en.wikipedia.org/wiki/First-past-the-post_voting"
    description = """
        A first-past-the-post (abbreviated FPTP, 1stP, 1PTP or FPP) voting
        method is one in which voters are required to indicate on the ballot
        the candidate of their choice, and the candidate who receives more
        votes than any other candidate wins.
    """
