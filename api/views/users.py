from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView, RetrieveUpdateAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from api.exceptions import ValidationError
from api.models import ModelValidationException
from ..serializers.devices import ReadDeviceSerializer, WriteableDeviceSerializer
from ..decorators import role_required
from ..serializers.users import ReadUserSerializer, WritableAdminUserSerializer, \
    WritableRawUserSerializer, UserPicSerializer, WritableUserSerializer, WritableOwnUserSerializer, \
    ChangePasswordSerializer
from ..models import User, Device
import hashlib
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q


class UserResendVerificationView(APIView):

    @role_required(required_role=User.SUPERVISOR)
    def post(self, request, pk):
        user = User.objects.get(pk=pk)
        if user is None:
            return Response(status=404, data=_("User not found"))
        user.resend_verification()
        return Response(status=204)


class UserActivationView(APIView):
    parser_classes = (JSONParser,)

    # this view is open to anyone with a valid token, if u have the token
    # its bc u mean to have it !
    permission_classes = (AllowAny,)

    def post(self, request, registration_token):
        json = request.data
        password = json.get("password", None)

        if registration_token is None:
            return Response(status=400, data=_("Missing param 'registration_token'"))

        if password is None:
            return Response(status=400, data=_("Missing param 'password'"))

        user = User.objects.filter(
            registration_hash=hashlib.md5(registration_token.encode('utf-8')).hexdigest()).first()

        if user is None:
            return Response(status=404, data=_("User not found"))

        if user.is_verified:
            return Response(status=404, data=_("User not found"))

        user.verify(password)

        return Response(status=201)


class UserList(APIView):

    def get(self, request, format=None):
        users = User.objects.all()
        serializer = ReadUserSerializer(users, many=True)
        return Response(serializer.data)


class UserPicUpdateView(APIView):
    serializer_class = UserPicSerializer
    parser_classes = (MultiPartParser, FormParser)

    @staticmethod
    def post(request):
        pic_serializer = UserPicSerializer(instance=request.user, data=request.data, partial=True)
        if pic_serializer.is_valid():
            pic_serializer.save()
            response_data = pic_serializer.data
            response_data['pic_url'] = request.build_absolute_uri(response_data['pic'])
            return Response(data=response_data, status=status.HTTP_201_CREATED)

        return Response(pic_serializer.errors, status=status.HTTP_412_PRECONDITION_FAILED)


class AdminUserMyDeviceListView(ListAPIView):
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('friendly_name', 'ip', 'serial')
    ordering_fields = ('id', 'friendly_name')

    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return WriteableDeviceSerializer
        return ReadDeviceSerializer

    @role_required(required_role=User.TEACHER)
    def get(self, request, *args, **kwargs):
        admin_user = request.user
        queryset = self.filter_queryset(Device.objects.filter(Q(owner=admin_user) | Q(admins__in=[admin_user])))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class AdminUserDetailOwnedDevicesView(ListAPIView):

    def get_serializer_class(self):
        return ReadDeviceSerializer

    @role_required(required_role=User.SUPERVISOR)
    def get(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        admin_user = User.objects.get(pk=pk)
        queryset = self.filter_queryset(Device.objects.filter(owner=admin_user))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class AdminUserDetailView(RetrieveUpdateDestroyAPIView):
    queryset = User.objects.filter(role=User.TEACHER)

    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return WritableAdminUserSerializer
        return ReadUserSerializer

    def patch(self, request, *args, **kwargs):
        pass

    @role_required(required_role=User.SUPERVISOR)
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    @role_required(required_role=User.TEACHER)
    def put(self, request, *args, **kwargs):
        try:
            current_user = request.user
            admin_user = self.get_object()

            return self.partial_update(request, *args, **kwargs)

        except ModelValidationException as error1:
            raise ValidationError(str(error1), 'error')


class CreateAdminUserView(ListCreateAPIView):
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('email', 'first_name', 'last_name')
    ordering_fields = ('id', 'email', 'first_name', 'last_name')
    queryset = User.objects.filter(role=User.TEACHER)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return WritableAdminUserSerializer
        return ReadUserSerializer

    @role_required(required_role=User.SUPERVISOR)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @role_required(required_role=User.SUPERVISOR)
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class CreateRawUserView(ListCreateAPIView):
    queryset = User.objects.filter(role=User.STUDENT)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return WritableRawUserSerializer
        return ReadUserSerializer

    @role_required(required_role=User.TEACHER)
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class MyUserDetailView(RetrieveUpdateAPIView):

    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return WritableOwnUserSerializer
        return ReadUserSerializer

    def get_object(self):
        return self.request.user

    def get(self, request, **kwargs):
        user = self.get_object()
        serializer = ReadUserSerializer(user, context={"request": request})
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        try:
            data = request.data
            if 'password' in data and data['password'] is not None:
                instance = self.get_object()
                serializer = ChangePasswordSerializer(data=request.data)
                if serializer.is_valid(True):
                    # set_password also hashes the password that the user will get
                    instance.set_password(serializer.data.get("password"))
                    instance.save()

            return self.partial_update(request, *args, **kwargs)
        except ModelValidationException as error1:
            raise ValidationError(str(error1), 'error')
