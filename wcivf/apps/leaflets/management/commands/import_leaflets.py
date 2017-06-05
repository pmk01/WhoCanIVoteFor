from datetime import datetime

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone as tz

import requests

from people.models import Person
from leaflets.models import Leaflet


class Command(BaseCommand):

    @transaction.atomic
    def handle(self, **options):
        url = 'https://electionleaflets.org/'
        url += 'api/latest_by_person?format=json'
        req = requests.get(url)
        results = req.json()
        self.add_leaflets(results)

    def add_leaflets(self, results):
        for person_id in results:
            leaflets = results[person_id]
            for l in leaflets:
                thumb_url = l['first_page_thumb']
                leaflet_id = l['pk']
                d = datetime.strptime(l['date_uploaded'].split('.')[0],
                                      "%Y-%m-%dT%H:%M:%S")
                dt_aware = tz.make_aware(d, tz.get_current_timezone())
                try:
                    person = Person.objects.get(
                        ynr_id=person_id)
                    leaflet_obj, created = Leaflet.objects.update_or_create(
                        person=person,
                        leaflet_id=leaflet_id
                    )
                    leaflet_obj.thumb_url = thumb_url
                    leaflet_obj.date_uploaded_to_electionleaflets = dt_aware
                    leaflet_obj.save()
                except Person.DoesNotExist:
                    print('No person found with id %s' % person_id)
