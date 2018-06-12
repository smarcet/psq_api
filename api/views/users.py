from rest_framework import status
from rest_framework.parsers import JSONParser
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.generics import  ListCreateAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from ..decorators import role_required
from ..serializers.users import ReadUserSerializer, WritableAdminUserSerializer, WritableRawUserSerializer, UserPicSerializer
from ..models import User
import hashlib
from django.utils.translation import ugettext_lazy as _


class UserValidateView(APIView):
    parser_classes = (JSONParser,)

    def post(self, request, registration_token):
        json=request.data
        password=json.get("password", None)

        if registration_token is None:
            return Response(status=400, data=_("Missing param 'registration_token'"))

        if password is None:
            return Response(status=400, data=_("Missing param 'password'"))

        user = User.objects.filter(registration_hash=hashlib.md5(registration_token.encode('utf-8')).hexdigest()).first()

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


class AdminUserPicView(APIView):
    serializer_class = UserPicSerializer
    parser_classes = (MultiPartParser, FormParser)

    @staticmethod
    def post(request, pk):

        pic_serializer = UserPicSerializer(data=request.data)

        if pic_serializer.is_valid():
            pic_serializer.save()
            return Response(pic_serializer.data, status=status.HTTP_201_CREATED)

        return Response(pic_serializer.errors, status=status.HTTP_412_PRECONDITION_FAILED)


class CreateAdminUserView(ListCreateAPIView):
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


class UserDetailMe(APIView):

    @staticmethod
    def get_object(pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    def get(self, request):
        user = self.get_object(request.user.id)
        serializer = ReadUserSerializer(user)
        return Response(serializer.data)
