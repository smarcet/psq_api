from rest_framework import serializers
from ..serializers.users import ReadUserSerializer
from ..models import Device
from ..models import User


class ReadDeviceSerializer(serializers.ModelSerializer):
    owner = ReadUserSerializer()
    users = ReadUserSerializer(many=True)
    admins = ReadUserSerializer(many=True)

    class Meta:
        model = Device
        fields = (
            'id', 'mac_address', 'last_know_ip', 'friendly_name', 'is_verified', 'mac_address', 'stream_key', 'serial',
            'slots', 'is_active', 'owner', 'users', 'admins')


class NullableDeviceSerializer(serializers.ModelSerializer):
    pass

    class Meta:
        model = Device
        exclude = (
            'id', 'mac_address', 'last_know_ip', 'friendly_name', 'is_verified', 'mac_address', 'stream_key', 'serial',
            'slots', 'is_active', 'owner', 'users', 'admins', 'is_live')


class OpenRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ('mac_address', 'last_know_ip')
        read_only_fields = ('serial', 'stream_key', 'id')


class VerifyDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ('friendly_name', 'slots')


class WriteableDeviceSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(many=False, queryset=User.objects.all(), required=False, allow_null=True)
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
        fields = (
            'id', 'mac_address', 'last_know_ip', 'friendly_name', 'is_verified', 'slots', 'is_active', 'owner', 'users',
            'admins')
