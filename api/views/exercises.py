from django.db.models import Q
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView
from ..exceptions import CustomValidationError
from ..models import ModelValidationException
from ..serializers import WriteableExerciseSerializer, ReadExerciseSerializer
from ..models import User, Exercise
from ..decorators import role_required
from django.utils.translation import ugettext_lazy as _


class ExerciseListCreateAPIView(ListCreateAPIView):
    filter_fields = ('id', 'title', 'type')
    ordering_fields = ('id', 'title', 'type')
    filter_backends = (SearchFilter,)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return WriteableExerciseSerializer
        return ReadExerciseSerializer

    def get_queryset(self):
        if self.request.method == 'GET':
            current_user = self.request.user
            if current_user.role == User.STUDENT:
                # get only the available exercises for current student
                return Exercise.objects\
                    .filter(Q(type=Exercise.REGULAR) & Q(allowed_devices__users__in=[current_user])).distinct().order_by('id')
            if current_user.role == User.TEACHER:
                return Exercise.objects \
                    .filter(Q(allowed_devices__admins__in=[current_user])
                            | Q(allowed_devices__owner__in=[current_user])
                            | Q(author=current_user)).distinct().order_by('id')
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
                raise ModelValidationException(_('user is not allowed to get this exercise'))

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
        device_id = self.kwargs['pk'];
        return Exercise.objects.filter(allowed_devices__in=[device_id])
