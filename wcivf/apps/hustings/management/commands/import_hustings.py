"""
Importer for all our important Hustings data
"""
import os
import collections
import csv
import datetime

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from elections.models import Election, PostElection
from hustings.models import Husting

Hust = collections.namedtuple(
    'Hust',
    [
        'electionid',
        'constituency',
        'gss_code',
        'title',
        'url',
        'date',
        'start_time',
        'end_time',
        'location',
        'postcode',
        'info'
    ]
)

def dt_from_string(dt):
    """
    Given a date string DT, return a datetime object.
    Try multiple strptime formats b/c Google sheets doesn't
    understand counting to three.
    """
    date = None
    try:
        date = datetime.datetime.strptime(dt, '%Y-%b-%d')
    except ValueError:
        date = datetime.datetime.strptime(dt, '%Y-%B-%d')
    if date:
        return timezone.make_aware(date, timezone.get_current_timezone())


def stringy_time_to_inty_time(stringy_time):
    """
    Given a string in the form HH:MM return integer values for hour
    and minute.
    """
    hour, minute = stringy_time.split(':')
    return int(hour), int(minute)


def set_time_string_on_datetime(dt, time_string):
    """
    Given a datetime DT and a string in the form HH:MM return a
    new datetime with the hour and minute set according to
    TIME_STRING
    """
    hour, minute = stringy_time_to_inty_time(time_string)
    dt = dt.replace(hour=hour, minute=minute)
    return dt


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            'filename',
            help='Path to the file with the hustings in it'
        )
        parser.add_argument(
            '--quiet',
            action='store_true',
            dest='quiet',
            default=False,
            help='Only output errors',
        )

    def delete_all_hustings(self):
        """
        Clear our hustings away.
        """
        Husting.objects.all().delete()

    def create_husting(self, data):
        """
        Create an individual husting
        """
        starts = dt_from_string(data.date)
        ends = None
        if data.start_time:
            starts = set_time_string_on_datetime(
                starts, data.start_time
            )
        if data.end_time:
            ends = dt_from_string(data.date)
            ends = set_time_string_on_datetime(
                ends, data.end_time
            )
        # This seems absurd. Maybe there's a better way to spell this
        # in the ORM ? Maybe I don't understand the data model properly?
        election = Election.objects.get(slug=data.electionid)
        try:
            post_election = election.postelection_set.get(
                post__area_name=data.constituency)
        except PostElection.DoesNotExist:
            self.not_a_constituency_friend.append(data.constituency)
            return None

        husting = Husting(
            post_election=post_election,
            title=data.title,
            url=data.url,
            starts= starts,
            ends=ends,
            location=data.location,
            postcode=data.postcode,
            postevent_url=data.info
        )
        husting.save()
        return husting

    @transaction.atomic
    def handle(self, **options):
        """
        Entrypoint for our command.
        """
        if options['quiet']:
            self.stdout = open(os.devnull, "w")

        self.delete_all_hustings()
        hustings_counter = 0
        self.not_a_constituency_friend = []
        with open(options['filename'], 'r') as fh:
            reader = csv.reader(fh)
            next(reader)
            for row in reader:
                data = Hust(*row)
                husting = self.create_husting(data)
                if husting:
                    hustings_counter += 1
                    self.stdout.write('Created husting {0} <{1}>'.format(
                        hustings_counter, husting)
                    )

        if len(self.not_a_constituency_friend) > 0:
            self.stderr.write(
                '\n\n\nUnfortunately your data contains "hustings" for ' \
                'things that are not a constituency. They have been ' \
                'ignored. Please do complain to your upstream data source.'
            )
            for place in self.not_a_constituency_friend:
                self.stderr.write(place)
