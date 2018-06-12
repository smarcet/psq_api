from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, GenericAPIView
from rest_framework import status
from rest_framework.response import Response
from ..models import ModelValidationException
from ..models import Tutorial, User
from ..decorators import role_required
from ..exceptions import ValidationError
from ..serializers import TutorialWriteSerializer, TutorialReadSerializer


class TutorialListCreateAPIView(ListCreateAPIView):
    queryset = Tutorial.objects.all()
    filter_fields = ('id', 'title')
    ordering_fields = ('id', 'title')

    @role_required(required_role=User.TEACHER)
    def post(self, request, *args, **kwargs):
        try:
            return self.create(request, *args, **kwargs)
        except ModelValidationException as error1:
            raise ValidationError(str(error1))

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TutorialWriteSerializer
        return TutorialReadSerializer


class TutorialRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Tutorial.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return TutorialWriteSerializer
        return TutorialReadSerializer

    def patch(self, request, *args, **kwargs):
        pass

    @role_required(required_role=User.TEACHER)
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    @role_required(required_role=User.TEACHER)
    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)