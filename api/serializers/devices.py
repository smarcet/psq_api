from rest_framework import serializers
from ..serializers.users import UserSerializer
from ..models import Device


class DeviceSerializer(serializers.ModelSerializer):

    owner = UserSerializer(many=False, read_only=True)
    users = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Device
        fields = ('id', 'friendly_name', 'serial', 'slots', 'is_active', 'users', 'owner')