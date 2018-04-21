from django.conf import settings
from django.db import models
from model_utils.models import TimeStampedModel
from ..validators import validate_duration


class Tutorial(TimeStampedModel):

    title = models.CharField(max_length=255, blank=False, unique=True)

    notes = models.TextField()

    duration = models.IntegerField(blank=False, validators=[validate_duration,])

    # relations

    taker = models.ForeignKey(settings.AUTH_USER_MODEL,
                              null=True, on_delete=models.SET_NULL,
                              related_name="accomplished_tutorials")

    exercise = models.ForeignKey("Exercise",
                                 null=True, on_delete=models.SET_NULL,
                                 related_name="associated_tutorials")

    device = models.ForeignKey("Device",
                                 null=True, on_delete=models.SET_NULL,
                                 related_name="associated_tutorials")
