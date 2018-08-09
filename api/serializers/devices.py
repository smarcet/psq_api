from rest_framework import serializers
from ..models import ModelValidationException
from ..serializers.users import ReadUserSerializer
from ..models import Device
from ..models import User
from django.utils.translation import ugettext_lazy as _


class ReadDeviceSerializer(serializers.ModelSerializer):
    owner = ReadUserSerializer()
    users = ReadUserSerializer(many=True)
    admins = ReadUserSerializer(many=True)

    class Meta:
        model = Device
        fields = (
            'id', 'mac_address', 'last_know_ip', 'friendly_name', 'is_verified', 'stream_key', 'serial',
            'slots', 'is_active', 'owner', 'users', 'admins')


class ReadSuperAdminDeviceSerializer(serializers.ModelSerializer):
    owner = ReadUserSerializer()

    class Meta:
        model = Device
        fields = (
            'id', 'mac_address', 'last_know_ip', 'friendly_name', 'is_verified', 'stream_key', 'serial',
            'slots', 'is_active', 'owner')


class ReadBasicDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = (
            'id', 'friendly_name' )


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

    def update(self, instance, validated_data):
        slots = validated_data['slots']
        users = instance.admins.count() + instance.users.count()

        if slots < users :
            raise ModelValidationException(_("slots max. # cant be less than current users quantity!"))

        return super(WriteableDeviceSerializer, self).update(instance, validated_data)

    class Meta:
        model = Device
        fields = (
            'id', 'mac_address', 'last_know_ip', 'friendly_name', 'is_verified', 'slots', 'is_active', 'owner', 'users',
            'admins', 'serial')
