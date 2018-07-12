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
from ..serializers import ExamVideoWriteSerializer


class ExamUploadAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = ExamVideoWriteSerializer
    parser_classes = (MultiPartParser, FormParser)

    @staticmethod
    def post(request):

        try:
            if not 'device_mac_address' in request.data:
                raise ModelValidationException

            if not 'device' in request.data:
                raise ModelValidationException

            device = Device.objects.filter(mac_address=request.data['device_mac_address']).first()

            if device is None:
                raise ModelValidationException

            if device.id != int(request.data['device']):
                raise ModelValidationException

            exam_video_serializer = ExamVideoWriteSerializer(data=request.data)
            exam_serializer = ExamStudentWriteSerializer(data=request.data)

            if exam_serializer.is_valid() and exam_video_serializer.is_valid():
                exam = exam_serializer.save()
                exam_video = exam_video_serializer.save()
                exam_video.set_exam(exam)
                response_data = exam_serializer.data
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

    @role_required(required_role=User.TEACHER)
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    @role_required(required_role=User.TEACHER)
    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
