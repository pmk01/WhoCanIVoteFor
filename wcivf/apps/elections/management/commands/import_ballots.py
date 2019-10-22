from django.core.management.base import BaseCommand

from elections.import_helpers import YNRBallotImporter


class Command(YNRBallotImporter, BaseCommand):
    def handle(self, **options):
        importer = YNRBallotImporter(stdout=self.stdout)
        importer.do_import()
