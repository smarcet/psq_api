from django.conf import settings
from django.db import models
from model_utils.models import TimeStampedModel


class ExamPendingRequest(TimeStampedModel):
    duration = models.IntegerField(blank=True, null=True)
    # relations

    taker = models.ForeignKey(settings.AUTH_USER_MODEL,
                              null=True, on_delete=models.SET_NULL,
                              related_name="pending_exams_request")

    exercise = models.ForeignKey("Exercise",
                                 null=True, on_delete=models.SET_NULL,
                                 related_name="pending_exams_request")

    device = models.ForeignKey("Device",
                               null=True, on_delete=models.SET_NULL,
                               related_name="pending_exams_request")

    is_processed = models.BooleanField(default=False)

    def set_taker(self, user):
        self.taker = user
        self.save()
        return self

    def set_device(self, device):
        self.device = device
        self.save()
        return self

    def mark_as_processed(self):
        self.is_processed = True
