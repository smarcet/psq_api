import base64
import hashlib
import hmac
import logging
import sys
from datetime import datetime

from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from macaddress import format_mac
from netaddr import mac_unix
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from ..decorators import role_required
from ..exceptions import CustomValidationError
from ..models import ModelValidationException, Device, Exercise, DeviceBroadCast
from ..models import User, Exam
from ..serializers import ExamReadSerializer, ExamStudentWriteSerializer, ExamEvaluatorWriteSerializer
from ..serializers import ExamVideoWriteSerializer, ExamPendingRequestWriteSerializer, \
    ExamPendingRequestVideoWriteSerializer


class mac_unix_expanded_upper(mac_unix):
    """A UNIX-style MAC address dialect class with leading zeroes."""
    word_fmt = '%.2X'


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

            return Response(exam_video_serializer.errors | exam_serializer.errors,
                            status=status.HTTP_412_PRECONDITION_FAILED)

        except ModelValidationException as error1:
            raise CustomValidationError(str(error1))


class ExamListCreateAPIView(ListCreateAPIView):
    filter_fields = ('id', 'approved')
    ordering_fields = ('id', 'approved')
    queryset = Exam.objects.filter(Q(exercise__type=Exercise.REGULAR))

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


class ValidateExamStreamingSignedUrlView(APIView):
    permission_classes = (AllowAny,)

    @staticmethod
    def get(request, *args, **kwargs):
        logger = logging.getLogger('api')
        try:
            device_id = int(request.GET.get("device_id"))
            exercise_id = int(request.GET.get("exercise_id"))
            user_id = int(request.GET.get("user_id"))
            exercise_max_duration = int(request.GET.get("exercise_max_duration"))
            signature = str(request.GET.get("signature"))
            expires = int(request.GET.get("expires"))
            now_epoch = int(datetime.utcnow().timestamp())

            if expires < now_epoch:
                raise ModelValidationException(_("link is expired"))

            current_device = Device.objects.get(pk=device_id)
            if current_device is None:
                return Response(data=_("device not found"),
                                status=status.HTTP_404_NOT_FOUND)

            current_exercise = Exercise.objects.get(pk=exercise_id)
            if current_exercise is None:
                return Response(data=_("exercise not found"),
                                status=status.HTTP_404_NOT_FOUND)
            current_user = User.objects.get(pk=user_id)

            if current_user is None:
                return Response(data=_("user not found"),
                                status=status.HTTP_404_NOT_FOUND)

            secret = format_mac(current_device.mac_address, mac_unix_expanded_upper)
            str_to_sign = "GET\n%s\n%s\n%s\n%s\n%s" % (device_id, exercise_id, exercise_max_duration, user_id, expires)
            h = hmac.new(bytearray(secret, 'utf-8'), str_to_sign.encode('utf-8'), hashlib.sha1)
            digest = h.digest()
            calculate_signature = base64.b64encode(digest).decode("utf-8")
            if signature != calculate_signature:
                raise ModelValidationException(_("link signature is invalid"))

            is_broadcasting =  DeviceBroadCast.objects.filter(
                Q(exercise_id=exercise_id) &
                Q(device_id=device_id) &
                Q(user_id=user_id) &
                Q(ends_at=None)).count() > 0

            if not is_broadcasting:
                raise ModelValidationException(_("device is not currently broadcasting"))

            return Response({
                'device': {
                    'id' : current_device.id,
                    'friendly_name' : current_device.friendly_name,
                    'serial': current_device.serial,
                    'slug': current_device.slug,
                },
                'exercise': {
                    'id': current_exercise.id,
                    'title': current_exercise.title,
                    'max_duration': current_exercise.max_duration,
                },
                'user': {
                    'id': current_user.id,
                    'first_name': current_user.first_name,
                    'last_name': current_user.last_name,
                }
            }, status=status.HTTP_200_OK)

        except ModelValidationException as error1:
            raise CustomValidationError(str(error1))
        except:
            print("Unexpected error:", sys.exc_info()[0])
            logger.error("Unexpected error {error}".format(error=sys.exc_info()[0]))
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)