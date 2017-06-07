from django.views.generic import TemplateView

from elections.models import Election
from results.models import ResultEvent


class ResultsListView(TemplateView):
    template_name = "results/results_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['elections'] = []
        election_qs = Election.objects.filter(
            current=True).order_by('election_date', '-election_weight')
        for election in election_qs:
            election_dict = {
                'election': election,
                'results': ResultEvent.objects.filter(
                    post_election__election=election,
                    person_posts__elected=True,
                ).order_by(
                    '-declaration_time'
                )
            }
            context['elections'].append(election_dict)
        return context
