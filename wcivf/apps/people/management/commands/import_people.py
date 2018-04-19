from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings

import requests

from people.models import Person, PersonPost
from elections.models import Election, Post
from parties.models import Party


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '--recent',
            action='store_true',
            dest='recent',
            default=False,
            help='Import changes in the last `n` minutes',
        )

        parser.add_argument(
            '--recent-minutes',
            action='store',
            dest='recent_minutes',
            default=5,
            type=int,
            help='Number of minutes to look back for changes',
        )

    @transaction.atomic
    def handle(self, **options):
        self.all_parties = {p.party_id: p for p in Party.objects.all()}
        self.all_elections = {e.slug: e for e in Election.objects.all()}
        self.all_posts = {p.ynr_id: p for p in Post.objects.all()}

        if options['recent']:
            next_page = settings.YNR_BASE + \
                '/api/v0.9/persons/?page_size=200'
        else:
            self.existing_people = set(Person.objects.values_list('pk', flat=True))
            next_page = settings.YNR_BASE + \
                '/media/cached-api/latest/persons-000001.json'
        self.seen_people = set()


        if options['recent']:
            past_time = datetime.now() - timedelta(
                minutes=options['recent_minutes'])
            next_page = "{}&updated_gte={}".format(
                next_page, past_time.isoformat()
            )

        while next_page:
            print(next_page)
            req = requests.get(next_page)
            results = req.json()
            self.add_people(results)
            next_page = results.get('next')

        PersonPost.objects.filter(party=None).delete()
        if not options['recent']:
            deleted_ids = self.existing_people.difference(self.seen_people)
            Person.objects.filter(ynr_id__in=deleted_ids).delete()

    def add_people(self, results):
        for person in results['results']:
            person_obj = Person.objects.update_or_create_from_ynr(
                person,
                all_elections=self.all_elections,
                all_posts=self.all_posts,
                all_parties=self.all_parties
            )
            if person['memberships']:
                self.seen_people.add(person_obj.pk)
