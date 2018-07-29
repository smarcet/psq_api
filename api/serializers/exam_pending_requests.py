from django.db.models import Q
from rest_framework import serializers

from api.models import ModelValidationException
from ..models import ExamPendingRequestVideo, ExamPendingRequest, User, Device, Exercise


class ExamPendingRequestVideoWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamPendingRequestVideo
        fields = ('file', )


class ExamPendingRequestWriteSerializer(serializers.ModelSerializer):
    taker = serializers.PrimaryKeyRelatedField(many=False, queryset=User.objects.filter(
        Q(role=User.STUDENT) | Q(role=User.TEACHER)))
    exercise = serializers.PrimaryKeyRelatedField(many=False, queryset=Exercise.objects.all())
    device = serializers.PrimaryKeyRelatedField(many=False, queryset=Device.objects.all())

    def create(self, validated_data):
        device = validated_data.pop('device')
        taker = validated_data.pop('taker')

        if not device.is_allowed_user(taker):
            raise ModelValidationException(
                _("user {user_id} is not allowed to use device {device_id}").format(user_id=taker.id,
                                                                                    device_id=device.id))
        instance = ExamPendingRequest.objects.create(**validated_data)

        return instance.set_taker(taker).set_device(device)

    class Meta:
        model = ExamPendingRequest
        fields = ('taker', 'exercise', 'device', 'duration' )