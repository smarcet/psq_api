import base64
import hashlib
import hmac
import logging
import sys
from datetime import datetime
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from macaddress import format_mac
from netaddr import mac_unix
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from ..decorators import role_required
from ..exceptions import CustomValidationError
from ..models import ModelValidationException, Device, Exercise, DeviceBroadCast
from ..models import User, Exam
from ..serializers import ExamReadSerializer, ExamStudentWriteSerializer, ExamEvaluatorWriteSerializer, ExamReadSerializerList


class mac_unix_expanded_upper(mac_unix):
    """A UNIX-style MAC address dialect class with leading zeroes."""
    word_fmt = '%.2X'


class ExamListCreateAPIView(ListCreateAPIView):

    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('exercise__title', 'taker__first_name', 'taker__last_name', 'taker__email',)
    ordering_fields = ('id', 'created', 'eval_date' )

    def get_queryset(self):
        current_user = self.request.user
        if current_user.is_student:
            return Exam.objects.filter(Q(exercise__type=Exercise.REGULAR) & Q(taker=current_user)).order_by('created')
        if current_user.is_teacher:
            return Exam.objects.filter(Q(exercise__type=Exercise.REGULAR) & Q(device__in=current_user.my_devices_ids)).order_by('created')

        return Exam.objects.filter(Q(exercise__type=Exercise.REGULAR))

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ExamStudentWriteSerializer
        return ExamReadSerializerList

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
            if current_user.is_student and exam.taker.id != current_user.id:
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
            if "device_id" not in request.GET:
                return Response(data={ "error" : _("missing device_id") },
                                status=status.HTTP_412_PRECONDITION_FAILED)

            if "exercise_id" not in request.GET:
                return Response(data={ "error" : _("missing exercise_id") },
                                status=status.HTTP_412_PRECONDITION_FAILED)

            if "user_id" not in request.GET:
                return Response(data={ "error" : _("missing user_id") },
                                status=status.HTTP_412_PRECONDITION_FAILED)

            if "exercise_max_duration" not in request.GET:
                return Response(data={ "error" : _("missing exercise_max_duration") },
                                status=status.HTTP_412_PRECONDITION_FAILED)

            if "signature" not in request.GET:
                return Response(data={ "error" : _("missing signature") },
                                status=status.HTTP_412_PRECONDITION_FAILED)

            if "expires" not in request.GET:
                return Response(data={ "error" : _("missing expires") },
                                status=status.HTTP_412_PRECONDITION_FAILED)

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

            current_broadcasting =  DeviceBroadCast.objects.filter(
                Q(exercise_id=exercise_id) &
                Q(device_id=device_id) &
                Q(user_id=user_id) &
                Q(ends_at=None)).order_by('-start_at').first()

            if current_broadcasting is None:
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
                },
                'broadcasting': {
                    'id': current_broadcasting.id,
                    'start_at': current_broadcasting.start_at.timestamp()
                }
            }, status=status.HTTP_200_OK)

        except ModelValidationException as error1:
            raise CustomValidationError(str(error1))
        except:
            print("Unexpected error:", sys.exc_info()[0])
            logger.error("Unexpected error {error}".format(error=sys.exc_info()[0]))
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)