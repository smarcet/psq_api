from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from api.models import ModelValidationException, Device
from ..decorators import role_required
from ..exceptions import CustomValidationError
from ..models import User, Exam
from ..serializers import ExamReadSerializer, ExamStudentWriteSerializer, ExamEvaluatorWriteSerializer
from ..serializers import ExamVideoWriteSerializer, ExamPendingRequestWriteSerializer, ExamPendingRequestVideoWriteSerializer
from django.utils.translation import ugettext_lazy as _
import logging


class ExamUploadAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = ExamVideoWriteSerializer
    parser_classes = (MultiPartParser, FormParser)

    @staticmethod
    def post(request):
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

            exam_video_serializer = ExamPendingRequestVideoWriteSerializer(data=request.data)
            exam_serializer = ExamPendingRequestWriteSerializer(data=request.data)

            if exam_serializer.is_valid() and exam_video_serializer.is_valid():
                logger.info("uploading new exam request - data is valid")
                exam = exam_serializer.save()
                logger.info("uploading new exam request - saving video")
                exam_video = exam_video_serializer.save()
                logger.info("uploading new exam request - saved video")
                exam_video.set_request(exam)
                response_data = exam_serializer.data
                logger.info("uploading new exam request - OK")
                return Response(data=response_data, status=status.HTTP_201_CREATED)

            return Response(exam_video_serializer.errors + exam_serializer.errors,
                            status=status.HTTP_412_PRECONDITION_FAILED)

        except ModelValidationException as error1:
            raise CustomValidationError(str(error1))


class ExamListCreateAPIView(ListCreateAPIView):
    filter_fields = ('id', 'approved')
    ordering_fields = ('id', 'approved')
    queryset = Exam.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ExamStudentWriteSerializer
        return ExamReadSerializer

    @role_required(required_role=User.STUDENT)
    def post(self, request, *args, **kwargs):
        try:
            return self.create(request, *args, **kwargs)
        except ModelValidationException as error1:
            raise CustomValidationError(str(error1))


class ExamRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Exam.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return ExamEvaluatorWriteSerializer
        return ExamReadSerializer

    def patch(self, request, *args, **kwargs):
        pass

    @role_required(required_role=User.STUDENT)
    def get(self, request, *args, **kwargs):
        try:
            exam = self.get_object()
            current_user = request.user
            if current_user.role == User.STUDENT and exam.taker.id != current_user.id:
                # exam should be own by user
                raise ModelValidationException(
                    _("exam {exam_id} does not belongs to user {user_id}").format(user_id=current_user.id,
                                                                                  exam_id=exam.id))
            return self.retrieve(request, *args, **kwargs)

        except ModelValidationException as error1:
            raise CustomValidationError(str(error1))

    @role_required(required_role=User.TEACHER)
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    @role_required(required_role=User.TEACHER)
    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
