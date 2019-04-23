from datetime import datetime

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone as tz

import requests

from people.models import Person
from peoplecvs.models import CV


class Command(BaseCommand):
    @transaction.atomic
    def handle(self, **options):
        url = "http://cv.democracyclub.org.uk/cvs.json"
        req = requests.get(url)
        results = req.json()
        self.add_cvs(results)

    def add_cvs(self, results):
        for result in results:
            id = result["person_id"]
            thumb_url = None
            if "thumb" in result:
                thumb_url = result["thumb"]["url"]
            try:
                person = Person.objects.get(ynr_id=id)
                cv_obj, created = CV.objects.update_or_create(person=person)
                cv_obj.url = result["url"]
                cv_obj.thumb_url = thumb_url
                d = datetime.strptime(
                    result["last_modified"], "%Y-%m-%dT%H:%M:%S"
                )
                dt_aware = tz.make_aware(d, tz.get_current_timezone())
                cv_obj.last_modified = dt_aware
                cv_obj.save()
            except Person.DoesNotExist:
                print("No person found with id %s" % result["person_id"])
