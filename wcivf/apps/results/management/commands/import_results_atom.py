import feedparser
import requests

from django.core.management.base import BaseCommand
from django.conf import settings

from people.models import PersonPost


class Command(BaseCommand):
    help = "Import results from the YNR Atom feed"

    def handle(self, *args, **options):
        feed_url = "{}/results/all.atom".format(settings.YNR_BASE)
        req = requests.get(feed_url)
        feed = feedparser.parse(req.text)
        for entry in feed['entries']:

            person_post = PersonPost.objects.get(
                person_id=entry['winner_person_id'],
                election__slug=entry['election_slug'],
                post__ynr_id=entry['post_id'],
                )
            if int(entry['retraction']) == 1:
                # The result has been retracted due to an error
                # Unset the elected flag
                person_post.elected = None
            else:
                person_post.elected = True
            person_post.save()
