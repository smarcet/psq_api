from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from ..exceptions import ValidationError
from api.models import ModelValidationException
from ..serializers import WriteableExerciseSerializer, ReadExerciseSerializer
from ..models import User, Exercise
from ..decorators import role_required


class ExerciseListCreateAPIView(ListCreateAPIView):
    filter_fields = ('id', 'title', 'type')
    ordering_fields = ('id', 'title', 'type')
    queryset = Exercise.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return WriteableExerciseSerializer
        return ReadExerciseSerializer

    @role_required(required_role=User.TEACHER)
    def post(self, request, *args, **kwargs):
        try:
            return self.create(request, *args, **kwargs)
        except ModelValidationException as error1:
            raise ValidationError(str(error1))


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
            raise ValidationError(str(error1), 'error')

    @role_required(required_role=User.TEACHER)
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    @role_required(required_role=User.TEACHER)
    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
