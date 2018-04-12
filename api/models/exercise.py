from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel


class Exercise(TimeStampedModel):

    title = models.CharField(max_length=100)

    abstract = models.TextField()

    max_duration = models.DurationField()

    REGULAR = 1
    TUTORIAL = 2
    TYPE_CHOICES = (
        (REGULAR, 'Regular'),
        (TUTORIAL, 'Tutorial')
    )

    type = models.PositiveSmallIntegerField(choices=TYPE_CHOICES, null=True, blank=True)

    # relations

    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                              null=True, on_delete=models.SET_NULL,
                              related_name="created_exercises")

    original_device = models.ForeignKey("Device",
                               null=True, on_delete=models.SET_NULL,
                               related_name="owned_exercises")

    allowed_devices = models.ManyToManyField("Device", related_name="allowed_exercises", blank=True)
