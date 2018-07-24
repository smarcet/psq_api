from rest_framework import serializers
from ..serializers import ReadUserSerializer, ReadDeviceSerializer
from ..models import DeviceUsersGroup, User, Device
from django.utils.translation import ugettext_lazy as _


class ReadDeviceUsersGroupSerializer(serializers.ModelSerializer):
    created_by = ReadUserSerializer()
    updated_by = ReadUserSerializer()
    members = ReadUserSerializer(many=True)
    device = ReadDeviceSerializer()

    class Meta:
        model = DeviceUsersGroup
        fields = ('id', 'name', 'code', 'created_by', 'updated_by', 'members', 'device')


class WriteableDeviceUsersGroupSerializer(serializers.ModelSerializer):

    members = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all(), required=False)
    device = serializers.PrimaryKeyRelatedField(many=False, queryset=Device.objects.all(), required=True, allow_null=True)

    def create(self, validated_data):
        device = validated_data.pop('device')
        members = []

        if 'members' in validated_data:
            members = validated_data.pop('members')

        instance = DeviceUsersGroup.objects.create(**validated_data)

        for user in members:
            instance.add_member(user)

        instance.set_device(device)

        instance.save()

        return instance

    class Meta:
        model = DeviceUsersGroup
        fields = (
            'id', 'name', 'members', 'device'
        )
