from django.conf import settings
from django.db import models
from model_utils.models import TimeStampedModel


class News(TimeStampedModel):
    title = models.CharField(max_length=255, blank=False, unique=True, null=True)

    body = models.TextField()

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   null=True, on_delete=models.SET_NULL,
                                   related_name="created_news")
