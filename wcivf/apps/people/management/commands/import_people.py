from django.core.management.base import BaseCommand
from django.conf import settings

import requests

from people.models import Person


class Command(BaseCommand):
    def handle(self, **options):
        next_page = settings.YNR_BASE + '/api/v0.9/persons/?page_size=200'
        while next_page:
            req = requests.get(next_page)
            results = req.json()
            self.add_people(results)
            next_page = results.get('next')

    def add_people(self, results):
        for person in results['results']:
            person_obj, created = Person.objects.get_or_create_from_ynr(
                person)
            if created:
                print("Added new person: {0}".format(person['name']))
