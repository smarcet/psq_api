from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from .video import Video


class TutorialVideo(Video):
    # relations

    exercise = models.ForeignKey("Exercise",
                                 null=True, on_delete=models.SET_NULL,
                                 related_name="videos")
