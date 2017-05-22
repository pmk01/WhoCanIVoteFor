"""
Importer for all the corporate overlords
"""
import collections
import csv
import datetime

from django.core.management.base import BaseCommand
from django.db import transaction

from people.models import Person, AssociatedCompany

Company = collections.namedtuple(
    'Commpany',
    [
        'person_id',
        'name',
        'company_name',
        'company_number',
        'company_status',
        'role',
        'role_status',
        'role_appointed_date',
        'role_resigned_date'
    ]
)

def date_from_string(dt):
    """
    Given a date string DT, return a date object.
    """
    return datetime.datetime.strptime(dt, '%d %B %Y').date()


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            'filename',
            help='Path to the file with the hustings in it'
        )

    def delete_all_companies(self):
        """
        Clear our companies away.
        """
        AssociatedCompany.objects.all().delete()

    def create_company(self, data):
        """
        Create an individual associated company
        """
        person = Person.objects.get(ynr_id=data.person_id)
        companies = AssociatedCompany.objects.filter(
            person=person, company_number=data.company_number
        )

        # We only want one reference to a company - we're not actually
        # trying to shadow Companies House
        if companies.count() == 1:
            if companies[0].role == 'Director' and data.role == 'Secretary':
                print('Directorship already noted')
                return companies[0]
            elif companies[0].role == 'Secretary' and data.role == 'Director':
                print('Updating to Director')
                company = companies[0]
            else:
                if data.company_number == companies[0].company_number:
                    print('Change of company name')
                    # Use the most recent appointment
                    data_appointed = date_from_string(data.role_appointed_date)
                    if data_appointed > companies[0].role_appointed_date:
                        company = companies[0]
                    else:
                        return companies[0]
                else:
                    print(data)
                    raise ValueError('UNKNOWN COMPANY SITUATION - DIE')
        else:
            company = AssociatedCompany(
                person=person,
                company_number=data.company_number
            )

        appointed = date_from_string(data.role_appointed_date)

        resigned = None
        if data.role_resigned_date:
            resigned = date_from_string(data.role_resigned_date)

        company.company_name        = data.company_name
        company.company_status      = data.company_status
        company.role                = data.role
        company.role_appointed_date = appointed

        if resigned:
            company.role_resigned_date = resigned
        company.save()
        return company

    @transaction.atomic
    def handle(self, **options):
        """
        Entrypoint for our command.
        """
        self.delete_all_companies()
        counter = 0
        with open(options['filename'], 'r') as fh:
            reader = csv.reader(fh)
            next(reader)
            for row in reader:
                try:
                    data = Company(*row)
                except TypeError:
                    print(row)
                    raise
                associated_company = self.create_company(data)
                if associated_company:
                    counter += 1
                    print ('Created associated company {0} <{1}>'.format(
                        counter, associated_company)
                    )
