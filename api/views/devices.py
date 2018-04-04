from rest_framework.response import Response

from ..serializers import DeviceSerializer
from ..models import Device
from rest_framework.generics import ListAPIView


class DeviceList(ListAPIView):

    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    filter_fields = ('serial', 'friendly_name', 'is_active')

