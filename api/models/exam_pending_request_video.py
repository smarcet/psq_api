from django.core.files.storage import FileSystemStorage
from django.db import models

from model_utils.models import TimeStampedModel


class ExamPendingRequestVideo(TimeStampedModel):

    request = models.ForeignKey("ExamPendingRequest",
                                null=True, on_delete=models.SET_NULL,
                                related_name="videos")
    file = models.FileField(
        storage=FileSystemStorage(),
        upload_to='raw_videos')

    def set_request(self, request):
        self.request = request
        self.save()
