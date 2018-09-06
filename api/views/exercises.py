from django.db.models import Q
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView, GenericAPIView
from ..exceptions import CustomValidationError
from ..models import ModelValidationException
from ..serializers import WriteableExerciseSerializer, ReadExerciseSerializer, StudentReadExerciseSerializer
from ..models import User, Exercise, Device, Exam
from ..decorators import role_required
from django.utils.translation import ugettext_lazy as _
from django.http import Http404
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Max, Count, Min
import itertools
from datetime import datetime
import pytz


class TutorialListAPIView(ListAPIView):
    filter_fields = ('id', 'title', 'type')
    ordering_fields = ('id', 'title', 'type')
    filter_backends = (SearchFilter,)
    serializer_class = ReadExerciseSerializer

    def get_queryset(self):
        current_user = self.request.user
        return Exercise.objects \
            .filter(Q(allowed_devices__admins__in=[current_user])
                    | Q(allowed_devices__owner__in=[current_user])
                    | Q(author=current_user)).distinct().filter(type=Exercise.TUTORIAL).order_by('id')


class ExerciseListCreateAPIView(ListCreateAPIView):
    search_fields = ('title',)
    ordering_fields = ('id', 'title', 'type', 'created')
    filter_backends = (SearchFilter, OrderingFilter)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return WriteableExerciseSerializer
        if self.request.user.is_student:
            return StudentReadExerciseSerializer
        return ReadExerciseSerializer

    def get_queryset(self):
        if self.request.method == 'GET':
            current_user = self.request.user
            if current_user.is_student:
                # get only the available exercises for current student
                return Exercise.objects \
                    .filter(Q(type=Exercise.REGULAR) & Q(allowed_devices__users__in=[current_user])).order_by(
                    'created').distinct()

            if current_user.is_teacher:
                return Exercise.objects \
                    .filter(Q(allowed_devices__admins__in=[current_user])
                            | Q(allowed_devices__owner__in=[current_user])
                            | Q(shared_with_devices__admins__in=[current_user])
                            | Q(shared_with_devices__owner__in=[current_user])
                            | Q(author=current_user)).order_by('created').distinct()
            # for super admin return all
            return Exercise.objects.all().order_by('id')
        return Exercise.objects.all().order_by('id')

    @role_required(required_role=User.TEACHER)
    def post(self, request, *args, **kwargs):
        try:
            return self.create(request, *args, **kwargs)
        except ModelValidationException as error1:
            raise CustomValidationError(str(error1))


class ExerciseRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Exercise.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return WriteableExerciseSerializer
        return ReadExerciseSerializer

    def patch(self, request, *args, **kwargs):
        pass

    @role_required(required_role=User.STUDENT)
    def get(self, request, *args, **kwargs):
        try:
            user = request.user
            exercise = self.get_object()
            if not exercise.can_view(user):
                raise ModelValidationException(_('user is not allowed to view this exercise'))

            return self.retrieve(request, *args, **kwargs)
        except ModelValidationException as error1:
            raise CustomValidationError(str(error1), 'error')

    @role_required(required_role=User.TEACHER)
    def delete(self, request, *args, **kwargs):
        current_user = request.user
        exercise = self.get_object()
        if exercise.is_shared_with_user(current_user):
            exercise.un_shared_with_user(current_user)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return self.destroy(request, *args, **kwargs)

    @role_required(required_role=User.TEACHER)
    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class ExerciseStatisticsAPIView(GenericAPIView):
    queryset = Exercise.objects.all()
    serializer_class = ReadExerciseSerializer

    @role_required(required_role=User.STUDENT)
    def get(self, request, pk, start_date, end_date):
        exercise = self.get_object()
        try:

            current_user = request.user
            start_date = datetime.fromtimestamp(start_date) \
                .replace(hour=00, minute=00, second=0, microsecond=0, tzinfo=pytz.UTC)
            end_date = datetime.fromtimestamp(end_date) \
                .replace(hour=23, minute=59, second=59, microsecond=999999, tzinfo=pytz.UTC)

            exams = Exam.objects.filter(Q(created__gte=start_date) & Q(created__lte=end_date) & Q(taker=current_user) &
                                        Q(exercise=exercise))

            if exams.count() == 0:
                return Response([], status=404)

            grouped = itertools.groupby(exams, lambda record: record.created.strftime("%Y-%m-%d"))
            grouped2 = itertools.groupby(exams, lambda record: record.created.strftime("%Y-%m-%d"))
            best_time_per_day = []

            max_instances_per_day = 0
            for tuple in [(day, min(list(exams_this_day), key=lambda x: x.duration)) for day, exams_this_day
                          in grouped]:
                best_time_per_day.append((tuple[0], tuple[1].duration))

            instances_per_day = [(day, len(list(exams_this_day))) for day, exams_this_day in grouped2]
            for tuple in instances_per_day:
                if max_instances_per_day < tuple[1]:
                    max_instances_per_day = tuple[1]

            data = {
                'total_instances': exams.count(),
                'max_instances_per_day': max_instances_per_day,
                'best_time': exams.aggregate(Min('duration')),
                'best_time_per_day': best_time_per_day,
                'instances_per_day': instances_per_day,
            }

            return Response(data, status=200)

        except ModelValidationException as error1:
            raise CustomValidationError(str(error1), 'error')


class DeviceExercisesDetailView(ListAPIView):
    serializer_class = ReadExerciseSerializer

    def get_queryset(self):
        device_id = self.kwargs['pk']
        current_user = self.request.user
        if current_user.is_teacher:
            return Exercise.objects.filter(
                Q(allowed_devices__in=[device_id]) |
                Q(shared_with_devices__in=[device_id])
            ).order_by('-created')

        return Exercise.objects.filter(
            (Q(allowed_devices__in=[device_id]) |
            Q(shared_with_devices__in=[device_id]) )
            & Q(type=Exercise.REGULAR)).order_by(
            '-created')


class ShareExerciseAPIView(GenericAPIView):
    queryset = Exercise.objects.all()
    serializer_class = ReadExerciseSerializer

    @role_required(required_role=User.TEACHER)
    def put(self, request, pk, device_id):
        exercise = self.get_object()
        try:

            current_user = request.user
            if exercise.author.id != current_user.id:
                raise ModelValidationException(
                    _("User {user_id} is not allowed to share exercise {exercise_id}").format(user_id=current_user.id,
                                                                                              exercise_id=pk))

            device = Device.objects.get(pk=device_id)
            if device is None:
                raise Http404(_("Device %s does not exists") % device_id)

            if exercise.is_allowed_device(device):
                raise ModelValidationException(
                    _("device {device_id} is already an allowed device").format(device_id=device_id))

            exercise.share_with(device)

            return Response({}, status=status.HTTP_204_NO_CONTENT)

        except ModelValidationException as error1:
            raise CustomValidationError(str(error1), 'error')
