from django.db import models

from django_extensions.db.models import TimeStampedModel

class BaseNotification(TimeStampedModel):
    """
    We need a postcode and email address at the very least
    """
    postcode = models.CharField(blank=False, max_length=15)
    email = models.EmailField()

    class Meta:
        abstract = True


class ElectionNotification(BaseNotification):
    pass
