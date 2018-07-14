from django.conf import settings
from django.db import models
from model_utils.models import TimeStampedModel
from ..models import Exercise, Device
from backend.settings import STREAMING_SERVER_DASH_TPL, STREAMING_SERVER_HLS_TPL


class DeviceBroadCast(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             blank=True,
                             null=True, on_delete=models.SET_NULL,
                             related_name="device_broadcasts")

    exercise = models.ForeignKey(Exercise,
                                 blank=True,
                                 null=True, on_delete=models.SET_NULL,
                                 related_name="device_broadcasts")

    device = models.ForeignKey(Device,
                               blank=True,
                               null=True, on_delete=models.SET_NULL,
                               related_name="broadcasts")

    start_at = models.DateTimeField(null=True)

    ends_at = models.DateTimeField(null=True)

    def get_hls_stream(self):
        return STREAMING_SERVER_HLS_TPL.format(slug=self.device.slug)

    def get_dash_stream(self):
        return STREAMING_SERVER_DASH_TPL.format(slug=self.device.slug)
