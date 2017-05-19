from django.views.generic import DetailView
from django.http import Http404
from django.db.models import Prefetch

from .models import Person, PersonPost


class PersonMixin(object):
    def get_object(self, queryset=None):
        return self.get_person(queryset)

    def get_person(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        pk = self.kwargs.get(self.pk_url_kwarg)
        queryset = queryset.filter(
            ynr_id=pk).prefetch_related(
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
                'election'
            )

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

        return obj


class EmailPersonView(PersonMixin, DetailView):
    template_name = "people/email_person.html"
    model = Person
