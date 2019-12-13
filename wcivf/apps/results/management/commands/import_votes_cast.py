from django.core.management.base import BaseCommand
from django.conf import settings

from core.helpers import show_data_on_error
from elections.helpers import JsonPaginator
from people.models import PersonPost
from elections.models import PostElection


class Command(BaseCommand):
    help = "Import results from the YNR API"

    def add_arguments(self, parser):
        parser.add_argument(
            "--since", action="store", dest="since", help="The election date"
        )

    def handle(self, *args, **options):
        base_url = "{}/api/next/results/?page_size=200".format(
            settings.YNR_BASE
        )
        if options["since"]:
            base_url = "{}&last_updated={}".format(base_url, options["since"])
        next_page = base_url
        for page in JsonPaginator(next_page, self.stdout):
            self.import_page(page["results"])

    def import_page(self, results):
        for resultset in results:
            post_election = PostElection.objects.get(
                ballot_paper_id=resultset["ballot"]["ballot_paper_id"]
            )
            for candidacy in resultset["candidate_results"]:
                with show_data_on_error("Membership", candidacy):
                    try:
                        person_post = PersonPost.objects.get(
                            post_election=post_election,
                            person__ynr_id=candidacy["person"]["id"],
                        )
                    except PersonPost.DoesNotExist:
                        continue
                    person_post.elected = candidacy["elected"]
                    person_post.votes_cast = candidacy["num_ballots"]
                    person_post.save()
