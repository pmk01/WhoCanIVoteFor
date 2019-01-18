from django.views.generic import TemplateView, DetailView
from django.http import Http404
from django.db.models import Prefetch
from django.apps import apps


from people.helpers import peopleposts_for_election_post


class ElectionsView(TemplateView):
    template_name = "elections/elections_view.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        Election = apps.get_model("elections.Election")
        all_elections = Election.objects.all().order_by(
            "-election_date", "election_type", "name"
        )

        context["past_elections"] = all_elections.filter(current=False)

        context["current_elections"] = all_elections.filter(current=True)

        return context


class ElectionView(DetailView):
    template_name = "elections/election_view.html"
    model = apps.get_model('elections.Election')
    pk_url_kwarg = "election"

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        pk = self.kwargs.get(self.pk_url_kwarg)
        PostElection = apps.get_model("elections.PostElection")
        queryset = queryset.filter(slug=pk).prefetch_related(
            Prefetch(
                "postelection_set",
                queryset=PostElection.objects.all()
                .select_related("election", "post")
                .order_by("post__label"),
            )
        )
        try:
            # Get the single item from the filtered queryset
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404(
                "No %(verbose_name)s found matching the query"
                % {"verbose_name": queryset.model._meta.verbose_name}
            )
        return obj


class PostView(DetailView):
    template_name = "elections/post_view.html"
    model = apps.get_model("elections.PostElection")

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        queryset = queryset.filter(
            ballot_paper_id=self.kwargs["election"]).select_related(
                'post', 'election'
            )

        try:
            # Get the single item from the filtered queryset
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404(
                "No %(verbose_name)s found matching the query"
                % {"verbose_name": queryset.model._meta.verbose_name}
            )
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['election'] = self.object.election
        context['person_posts'] = peopleposts_for_election_post(
            election=context['election'],
            post=self.object.post
        ).select_related(
            'post',
            'person',
            'person__cv',
            'party',
            'results',
        ).prefetch_related(
            'person__leaflet_set',
            'person__pledges',
        ).order_by('-elected')

        return context
