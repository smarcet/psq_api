from django.conf import settings
from django.db import models
from model_utils.models import TimeStampedModel
from ..validators import validate_duration


class Tutorial(TimeStampedModel):
    title = models.CharField(max_length=255, blank=False, unique=True, null=True)

    notes = models.TextField()

    duration = models.PositiveIntegerField(blank=False, validators=[validate_duration, ])

    # relations

    taker = models.ForeignKey(settings.AUTH_USER_MODEL,
                              null=True, on_delete=models.SET_NULL,
                              related_name="accomplished_tutorials")

    exercise = models.ForeignKey("Exercise",
                                 null=True, blank=False, on_delete=models.SET_NULL,
                                 related_name="associated_tutorials")

    device = models.ForeignKey("Device",
                               null=True, blank=False, on_delete=models.SET_NULL,
                               related_name="associated_tutorials")

    def set_taker(self, user):
        self.taker = user
        self.save()
        return self

    def set_device(self, device):
        self.device = device
        self.save()
        return self