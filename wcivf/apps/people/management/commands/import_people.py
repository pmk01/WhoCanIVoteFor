import os
import json
import tempfile
import shutil

from dateutil.parser import parse

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
            "--recent",
            action="store_true",
            dest="recent",
            default=False,
            help="Import changes in the last `n` minutes",
        )

        parser.add_argument(
            "--since",
            action="store",
            dest="since",
            type=self.valid_date,
            help="Import changes since [datetime]",
        )
        parser.add_argument(
            "--update-info-only",
            action="store_true",
            help="Only update person info, not posts",
        )

    def valid_date(self, value):
        return parse(value)

    def handle(self, **options):
        self.options = options
        self.dirpath = tempfile.mkdtemp()

        try:
            self.download_pages()
            self.add_to_db()
        finally:
            shutil.rmtree(self.dirpath)

    @transaction.atomic
    def add_to_db(self):
        self.all_parties = {p.party_id: p for p in Party.objects.all()}
        self.all_elections = {e.slug: e for e in Election.objects.all()}
        self.all_posts = {p.ynr_id: p for p in Post.objects.all()}
        self.existing_people = set(Person.objects.values_list("pk", flat=True))
        self.seen_people = set()

        files = [f for f in os.listdir(self.dirpath) if f.endswith(".json")]
        for file in files:
            self.stdout.write("Importing {}".format(file))
            with open(os.path.join(self.dirpath, file), "r") as f:
                results = json.loads(f.read())
                self.add_people(
                    results, update_info_only=self.options["update_info_only"]
                )

        PersonPost.objects.filter(party=None).delete()
        if not self.options["recent"] or self.options["update_info_only"]:
            deleted_ids = self.existing_people.difference(self.seen_people)
            Person.objects.filter(ynr_id__in=deleted_ids).delete()

    def save_page(self, url, page):
        # get the file name from the page number
        if "cached-api" in url:
            filename = url.split("/")[-1]
        else:
            if "page=" in url:
                page_number = url.split("page_size=")[1].split("&")[0]

            else:
                page_number = 1
            filename = "page-{}.json".format(page_number)
        file_path = os.path.join(self.dirpath, filename)

        # Save the page
        with open(file_path, "w") as f:
            f.write(page)

    def download_pages(self):
        if self.options["recent"] or self.options["since"]:
            if self.options["recent"]:
                past_time_str = Person.objects.latest().last_updated
            if self.options["since"]:
                past_time_str = self.options["since"]

            next_page = (
                settings.YNR_BASE
                + "/api/next/persons/?page_size=200&updated_gte={}".format(
                    past_time_str.isoformat()
                )
            )

        else:
            next_page = (
                settings.YNR_BASE
                + "/media/cached-api/latest/persons-000001.json"
            )

        while next_page:
            self.stdout.write("Downloading {}".format(next_page))
            req = requests.get(next_page)
            req.raise_for_status()
            page = req.text
            results = req.json()
            self.save_page(next_page, page)
            next_page = results.get("next")

    def add_people(self, results, update_info_only=False):
        for person in results["results"]:
            person_obj = Person.objects.update_or_create_from_ynr(
                person,
                all_elections=self.all_elections,
                all_posts=self.all_posts,
                all_parties=self.all_parties,
                update_info_only=update_info_only,
            )
            if person["memberships"]:
                self.seen_people.add(person_obj.pk)
