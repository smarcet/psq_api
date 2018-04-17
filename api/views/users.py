from rest_framework.parsers import JSONParser
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.generics import  ListCreateAPIView
from rest_framework.response import Response
from ..decorators import token_required
from ..serializers.users import ReadUserSerializer, WritableAdminUserSerializer, WritableRawUserSerializer
from ..models import User
import hashlib


class UserValidateView(APIView):
    parser_classes = (JSONParser,)

    def post(self, request, registration_token):
        json=request.data
        password=json.get("password", None)
        if registration_token is None:
            return Response(status=400, data="Missing param 'registration_token'")
        if password is None:
            return Response(status=400, data="Missing param 'password'")

        user = User.objects.filter(registration_hash=hashlib.md5(registration_token.encode('utf-8')).hexdigest()).first()

        if user is None:
            return Response(status=404, data="User not found")

        if user.is_verified:
            return Response(status=404, data="User not found")


        user.verify(password);

        return Response(status=201)


class UserList(APIView):

    def get(self, request, format=None):
        users = User.objects.all()
        serializer = ReadUserSerializer(users, many=True)
        return Response(serializer.data)


class CreateAdminUserView(ListCreateAPIView):
    queryset = User.objects.filter(role=User.TEACHER)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return WritableAdminUserSerializer
        return ReadUserSerializer

    #@token_required(required_role=User.SUPERVISOR)
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class CreateRawUserView(ListCreateAPIView):
    queryset = User.objects.filter(role=User.STUDENT)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return WritableRawUserSerializer
        return ReadUserSerializer

    #@token_required(required_role=User.TEACHER)
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class UserDetailMe(APIView):

    @staticmethod
    def get_object(pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    @token_required()
    def get(self, request):
        user = self.get_object(request.user.id)
        serializer = ReadUserSerializer(user)
        return Response(serializer.data)