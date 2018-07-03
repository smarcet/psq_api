from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel
from ..models import ModelValidationException
from ..validators import validate_max_duration


class Exercise(TimeStampedModel):

    title = models.CharField(max_length=255, blank=False, unique=True)

    abstract = models.TextField(blank=False)

    max_duration = models.IntegerField(blank=False, validators=[validate_max_duration,])

    REGULAR = 1
    TUTORIAL = 2

    TYPE_CHOICES = (
        (REGULAR, 'Regular'),
        (TUTORIAL, 'Tutorial')
    )

    type = models.PositiveSmallIntegerField(choices=TYPE_CHOICES, null=True, blank=False, default=REGULAR)

    # relations

    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               null=True, on_delete=models.SET_NULL,
                               related_name="created_exercises")

    original_device = models.ForeignKey("Device",
                                        null=True, on_delete=models.SET_NULL,
                                        related_name="owned_exercises")

    allowed_devices = models.ManyToManyField("Device", related_name="allowed_exercises", blank=True)

    created_from_tutorial = models.ForeignKey("Exercise",
                                              null=True, on_delete=models.SET_NULL,
                                              blank=True
                                              )

    def add_allowed_device(self, device):

        if device in self.allowed_devices.all():
            raise ModelValidationException(_("device {device_id} is already an allowed device").format(device_id=device.id))

        self.allowed_devices.add(device)
        self.save()

    def set_author(self, author):
        self.author = author
        self.save()

    def set_original_device(self, original_device):
        if original_device is None:
            raise ModelValidationException(
                _("original device could not be null"))

        self.original_device = original_device
        self.save()
