from django.db import models
from model_utils.models import TimeStampedModel
from django.utils.timezone import now


class MailRequest(TimeStampedModel):
    to_address = models.EmailField()
    from_address = models.EmailField()
    subject = models.CharField(max_length=255)
    body = models.TextField()
    sent_date = models.DateTimeField(null=True)
    is_sent = models.BooleanField(default=False)

    def mark_as_sent(self):
        self.is_sent = True
        self.sent_date = now()

