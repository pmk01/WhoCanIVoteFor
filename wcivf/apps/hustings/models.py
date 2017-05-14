"""
Models for Hustings
"""
from django.db import models

from elections.models import Post


class Husting(models.Model):
    """
    A Husting.
    """
    post    = models.ForeignKey(Post)
    title   = models.CharField(max_length=250)
    url     = models.URLField()
    starts  = models.DateTimeField()
    ends    = models.DateTimeField(blank=True, null=True)
    location = models.CharField(max_length=250, blank=True, null=True)
    postcode = models.CharField(max_length=10, blank=True, null=True)
