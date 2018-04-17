from django.core.management.base import BaseCommand
from django.db import transaction

import csv

from parties.models import Party, LocalParty
from elections.models import Election


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
                election = Election.objects.get(
                        slug=row['election_id'])
                try:
                    party = Party.objects.get(party_id='party:%s' % party_id)
                    self.local_party(row, party, election)
                except Party.DoesNotExist:
                    print("Parent party not found with ID %s" % party_id)

    def add_manifesto(self, row, party, election):
        country = row.get('country', 'UK').strip()
        if 'local.' in election.slug:
            country = "Local"
        language = row.get('language', 'English').strip()
        manifesto_obj, created = Manifesto.objects.update_or_create(
            election=election, party=party, country=country, language=language,
            web_url=row['web'].strip(), pdf_url=row['pdf'].strip())
        manifesto_obj.save()
