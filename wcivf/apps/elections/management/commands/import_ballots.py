from django.core.management.base import BaseCommand

from elections.import_helpers import YNRBallotImporter


class Command(YNRBallotImporter, BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--current",
            action="store_true",
            dest="current",
            default=False,
            help="Only import ballots that are'current'",
        )
        parser.add_argument(
            "--force-all-metadata",
            action="store_true",
            dest="force_metadata",
            default=False,
            help="Imports all metadata from EE for all elections",
        )

    def handle(self, **options):
        importer = YNRBallotImporter(
            stdout=self.stdout,
            current_only=options["current"],
            force_metadata=options["force_metadata"],
        )
        importer.do_import()
