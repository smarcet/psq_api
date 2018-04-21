from django.db import models
from .video import Video


class TutorialVideo(Video):
    # relations

    exercise = models.ForeignKey("Tutorial",
                                 null=True, on_delete=models.SET_NULL,
                                 related_name="videos")
