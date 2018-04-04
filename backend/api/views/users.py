from ..decorators import token_required
from ..serializers.users import UserSerializer
from ..models import User
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response


class UserList(APIView):

    def get(self, request, format=None):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


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
        serializer = UserSerializer(user)
        return Response(serializer.data)