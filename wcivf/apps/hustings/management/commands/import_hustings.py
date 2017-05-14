"""
Importer for all our important Hustings data
"""
import collections
import csv
import datetime

from django.core.management.base import BaseCommand

from elections.models import Election, Post, PostElection
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
    try:
        return datetime.datetime.strptime(dt, '%Y-%b-%d')
    except ValueError:
        return datetime.datetime.strptime(dt, '%Y-%B-%d')


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
            post = election.postelection_set.get(
                post__area_name=data.constituency).post
        except PostElection.DoesNotExist:
            self.not_a_constituency_friend.append(data.constituency)
            return None

        husting = Husting(
            post=post,
            title=data.title,
            url=data.url,
            starts= starts,
            ends=ends,
            location=data.location,
            postcode=data.postcode
        )
        husting.save()
        return husting

    def handle(self, **options):
        """
        Entrypoint for our command.
        """
        self.delete_all_hustings()
        self.not_a_constituency_friend = []
        with open(options['filename'], 'r') as fh:
            reader = csv.reader(fh)
            next(reader)
            for row in reader:
                data = Hust(*row)
                husting = self.create_husting(data)
                if husting:
                    print ('Created husting {0} {1}'.format(husting.id, husting))

        if len(self.not_a_constituency_friend) > 0:
            print(
                '\n\n\nUnfortunately your data contains "hustings" for ' \
                'things that are not a constituency. They have been ' \
                'ignored. Please do complain to your upstream data source.'
            )
            for place in self.not_a_constituency_friend:
                print(place)
