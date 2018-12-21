"""
Expects a CSV with:

* `election id`
* `person id`
* `q1`
* `q2`
* `q3`
* `q[n]`

Where the values of the `Q` fields are an question and answer. The text before
the first newline will be assumed to be the question, and any remainder
will be taken as the answer.

"""

from django.core.management.base import BaseCommand
from django.db import transaction

import csv

from pledges.models import CandidatePledge
from people.models import Person
from elections.models import PostElection

PERSON_ID_TEXT = "person id"
ELECTION_ID_TEXT = "election id"


class Command(BaseCommand):
    help = "Import pledges from a CSV"

    def add_arguments(self, parser):
        parser.add_argument("filename", help="Path to the file with the manifestos")

    @transaction.atomic
    def handle(self, **options):
        # Delete all data first, as rows in the source might have been deleted
        CandidatePledge.objects.all().delete()
        with open(options["filename"], "r") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                try:
                    self.add_pledge(row)
                except:
                    print(row)

    def add_pledge(self, row):
        person = Person.objects.get(pk=row.pop(PERSON_ID_TEXT))
        post_election = PostElection.objects.get(
            ballot_paper_id=row.pop(ELECTION_ID_TEXT)
        )

        for k, v in row.items():
            question = []
            answer = []
            lines = v.splitlines()
            question = lines[0]
            if question.startswith("Q:"):
                question = question[2:]
            for line in lines[1:]:
                if line.startswith("A:"):
                    line = line[2:]
                answer.append(line.strip())

            CandidatePledge.objects.create(
                person=person,
                ballot_paper=post_election,
                question=question,
                answer="\n".join(answer),
            )
