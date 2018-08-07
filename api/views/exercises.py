from django.db.models import Q
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView
from ..exceptions import CustomValidationError
from ..models import ModelValidationException
from ..serializers import WriteableExerciseSerializer, ReadExerciseSerializer, StudentReadExerciseSerializer
from ..models import User, Exercise
from ..decorators import role_required
from django.utils.translation import ugettext_lazy as _


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
    search_fields = ( 'title', )
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
            if current_user.is_student :
                # get only the available exercises for current student
                return Exercise.objects\
                    .filter(Q(type=Exercise.REGULAR) & Q(allowed_devices__users__in=[current_user])).order_by('created').distinct()
            if current_user.is_teacher :
                return Exercise.objects \
                    .filter(Q(allowed_devices__admins__in=[current_user])
                            | Q(allowed_devices__owner__in=[current_user])
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
        return self.destroy(request, *args, **kwargs)

    @role_required(required_role=User.TEACHER)
    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class DeviceExercisesDetailView(ListAPIView):
    serializer_class = ReadExerciseSerializer

    def get_queryset(self):
        device_id = self.kwargs['pk']
        current_user = self.request.user
        if current_user.is_teacher:
            return Exercise.objects.filter(Q(allowed_devices__in=[device_id])).order_by('-created')
        return Exercise.objects.filter(Q(allowed_devices__in=[device_id]) & Q(type=Exercise.REGULAR)).order_by('-created')
