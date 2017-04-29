import json

import requests

from django.db import models
from django.conf import settings

from django_extensions.db.models import TimeStampedModel

FOUND_USEFUL_CHOICES = (
    ('YES', 'Yes'),
    ('NO', 'No'),
)

class Feedback(TimeStampedModel):
    found_useful = models.CharField(
        blank=True,
        max_length=100,
        choices=FOUND_USEFUL_CHOICES,
    )
    comments = models.TextField(blank=True)
    source_url = models.CharField(blank=True, max_length=800)



    def send_feedback_to_slack(self):
        msg_fmt = "Yay! Someone just left some feedback on the site! {extra}"
        color = "#2AB27B"

        if self.found_useful:
            message = msg_fmt.format(
                extra="They found what they were looking for! :+1:"
            )
        else:
            color = "#C7254E"
            message = msg_fmt.format(
                extra="They didn't find what they were looking for :-1:"
            )

        payload = {
            "fallback": message,
            "pretext": message,
            "color": color,
        }

        if self.comments:
            payload["fields"] = [
                {
                    # "title": "They said:",
                    "value": self.comments,
                    "short": False
                }
            ]
        if getattr(settings, 'SLACK_FEEDBACK_WEBHOOK_URL', None):
            url = settings.SLACK_FEEDBACK_WEBHOOK_URL
            requests.post(url, json.dumps(payload), timeout=2)
