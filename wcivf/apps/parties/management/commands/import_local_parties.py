from django.core.management.base import BaseCommand
from django.db import transaction

import csv

from parties.models import Party, LocalParty
from elections.models import Election, PostElection


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            'filename',
            help='Path to the file with the manifestos'
        )

    @transaction.atomic
    def handle(self, **options):
        # Delete all data first, as rows in the source might have been deleted
        LocalParty.objects.all().delete()
        with open(options['filename'], 'r') as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                party_id = row['party_id'].strip()
                # Try to get a post election
                try:
                    party = Party.objects.get(party_id='party:%s' % party_id)
                except Party.DoesNotExist:
                    print("Parent party not found with ID %s" % party_id)
                    continue

                post_elections = PostElection.objects.filter(
                    ballot_paper_id=row['election_id'])

                if not post_elections.exists():
                    # This might be an election ID, in that case,
                    # apply thie row to all post elections without
                    # info already
                    post_elections = PostElection.objects.filter(
                        election__slug=row['election_id'],
                    ).exclude(
                        localparty__parent=party
                    )

                self.add_local_party(row, party, post_elections)

    def add_local_party(self, row, party, post_elections):
        twitter = row['Twitter'].replace('https://twitter.com/', '')
        twitter = twitter.split('/')[0]
        twitter = twitter.split('?')[0]
        for post_election in post_elections:
            LocalParty.objects.update_or_create(
                parent=party,
                post_election=post_election,
                defaults={
                    'name': row['Local party name'],
                    'twitter': twitter,
                    'facebook_page': row['Facebook'],
                    'homepage': row['Website'],
                    'email': row['Email'],
                }
            )
