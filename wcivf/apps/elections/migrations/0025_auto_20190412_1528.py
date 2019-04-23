# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def insert_voting_systems(apps, schema_editor):
    VotingSystem = apps.get_model("elections", "VotingSystem")
    db_alias = schema_editor.connection.alias
    VotingSystem.objects.using(db_alias).bulk_create(
        [
            VotingSystem(
                slug="AMS",
                name="Additional Member System",
                wikipedia_url="https://en.wikipedia.org/wiki/Additional_Member_System",
                description="In an election using the Additional Member System, each voter casts two votes: a vote for a candidate standing in their constituency (with or without an affiliated party), and a vote for a party list standing in a wider region made up of multiple constituencies.",
            ),
            VotingSystem(
                slug="FPTP",
                name="First-past-the-post",
                wikipedia_url="https://en.m.wikipedia.org/wiki/First-past-the-post_voting",
                description="A first-past-the-post (abbreviated FPTP, 1stP, 1PTP or FPP) or winner-takes-all election is one that is won by the candidate receiving more votes than any others.",
            ),
            VotingSystem(
                slug="sv",
                name="Supplementary Vote",
                wikipedia_url="https://en.wikipedia.org/wiki/Contingent_vote#Supplementary_vote",
                description="Under the supplementary vote (SV), voters express a first and second choice of candidate only, and, if no candidate receives an absolute majority of first-choice votes, all but the two leading candidates are eliminated and the votes of those eliminated redistributed according to their second-choice votes to determine the winner.",
            ),
            VotingSystem(
                slug="STV",
                name="Single Transferable Vote",
                wikipedia_url="https://en.wikipedia.org/wiki/Single_transferable_vote",
                description="The single transferable vote (STV) is a voting system designed to achieve proportional representation through ranked voting in multi-seat organizations or constituencies (voting districts).",
            ),
            VotingSystem(
                slug="PR-CL",
                name="Closed List",
                wikipedia_url="https://en.wikipedia.org/wiki/Closed_list",
                description="Closed list describes the variant of party-list proportional representation where voters can (effectively) only vote for political parties as a whole and thus have no influence on the party-supplied order in which party candidates are elected.",
            ),
        ]
    )


def delete_voting_systems(apps, schema_editor):
    VotingSystem = apps.get_model("elections", "VotingSystem")
    db_alias = schema_editor.connection.alias
    VotingSystem.objects.using(db_alias).get(slug="AMS").delete()
    VotingSystem.objects.using(db_alias).get(slug="FPTP").delete()
    VotingSystem.objects.using(db_alias).get(slug="sv").delete()
    VotingSystem.objects.using(db_alias).get(slug="STV").delete()
    VotingSystem.objects.using(db_alias).get(slug="PR-CL").delete()


class Migration(migrations.Migration):

    dependencies = [("elections", "0024_default_for_has_by_elections")]

    operations = [
        migrations.RunPython(insert_voting_systems, delete_voting_systems)
    ]
