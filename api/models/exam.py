from django.conf import settings
from django.db import models
from model_utils.models import TimeStampedModel
from ..validators import validate_duration
from datetime import datetime
from ..models import ModelValidationException
from django.utils.translation import ugettext_lazy as _


class Exam(TimeStampedModel):

    notes = models.TextField()

    duration = models.IntegerField(blank=False, validators=[validate_duration, ])

    approved = models.BooleanField(default=False)
    evaluated = models.BooleanField(default=False)
    eval_date = models.DateTimeField(null=True)

    video_views = models.IntegerField(default=0)
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

    video_shares = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)

    def add_share(self, user):

        if user in self.video_shares.all():
            raise ModelValidationException(_("user %s is already on videos shares") % user.id)

        if user.id == self.taker.id:
            raise ModelValidationException(_("user %s is already owner") % user.id)

        self.video_shares.add(user)
        self.save()

    def can_reproduce(self, user):
        if self.taker == user:
            return True
        if user in self.video_shares.all():
            return True
        return False

    def add_view(self):
        self.video_views = self.video_views + 1
        self.save()

    def remove_admin(self, user):
        if user not in self.video_shares.all():
            raise ModelValidationException(_("user %s is not on video shares") % user.id)
        self.video_shares.remove(user)
        self.save()

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
        self.eval_date = datetime.utcnow()

    def reject(self, notes=None):
        self.approved = False
        self.evaluated = True
        self.notes = notes or ''
        self.eval_date = datetime.utcnow()
