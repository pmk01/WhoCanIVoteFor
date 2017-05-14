import os

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    def handle(self, **options):

        commands = [
            'import_elections',
            'import_posts',
            'import_parties',
            'import_people',
            'import_wikipedia_bios',
        ]

        for command in commands:
            print(command)
            call_command(command)

        # Unset dirty file if it exists
        if getattr(settings, 'CHECK_HOST_DIRTY', False):
            dirty_file_path = os.path.expanduser(
                getattr(settings, 'DIRTY_FILE_PATH'))

            if os.path.exists(dirty_file_path):
                os.remove(dirty_file_path)
