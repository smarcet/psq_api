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

    allowed_devices = models.ManyToManyField("Device", related_name="allowed_exercises", blank=True)

    allowed_tutorials = models.ManyToManyField("Exercise", related_name="related_exercises", blank=True)

    def add_allowed_device(self, device):

        if device in self.allowed_devices.all():
            raise ModelValidationException(_("device {device_id} is already an allowed device").format(device_id=device.id))

        self.allowed_devices.add(device)
        self.save()

    def is_tutorial(self):
        return self.type == Exercise.TUTORIAL

    def is_tutorial_completed(self):
        return self.is_tutorial() and self.related_exercises.count() > 0

    def add_tutorial(self, exercise):
        if not exercise.is_tutorial():
            raise ModelValidationException(
                _("exercise {exercise_id} is not a tutorial").format(exercise_id=exercise.id))

        self.allowed_tutorials.add(exercise)
        self.save()

    def set_author(self, author):
        self.author = author
        self.save()

    def can_view(self, user):
        if self.author is not None and self.author.id == user.id:
            return True

        for device in self.allowed_devices.all():
            if device.is_allowed_user(user):
                return True

        return False

    def share_with(self, device):
        self.add_allowed_device(device)

