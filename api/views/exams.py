from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from ..exceptions import ValidationError
from api.models import ModelValidationException
from ..serializers import ExamReadSerializer, ExamStudentWriteSerializer, ExamEvaluatorWriteSerializer
from ..models import User, Exam
from ..decorators import role_required


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
            raise ValidationError(str(error1))


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