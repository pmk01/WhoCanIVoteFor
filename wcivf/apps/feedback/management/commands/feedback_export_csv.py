from datetime import datetime, timedelta
import csv
import json
import random
from django.utils import timezone

import requests

from django.core.management.base import BaseCommand
from django.conf import settings

from feedback.models import Feedback

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '--since-date',
            action='store',
            dest='since_date',
            type=str,
            help='Feedback since the given date'
        )


    def handle(self, **options):
        since_date = options.get('since_date', None)

        feedback_to_export = Feedback.objects.all()

        if since_date:
            date = datetime.strptime(since_date, '%Y-%m-%d')
            date = timezone.make_aware(date, timezone.get_current_timezone())
            feedback_to_export = feedback_to_export.filter(
                created__gte=date)

        fieldnames = [
            'created',
            'found_useful',
            'comments',
            'source_url',
        ]
        out = csv.DictWriter(self.stdout, fieldnames=fieldnames)
        out.writeheader()
        for feedback in feedback_to_export:
            out.writerow({
                'created': feedback.created,
                'found_useful': feedback.found_useful,
                'comments': feedback.comments,
                'source_url': feedback.source_url,
            })
