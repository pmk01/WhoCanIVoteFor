from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.conf import settings

from elections.helpers import JsonPaginator
from elections.models import Election


class Command(BaseCommand):
    def get_paginator(self, page1):
        return JsonPaginator(page1, self.stdout)

    def handle(self, **options):
        pages = self.get_paginator(
            settings.YNR_BASE + "/api/next/elections/?page_size=200"
        )
        for page in pages:
            self.add_elections(page)

        # Now import any other bits from EE that aren't in YNR
        self.import_extras()

    def add_elections(self, results):
        for election in results["results"]:
            election_obj, created = Election.objects.update_or_create_from_ynr(
                election
            )
            if created:
                self.stdout.write(
                    "Added new election: {0}".format(election["name"])
                )

    def import_extras(self):
        poll_open_date_gte = str(date.today() - timedelta(days=30))
        pages = self.get_paginator(
            f"{settings.EE_BASE}/api/elections/?poll_open_date__gte={poll_open_date_gte}"
        )
        for page in pages:
            for election in page["results"]:
                try:
                    election_obj = Election.objects.get(
                        slug=election["election_id"]
                    )
                    election_obj.metadata = election["metadata"]
                    if election["voting_system"]:
                        election_obj.voting_system_id = election[
                            "voting_system"
                        ]["slug"]
                    election_obj.save()
                except Election.DoesNotExist:
                    pass
