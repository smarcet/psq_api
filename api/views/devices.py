from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, GenericAPIView
from rest_framework import status
from rest_framework.response import Response
from ..models import Device
from ..models import User
from ..models import ModelValidationException
from ..decorators import role_required
from ..exceptions import ValidationError
from ..serializers import WriteableDeviceSerializer, ReadDeviceSerializer, NullableDeviceSerializer, \
    OpenRegistrationSerializer


class DeviceListCreate(ListCreateAPIView):
    queryset = Device.objects.all()
    filter_fields = ('serial', 'friendly_name', 'is_active')

    @role_required(required_role=User.SUPERVISOR)
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return WriteableDeviceSerializer
        return ReadDeviceSerializer


class DeviceDetail(RetrieveUpdateDestroyAPIView):
    queryset = Device.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return WriteableDeviceSerializer
        return ReadDeviceSerializer

    def patch(self, request, *args, **kwargs):
        pass

    @role_required(required_role=User.SUPERVISOR)
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    @role_required(required_role=User.TEACHER)
    def put(self, request, *args, **kwargs):
        try:
            current_user = request.user
            device = self.get_object()
            if not device.is_allowed_admin(current_user):
                raise ModelValidationException(
                    _("User {user_id} is mot allowed to manage device {device_id}}").format(user_id=current_user.id,
                                                                                            device_id=device.id))
            return self.partial_update(request, *args, **kwargs)

        except ModelValidationException as error1:
            raise ValidationError(str(error1))


class DeviceUsersList(GenericAPIView):
    queryset = Device.objects.all()
    serializer_class = NullableDeviceSerializer

    @role_required(required_role=User.TEACHER)
    def put(self, request, pk, user_id):
        device = self.get_object()
        try:
            current_user = request.user
            if not device.is_allowed_admin(current_user):
                raise ModelValidationException(
                    _("User {user_id} is mot allowed to manage device {device_id}}").format(user_id=current_user.id,
                                                                                            device_id=pk))

            user = User.objects.get(pk=user_id)

            device.add_user(user)

        except ModelValidationException as error1:
            raise ValidationError(str(error1))

        except User.DoesNotExist:
            raise Http404(_("User %s does not exists") % user_id)

    @role_required(required_role=User.TEACHER)
    def delete(self, request, pk, user_id):
        device = self.get_object()
        try:
            current_user = request.user
            if not device.is_allowed_admin(current_user):
                raise ModelValidationException(
                    _("User {user_id} is mot allowed to manage device {device_id}}").format(user_id=current_user.id,
                                                                                            device_id=pk))

            user = User.objects.get(pk=user_id)

            device.remove_user(user)

        except ModelValidationException as error1:
            raise ValidationError(str(error1))

        except User.DoesNotExist:
            raise Http404(_("User %s does not exists") % user_id)


class DeviceOpenRegistrationView(GenericAPIView):

    queryset = Device.objects.all()
    serializer_class = OpenRegistrationSerializer

    def post(self, request):
        serializer = OpenRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            instance = serializer.save()
            data = {'id' : instance.id, 'mac_address' : str(instance.mac_address), 'last_know_ip' : instance.last_know_ip, 'stream_key': instance.stream_key, 'serial': str(instance.serial)  }
            return Response(data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_412_PRECONDITION_FAILED)


class DeviceAdminsList(GenericAPIView):
    queryset = Device.objects.all()
    serializer_class = NullableDeviceSerializer

    @role_required(required_role=User.TEACHER)
    def put(self, request, pk, user_id):
        device = self.get_object()
        try:

            current_user = request.user
            if not device.is_allowed_admin(current_user):
                raise ModelValidationException(
                    _("User {user_id} is mot allowed to manage device {device_id}}").format(user_id=current_user.id,
                                                                                            device_id=pk))

            user = User.objects.get(pk=user_id)

            device.add_admin(user)

        except ModelValidationException as error1:
            raise ValidationError(str(error1))

        except User.DoesNotExist:
            raise Http404(_("User %s does not exists") % user_id)

    @role_required(required_role=User.TEACHER)
    def delete(self, request, pk, user_id):

        device = self.get_object()
        try:
            current_user = request.user
            if not device.is_allowed_admin(current_user):
                raise ModelValidationException(
                    _("User {user_id} is mot allowed to manage device {device_id}}").format(user_id=current_user.id,
                                                                                            device_id=pk))

            user = User.objects.get(pk=user_id)

            device.remove_admin(user)

        except ModelValidationException as error1:
            raise ValidationError(str(error1))

        except User.DoesNotExist:
            raise Http404(_("User %s does not exists") % user_id)
