from drf_chunked_upload.views import ChunkedUploadView
from rest_framework.permissions import AllowAny
from ..serializers import FileUploadSerializer
from ..models import FileUpload
import logging
from ..models import ModelValidationException, Device, ExamPendingRequestVideo
from ..serializers import ExamPendingRequestWriteSerializer
from ..exceptions import CustomValidationError
from django.db import transaction
from django.core.files import File


class FileUploadView(ChunkedUploadView):
    # open local endpoint

    permission_classes = (AllowAny,)

    model = FileUpload

    serializer_class = FileUploadSerializer

    @transaction.atomic
    def on_completion(self, chunked_upload, request):
        logger = logging.getLogger('api')
        try:
            logger.info("uploading new exam request ...")
            if 'device_mac_address' not in request.data:
                raise ModelValidationException

            if 'device' not in request.data:
                raise ModelValidationException

            device = Device.objects.filter(mac_address=request.data['device_mac_address']).first()

            if device is None:
                raise ModelValidationException

            if device.id != int(request.data['device']):
                raise ModelValidationException
            file_path = chunked_upload.file.path

            with open(file_path, "rb") as file_input:
                exam_serializer = ExamPendingRequestWriteSerializer(data=request.data)

                if exam_serializer.is_valid():
                    logger.info("uploading new exam request - data is valid")
                    exam = exam_serializer.save()
                    logger.info("uploading new exam request - saving video")
                    exam_video = ExamPendingRequestVideo()
                    exam_video.file = File(file_input)
                    logger.info("uploading new exam request - saved video")
                    exam_video.set_request(exam)
                    exam_video.save()
                    logger.info("uploading new exam request - OK")

        except ModelValidationException as error1:
            raise CustomValidationError(str(error1))
        except Exception as exc:
            logger.error("ProcessExamCreationJobsCronJob - Unexpected error")
            raise exc
