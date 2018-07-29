from django.conf import settings
from django.db import models
from model_utils.models import TimeStampedModel
import uuid
from storages.backends.gcloud import GoogleCloudStorage


class Video(TimeStampedModel):
    description = models.TextField()

    type = models.TextField()

    key = models.UUIDField(unique=True, null=False, default=uuid.uuid4)

    file = models.FileField(
        storage=GoogleCloudStorage(bucket_name='psq_videos'),
        upload_to='videos')

    # relations

    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               null=True, on_delete=models.SET_NULL,
                               related_name="created_videos")
