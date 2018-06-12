from django.conf import settings
from django.db import models
from model_utils.models import TimeStampedModel
from ..validators import validate_duration
from django.utils.timezone import now


class Exam(TimeStampedModel):
    notes = models.TextField()

    duration = models.IntegerField(blank=False, validators=[validate_duration, ])

    approved = models.BooleanField(default=False)
    evaluated = models.BooleanField(default=False)
    eval_date = models.DateTimeField(null=True)

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

    def set_taker(self, user):
        self.taker = user
        self.save()
        return self

    def set_evaluator(self, user):
        self.evaluator = user
        self.save()
        return self

    def set_device(self, device):
        self.device = device
        self.save()
        return self

    def approve(self, notes=None):
        self.approved = True
        self.evaluated = True
        self.notes = notes or ''
        self.eval_date = now()

    def reject(self, notes=None):
        self.approved = True
        self.evaluated = True
        self.notes = notes or ''
        self.eval_date = now()
