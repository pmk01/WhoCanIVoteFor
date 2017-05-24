from django.db import models

from people.models import Person


class Leaflet(models.Model):
    person = models.ForeignKey(Person)
    leaflet_id = models.IntegerField()
    thumb_url = models.URLField(null=True, blank=True)
    date_uploaded_to_electionleaflets = models.DateTimeField(null=True,
                                                             blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
