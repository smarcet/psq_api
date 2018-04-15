from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, GenericAPIView
from ..exceptions import ValidationError
from ..serializers import WriteableDeviceSerializer, ReadDeviceSerializer, NullableDeviceSerializer
from ..models import Device
from ..models import User
from ..models import ModelValidationException
from ..decorators import token_required, allowed_device


class DeviceList(ListCreateAPIView):

    queryset = Device.objects.all()
    filter_fields = ('serial', 'friendly_name', 'is_active')

    @token_required(required_role=User.SUPERVISOR)
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

    @token_required(required_role=User.SUPERVISOR)
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    @token_required(required_role=User.TEACHER)
    @allowed_device()
    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class DeviceUsersList(GenericAPIView):
    queryset = Device.objects.all()
    serializer_class = NullableDeviceSerializer

    @token_required(required_role=User.TEACHER)
    @allowed_device()
    def put(self, request, pk, user_id):
        device = self.get_object()
        try:
            user = User.objects.get(pk=user_id)

            device.add_user(user)

        except ModelValidationException as error1:
            raise ValidationError(str(error1))

        except User.DoesNotExist:
            raise Http404(_("User %s does not exists") % user_id)

    @token_required(required_role=User.TEACHER)
    @allowed_device()
    def delete(self, request, pk, user_id):
        device = self.get_object()
        try:
            user = User.objects.get(pk=user_id)

            device.remove_user(user)

        except ModelValidationException as error1:
            raise ValidationError(str(error1))

        except User.DoesNotExist:
            raise Http404(_("User %s does not exists") % user_id)


class DeviceAdminsList(GenericAPIView):
    queryset = Device.objects.all()
    serializer_class = NullableDeviceSerializer

    @token_required(required_role=User.TEACHER)
    @allowed_device()
    def put(self, request, pk, user_id):
        device = self.get_object()
        try:
            user = User.objects.get(pk=user_id)

            device.add_admin(user)

        except ModelValidationException as error1:
            raise ValidationError(str(error1))

        except User.DoesNotExist:
            raise Http404(_("User %s does not exists") % user_id)

    @token_required(required_role=User.TEACHER)
    @allowed_device()
    def delete(self, request, pk, user_id):

        device = self.get_object()
        try:
            user = User.objects.get(pk=user_id)

            device.remove_admin(user)

        except ModelValidationException as error1:
            raise ValidationError(str(error1))

        except User.DoesNotExist:
            raise Http404(_("User %s does not exists") % user_id)


