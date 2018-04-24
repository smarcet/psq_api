from django.conf import settings
from django.db import models
from model_utils.models import TimeStampedModel
from ..validators import validate_duration


class Exam(TimeStampedModel):

    notes = models.TextField()

    duration = models.IntegerField(blank=False, validators=[validate_duration,])

    approved = models.BooleanField(default=False)

    # relations

    taker = models.ForeignKey(settings.AUTH_USER_MODEL,
                              null=True, on_delete=models.SET_NULL,
                              related_name="taked_exams")

    evaluator = models.ForeignKey(settings.AUTH_USER_MODEL,
                              null=True, on_delete=models.SET_NULL,
                              related_name="evaluated_exams")

    exercise = models.ForeignKey("Exercise",
                                 null=True, on_delete=models.SET_NULL,
                                 related_name="exams")

    device = models.ForeignKey("Device",
                                 null=True, on_delete=models.SET_NULL,
                                 related_name="exams")
