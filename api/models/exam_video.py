from django.conf import settings
from django.db import models
from .video import Video


class ExamVideo(Video):
    # relations

    exam = models.ForeignKey("Exam",
                             null=True, on_delete=models.SET_NULL,
                             related_name="videos")

    shares = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)

    def set_exam(self, exam):
        self.exam = exam
        self.save()