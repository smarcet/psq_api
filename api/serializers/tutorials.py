from rest_framework import serializers
from api.models import ModelValidationException
from ..serializers import ReadUserSerializer, ReadDeviceSerializer, ReadExerciseSerializer
from ..models import Exercise, User, Device, Tutorial
from django.utils.translation import ugettext_lazy as _


class TutorialReadSerializer(serializers.ModelSerializer):

    taker = ReadUserSerializer()
    exercise = ReadExerciseSerializer()
    device = ReadDeviceSerializer()

    class Meta:
        model = Tutorial
        fields = ('id', 'created', 'modified', 'title', 'notes', 'duration', 'taker', 'exercise', 'device',
                  )


class TutorialWriteSerializer(serializers.ModelSerializer):

    taker = serializers.PrimaryKeyRelatedField(many=False, queryset=User.objects.filter(role=User.TEACHER))
    exercise = serializers.PrimaryKeyRelatedField(many=False, queryset=Exercise.objects.filter(type=Exercise.TUTORIAL))
    device = serializers.PrimaryKeyRelatedField(many=False, queryset=Device.objects.all())

    def create(self, validated_data):
        device = validated_data.pop('device')
        taker = validated_data.pop('taker')

        if not device.is_allowed_admin(taker):
            raise ModelValidationException(
                _("user {user_id} is not allowed to admin device {device_id}").format(user_id=taker.id,
                                                                                      device_id=device.id))
        instance = Tutorial.objects.create(**validated_data)

        return instance.set_taker(taker).set_device(device)
       
    class Meta:
        model = Tutorial
        fields = ('id', 'created', 'modified', 'title', 'notes', 'duration', 'taker', 'exercise', 'device',
                  )