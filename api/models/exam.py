from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel

class Exam(TimeStampedModel):

    notes = models.TextField()

    duration = models.DurationField()

    # relations

    taker = models.ForeignKey(settings.AUTH_USER_MODEL,
                              null=True, on_delete=models.SET_NULL,
                              related_name="taked_exams")

    evaluator = models.ForeignKey(settings.AUTH_USER_MODEL,
                              null=True, on_delete=models.SET_NULL,
                              related_name="evalutaed_exams")

    exercise = models.ForeignKey("Exercise",
                                 null=True, on_delete=models.SET_NULL,
                                 related_name="exams")

    device = models.ForeignKey("Device",
                                 null=True, on_delete=models.SET_NULL,
                                 related_name="exams")
