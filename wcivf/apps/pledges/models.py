from django.db import models


class CandidatePledge(models.Model):
    person = models.ForeignKey("people.person", related_name="pledges")
    ballot_paper = models.ForeignKey("elections.PostElection")
    question = models.TextField(blank=True)
    answer = models.TextField(blank=True)
