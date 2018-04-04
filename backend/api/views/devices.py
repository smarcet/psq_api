from rest_framework.response import Response

from ..serializers import DeviceSerializer
from ..models import Device
from rest_framework.views import APIView
from rest_framework.settings import api_settings
from ..mixins import MyPaginationMixin


class DeviceList(APIView, MyPaginationMixin):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS

    def get(self, request):

        page = self.paginate_queryset(self.queryset)
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.serializer_class(self.queryset, many=True)
        return Response(serializer.data)