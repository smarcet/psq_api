from django.conf import settings
from django.db import models
from model_utils.models import TimeStampedModel
import uuid


class Video(TimeStampedModel):
    description = models.TextField()

    key = models.UUIDField(unique=True, null=False, default=uuid.uuid4)

    file = models.FileField(upload_to='videos')

    thumbnail = models.FileField(upload_to='thumbnails')

    # relations

    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               null=True, on_delete=models.SET_NULL,
                               related_name="created_videos")