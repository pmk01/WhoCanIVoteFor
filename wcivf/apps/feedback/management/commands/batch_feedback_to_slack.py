from django.core.management.base import BaseCommand
from django.conf import settings
from datetime import datetime, timedelta

import requests
import json
from feedback.models import Feedback

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '--hours-ago',
            action='store',
            dest='hours',
            default=1,
            help='Hours to look back for feedback'
        )

    def handle(self, **options):
        past_time = datetime.now() - timedelta(hours=int(options['hours']))

        msg_fmt = "Aggregated site feedback since {time} - :+1: x{found}, :-1: x{not_found} - yay!"

        recent_feedback = list(Feedback.objects.filter(created__gte=past_time))

        found     = len([feedback for feedback in recent_feedback if feedback.found_useful == 'YES'])
        not_found = len([feedback for feedback in recent_feedback if feedback.found_useful != 'YES'])

        message = msg_fmt.format(
            time      = past_time.strftime("%H:%M"),
            found     = found,
            not_found = not_found
        )

        payload = {
            "fallback": message,
            "pretext": message,
            "color": "#2AB27B" if found >= not_found else "#C7254E",
        }

        comments = [ { "title" : "<{0}{1}>".format(settings.CANONICAL_URL, feedback.source_url), "value": feedback.comments, "short": False }
                     for feedback in recent_feedback if feedback.comments is not None][0:5]

        if comments:
            payload["fields"] = comments

        if getattr(settings, 'SLACK_FEEDBACK_WEBHOOK_URL', None):
            url = settings.SLACK_FEEDBACK_WEBHOOK_URL
            requests.post(url, json.dumps(payload), timeout=2)