from rest_framework import serializers
from ..serializers.users import UserSerializer
from ..models import Device
from ..models import User


class ReadDeviceSerializer(serializers.ModelSerializer):
    owner = UserSerializer()
    users = UserSerializer(many=True)
    admins = UserSerializer(many=True)

    class Meta:
        model = Device
        fields = (
        'id', 'mac_address', 'last_know_ip', 'friendly_name', 'serial', 'slots', 'is_active', 'owner', 'users', 'admins')


class NullableDeviceSerializer(serializers.ModelSerializer):
    pass

    class Meta:
        model = Device
        exclude = ('id', 'mac_address', 'last_know_ip', 'friendly_name', 'serial', 'slots', 'is_active', 'owner', 'users', 'admins')


class WriteableDeviceSerializer(serializers.ModelSerializer):

    owner = serializers.PrimaryKeyRelatedField(many=False, queryset= User.objects.all())
    users = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all(), required=False)
    admins = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all(), required=False)

    def create(self, validated_data):
        owner = validated_data.pop('owner')
        users = []
        admins = []

        if 'users' in validated_data:
            users = validated_data.pop('users')

        if 'admins' in validated_data:
            admins = validated_data.pop('admins')

        instance = Device.objects.create(**validated_data)

        for user in users:
            instance.add_user(user)

        for user in admins:
            instance.add_admin(user)

        instance.set_owner(owner)
        return instance


    class Meta:
        model = Device
        fields = ('id', 'mac_address', 'last_know_ip', 'friendly_name', 'serial', 'slots', 'is_active', 'owner', 'users', 'admins')