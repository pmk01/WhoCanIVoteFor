from django.views.generic import TemplateView

from elections.models import Election
from people.models import PersonPost

class ResultsListView(TemplateView):
    template_name = "results/results.list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['elections'] = []
        election_qs = Election.objects.filter(
            current=True).order_by('election_date', '-election_weight')
        for election in election_qs:
            election_dict = {
                'election': election,
                'winners': PersonPost.objects.filter(
                    election=election, elected=True)
            }
            context['elections'].append(election_dict)
        return context
