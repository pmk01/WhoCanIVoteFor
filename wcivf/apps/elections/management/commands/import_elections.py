from django.core.management.base import BaseCommand
from django.conf import settings

from elections.helpers import JsonPaginator
from elections.models import Election


class Command(BaseCommand):
    def get_paginator(self, page1):
        return JsonPaginator(page1, self.stdout)

    def handle(self, **options):
        pages = self.get_paginator(
            settings.YNR_BASE + "/api/v0.9/elections/?page_size=200"
        )
        for page in pages:
            self.add_elections(page)

        # Now import any metadata from EE
        self.import_metadata()

    def add_elections(self, results):
        for election in results["results"]:
            election_obj, created = Election.objects.update_or_create_from_ynr(election)
            if created:
                self.stdout.write("Added new election: {0}".format(election["name"]))

    def import_metadata(self):
        pages = self.get_paginator(
            "{}/api/elections/?current=true&metadata=1".format(settings.EE_BASE)
        )
        for page in pages:
            for election in page["results"]:
                try:
                    election_obj = Election.objects.get(slug=election["election_id"])
                    election_obj.metadata = election["metadata"]
                    election_obj.save()
                except:
                    pass
