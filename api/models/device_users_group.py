from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel


class DeviceUsersGroup(TimeStampedModel):

    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50)

    device = models.ForeignKey("Device",
                               null=True, on_delete=models.SET_NULL,
                               related_name="user_groups")

    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="users_groups", blank=True)
