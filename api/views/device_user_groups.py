from django.db.models import Q
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, GenericAPIView
from ..models import User, DeviceUsersGroup
from ..decorators import role_required
from ..serializers import ReadDeviceUsersGroupSerializer, WriteableDeviceUsersGroupSerializer


class DeviceUsersGroupsListCreateView(ListCreateAPIView):

    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    ordering_fields = ('id', 'name')

    def get_queryset(self):
        current_user = self.request.user
        return DeviceUsersGroup.objects.filter(Q(device__in=current_user.my_devices)).order_by('id')

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


class DeviceUsersGroupsRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    def get_queryset(self):
        current_user = self.request.user
        return DeviceUsersGroup.objects.filter(Q(device__in=current_user.my_devices)).order_by('id')

    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return WriteableDeviceUsersGroupSerializer
        return ReadDeviceUsersGroupSerializer

    def patch(self, request, *args, **kwargs):
        pass

    @role_required(required_role=User.TEACHER)
    def get(self, request, *args, **kwargs):
            return self.retrieve(request, *args, **kwargs)

    @role_required(required_role=User.TEACHER)
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    @role_required(required_role=User.TEACHER)
    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
