from django.core.management.base import BaseCommand
from django.conf import settings

import requests

from elections.models import Election


class Command(BaseCommand):
    def handle(self, **options):
        next_page = settings.YNR_BASE + '/api/v0.9/elections/'
        while next_page:
            req = requests.get(next_page)
            results = req.json()
            self.add_elections(results)
            next_page = results.get('next')

        # Now import any metadata from EE
        self.import_metadata()

    def add_elections(self, results):
        for election in results['results']:
            election_obj, created = Election.objects.update_or_create_from_ynr(
                election)
            if created:
                print("Added new election: {0}".format(election['name']))

    def import_metadata(self):
        next_page = '{}/api/elections/?current=true&metadata=1'.format(
            settings.EE_BASE
        )
        while next_page:
            req = requests.get(next_page)
            results = req.json()
            next_page = results.get('next')
            for election in results['results']:
                try:
                    election_obj = Election.objects.get(
                        slug=election['election_id'])
                    election_obj.metadata = election['metadata']
                    election_obj.save()
                except:
                    pass

