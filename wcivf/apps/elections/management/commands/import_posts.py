from django.core.management.base import BaseCommand
from django.conf import settings

import requests

from elections.helpers import EEHelper
from elections.models import Post, PostElection


class Command(BaseCommand):

    def get_replacement_ballot(self, ballot_id):
        replacement_ballot = None
        ee = EEHelper()
        ee_data = ee.get_data(ballot_id)
        if ee_data:
            replacement_ballot_id = ee_data['replaced_by']
            if replacement_ballot_id:
                replacement_ballot = PostElection.objects.get(
                    ballot_paper_id=replacement_ballot_id
                )
        return replacement_ballot

    def get_metadata(self, ballot_id):
        ee = EEHelper()
        ee_data = ee.get_data(ballot_id)
        if ee_data:
            return ee_data['metadata']
        return None

    def handle(self, **options):
        next_page = settings.YNR_BASE \
            + '/media/cached-api/latest/posts-000001.json'
        while next_page:
            print(next_page)
            req = requests.get(next_page)
            if req.status_code != 200:
                print(req.url)
                print(req.content)
            results = req.json()
            self.add_posts(results)
            next_page = results.get('next')
        self.attach_cancelled_ballot_info()

    def add_posts(self, results):
        for post in results['results']:
            post_obj, created = Post.objects.update_or_create_from_ynr(
                post)
            if created:
                print("Added new post: {0}".format(post['label']))

    def attach_cancelled_ballot_info(self):
        # we need to do this as a post-process instead of in the manager
        # because if we're going to link 2 PostElection objects together
        # we need to be sure that both of them already exist in our DB
        cancelled_ballots = PostElection.objects.filter(cancelled=True)
        for cb in cancelled_ballots:
            cb.replaced_by = self.get_replacement_ballot(cb.ballot_paper_id)
            cb.metadata = self.get_metadata(cb.ballot_paper_id)
            cb.save()
