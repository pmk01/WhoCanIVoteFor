"""
Hack because Django makes it hard to use data migrations to do this :/
"""

from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site


class Command(BaseCommand):
    def handle(self, **options):
        Site.objects.all().update(domain="whocanivotefor.co.uk")
