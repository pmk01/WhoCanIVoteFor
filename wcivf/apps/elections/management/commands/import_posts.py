from django.core.management.base import BaseCommand
from django.conf import settings

from elections.helpers import EEHelper, JsonPaginator
from elections.models import Post, PostElection, Election


class Command(BaseCommand):
    def get_replacement_ballot(self, ballot_id):
        replacement_ballot = None
        ee = EEHelper()
        ee_data = ee.get_data(ballot_id)
        if ee_data:
            replacement_ballot_id = ee_data["replaced_by"]
            if replacement_ballot_id:
                replacement_ballot = PostElection.objects.get(
                    ballot_paper_id=replacement_ballot_id
                )
        return replacement_ballot

    def get_metadata(self, ballot_id):
        ee = EEHelper()
        ee_data = ee.get_data(ballot_id)
        if ee_data:
            return ee_data["metadata"]
        return None

    def get_paginator(self, page1):
        return JsonPaginator(page1, self.stdout)

    def handle(self, **options):
        pages = self.get_paginator(
            settings.YNR_BASE + "/media/cached-api/latest/posts-000001.json"
        )
        for page in pages:
            self.add_posts(page)
        self.attach_cancelled_ballot_info()
        self.populate_any_non_by_elections_field()

    def add_posts(self, results):
        for post in results["results"]:
            post_obj, created = Post.objects.update_or_create_from_ynr(post)
            if created:
                self.stdout.write("Added new post: {0}".format(post["label"]))

    def attach_cancelled_ballot_info(self):
        # we need to do this as a post-process instead of in the manager
        # because if we're going to link 2 PostElection objects together
        # we need to be sure that both of them already exist in our DB
        cancelled_ballots = PostElection.objects.filter(cancelled=True)
        for cb in cancelled_ballots:
            cb.replaced_by = self.get_replacement_ballot(cb.ballot_paper_id)
            cb.metadata = self.get_metadata(cb.ballot_paper_id)
            cb.save()

    def populate_any_non_by_elections_field(self):
        qs = Election.objects.all().prefetch_related("postelection_set")
        for election in qs:
            any_non_by_elections = any(
                b.ballot_paper_id
                for b in election.postelection_set.all()
                if ".by." not in b.ballot_paper_id
            )
            election.any_non_by_elections = any_non_by_elections
            election.save()
