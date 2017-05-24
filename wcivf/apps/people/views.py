from django.views.generic import DetailView
from django.http import Http404
from django.db.models import Prefetch
from django.utils.html import strip_tags

from .models import Person, PersonPost
from elections.models import PostElection
from leaflets.models import Leaflet


class PersonMixin(object):
    def get_object(self, queryset=None):
        return self.get_person(queryset)

    def get_person(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        pk = self.kwargs.get(self.pk_url_kwarg)
        queryset = queryset.filter(
            ynr_id=pk).select_related(
                'cv'
            ).prefetch_related(
                Prefetch(
                    'personpost_set',
                    queryset=PersonPost.objects.all().select_related(
                        'election', 'post', 'party')
                )
            )

        try:
            # Get the single item from the filtered queryset
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404("No %(verbose_name)s found matching the query" %
                          {'verbose_name': queryset.model._meta.verbose_name})

        obj.current_posts = PersonPost.objects.filter(
            person=obj, election__current=True).select_related(
                'party',
                'post',
                'election',
            )
        obj.leaflets = Leaflet.objects.filter(person=obj) \
            .order_by('-date_uploaded_to_electionleaflets')[:3]

        return obj


class PersonView(DetailView, PersonMixin):
    model = Person

    def get_object(self, queryset=None):
        obj = self.get_person(queryset)

        obj.past_posts = PersonPost.objects.filter(
            person=obj, election__current=False).select_related(
                'party',
                'post',
                'election'
            )
        obj.intro = self.get_intro(obj)
        obj.text_intro = strip_tags(obj.intro)

        return obj

    def get_intro(self, person):
        intro = [person.name]
        post = None
        if person.current_posts:
            post = person.current_posts[0]
            intro.append('is')
        elif person.past_posts:
            post = person.past_posts[0]
            intro.append('was')
        if post:
            party = post.party
            if party:
                if party.party_name == "Independent":
                    intro.append('an independent candidate')
                elif party.party_name == "Speaker seeking re-election":
                    intro.append('the Speaker seeking re-election')
                else:
                    intro.append('a candidate for the')
                    str = '<a href="' + party.get_absolute_url() + '">'
                    str += party.party_name + '</a>'
                    intro.append(str)
            else:
                intro.append('a candidate')
            intro.append('in')
            if post.post.organization == 'House of Commons of the United Kingdom':
                intro.append('the constituency of')
            try:
                postelection = PostElection.objects.get(post=post.post)
                str = '<a href="' + postelection.get_absolute_url() + '">'
                str += post.post.label + '</a>'
            except PostElection.DoesNotExist:
                str = post.post.label
            str += ' in the <a href="' + post.election.get_absolute_url()
            str += '">' + post.election.name + '</a>'
            intro.append(str)
        return ' '.join(intro)


class EmailPersonView(PersonMixin, DetailView):
    template_name = "people/email_person.html"
    model = Person
