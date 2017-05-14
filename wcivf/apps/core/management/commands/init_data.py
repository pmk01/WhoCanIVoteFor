import os

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '--full',
            action='store_true',
            dest='full',
            default=False,
            help='Import all data, not just people',
        )

    def handle(self, **options):

        if options['full']:
            commands = [
                ('import_elections', ),
                ('import_posts', ),
                ('import_parties', ),
                ('import_people', ),
            ]
        else:
            commands = [
                ('import_people', "--recent", "--recent-minutes=30"),
            ]



        for command in commands:
            print(" ".join(command))
            call_command(*command)

        # Unset dirty file if it exists
        if getattr(settings, 'CHECK_HOST_DIRTY', False):
            dirty_file_path = os.path.expanduser(
                getattr(settings, 'DIRTY_FILE_PATH'))

            if os.path.exists(dirty_file_path):
                os.remove(dirty_file_path)
