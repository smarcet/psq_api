from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Device(models.Model):

    serial = models.CharField(max_length=100)
    friendly_name = models.CharField(max_length=100)
    slots =  models.PositiveSmallIntegerField(default=3, blank=False, null=False)
    is_active = models.BooleanField(_('active'), default=True)

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="owned_devices")
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="allowed_devices")

    class Meta:
        app_label = 'api'

    def clean(self):
        pass

