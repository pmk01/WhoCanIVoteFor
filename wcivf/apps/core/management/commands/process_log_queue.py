from django.core.management.base import BaseCommand

from core.models import write_logged_postcodes


class Command(BaseCommand):
    def handle(self, **options):
        write_logged_postcodes()
