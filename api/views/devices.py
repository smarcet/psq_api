from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, GenericAPIView
from rest_framework import status
from rest_framework.response import Response
from ..models import Device
from ..models import User
from ..models import ModelValidationException
from ..decorators import role_required
from ..exceptions import ValidationError
from ..serializers import WriteableDeviceSerializer, ReadDeviceSerializer, NullableDeviceSerializer, \
    OpenRegistrationSerializer, VerifyDeviceSerializer


class DeviceListCreateView(ListCreateAPIView):
    queryset = Device.objects.all()
    filter_backends = (SearchFilter,)
    search_fields = ('friendly_name', 'mac_address')
    ordering_fields = ('id', 'friendly_name')

    @role_required(required_role=User.SUPERVISOR)
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    @role_required(required_role=User.SUPERVISOR)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return WriteableDeviceSerializer
        return ReadDeviceSerializer


class DeviceDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Device.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return WriteableDeviceSerializer
        return ReadDeviceSerializer

    def patch(self, request, *args, **kwargs):
        pass

    @role_required(required_role=User.STUDENT)
    def get(self, request, *args, **kwargs):
        try:
            current_user = request.user
            device = self.get_object()

            if not device.is_allowed_user(current_user):
                raise ModelValidationException(
                    _("User {user_id} is mot allowed to manage device {device_id}").format(user_id=current_user.id,
                                                                                           device_id=device.id))

            return self.retrieve(request, *args, **kwargs)
        except ModelValidationException as error1:
            raise ValidationError(str(error1), 'error')

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
                    _("User {user_id} is mot allowed to manage device {device_id}").format(user_id=current_user.id,
                                                                                           device_id=device.id))
            return self.partial_update(request, *args, **kwargs)

        except ModelValidationException as error1:
            raise ValidationError(str(error1), 'error')


class DeviceUsersListView(GenericAPIView):
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

            return Response(status=status.HTTP_204_NO_CONTENT)

        except ModelValidationException as error1:
            raise ValidationError(str(error1), 'error')

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

            return Response(status=status.HTTP_204_NO_CONTENT)

        except ModelValidationException as error1:
            raise ValidationError(str(error1), 'error')

        except User.DoesNotExist:
            raise Http404(_("User %s does not exists") % user_id)


class AdminUserOwnedDevicesManageView(GenericAPIView):

    @role_required(required_role=User.SUPERVISOR)
    def delete(self, request, pk, device_id):
        admin_user = User.objects.get(pk=pk)
        device = Device.objects.get(pk=device_id)
        try:
            if not device.is_allowed_admin(admin_user):
                raise ModelValidationException(
                    _("User {user_id} is mot allowed to manage device {device_id}}").format(user_id=admin_user.id,
                                                                                            device_id=device_id))

            device.unlink_from_owner()
            return Response({}, status=status.HTTP_204_NO_CONTENT)

        except ModelValidationException as error1:
            raise ValidationError(str(error1), 'error')

    @role_required(required_role=User.SUPERVISOR)
    def put(self, request, pk, device_id):
        admin_user = User.objects.get(pk=pk)
        device = Device.objects.get(pk=device_id)
        try:
            if device.is_owned_by(admin_user):
                raise ModelValidationException(
                    _("User {user_id} already own device {device_id}").format(user_id=admin_user.id,
                                                                              device_id=device_id))

            device.link_to(admin_user)
            return Response({}, status=status.HTTP_204_NO_CONTENT)

        except ModelValidationException as error1:
            raise ValidationError(str(error1), 'error')


class DeviceVerifyView(GenericAPIView):
    queryset = Device.objects.all()
    serializer_class = VerifyDeviceSerializer

    @role_required(required_role=User.SUPERVISOR)
    def put(self, request, pk):
        device = self.get_object()

        serializer = VerifyDeviceSerializer(device, data=request.data, partial=True)

        if serializer.is_valid():
            device.do_verify()
            instance = serializer.save()
            data = {'id': instance.id, 'mac_address': str(instance.mac_address), 'last_know_ip': instance.last_know_ip,
                    'stream_key': instance.stream_key, 'serial': str(instance.serial)}
            return Response(data, status=status.HTTP_204_NO_CONTENT)

        return Response(serializer.errors, status=status.HTTP_412_PRECONDITION_FAILED)


class DeviceOpenRegistrationView(GenericAPIView):
    queryset = Device.objects.all()
    serializer_class = OpenRegistrationSerializer

    def post(self, request):
        serializer = OpenRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            instance = serializer.save()
            data = {'id': instance.id, 'mac_address': str(instance.mac_address), 'last_know_ip': instance.last_know_ip,
                    'stream_key': instance.stream_key, 'serial': str(instance.serial)}
            return Response(data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_412_PRECONDITION_FAILED)


class DeviceAdminsListView(GenericAPIView):
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

            return Response({}, status=status.HTTP_204_NO_CONTENT)

        except ModelValidationException as error1:
            raise ValidationError(str(error1), 'error')

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

            return Response({}, status=status.HTTP_204_NO_CONTENT)

        except ModelValidationException as error1:
            raise ValidationError(str(error1), 'error')

        except User.DoesNotExist:
            raise Http404(_("User %s does not exists") % user_id)
