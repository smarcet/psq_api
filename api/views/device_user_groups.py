from django.db.models import Q
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, GenericAPIView
from ..models import User, DeviceUsersGroup
from ..decorators import role_required
from ..serializers import ReadDeviceUsersGroupSerializer, WriteableDeviceUsersGroupSerializer
import logging


class DeviceUsersGroupsListCreateView(ListCreateAPIView):

    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    ordering_fields = ('id', 'name')

    def get_queryset(self):
        current_user = self.request.user
        queryset = DeviceUsersGroup.objects.filter(Q(device__in=current_user.my_devices)).order_by('id')
        return queryset

    @role_required(required_role=User.TEACHER)
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    @role_required(required_role=User.TEACHER)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return WriteableDeviceUsersGroupSerializer
        return ReadDeviceUsersGroupSerializer
