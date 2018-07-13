from rest_framework import serializers
from api.models import ModelValidationException, ExamVideo
from ..serializers import ReadUserSerializer, ReadDeviceSerializer, ReadExerciseSerializer
from ..models import Exercise, User, Device, Tutorial, Exam
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q


class ExamReadSerializer(serializers.ModelSerializer):
    taker = ReadUserSerializer()
    evaluator = ReadUserSerializer()
    exercise = ReadExerciseSerializer()
    device = ReadDeviceSerializer()

    class Meta:
        model = Exam
        fields = ('id', 'created', 'modified', 'notes', 'duration', 'approved', 'taker', 'evaluator',
                  'exercise', 'device'
                  )


class ExamVideoWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamVideo
        fields = ('file', 'author')


class ExamStudentWriteSerializer(serializers.ModelSerializer):
    taker = serializers.PrimaryKeyRelatedField(many=False, queryset=User.objects.filter(
        Q(role=User.STUDENT) | Q(role=User.TEACHER)))
    exercise = serializers.PrimaryKeyRelatedField(many=False, queryset=Exercise.objects.filter(type=Exercise.REGULAR))
    device = serializers.PrimaryKeyRelatedField(many=False, queryset=Device.objects.all())

    def create(self, validated_data):
        device = validated_data.pop('device')
        taker = validated_data.pop('taker')

        if not device.is_allowed_user(taker):
            raise ModelValidationException(
                _("user {user_id} is not allowed to use device {device_id}").format(user_id=taker.id,
                                                                                    device_id=device.id))
        instance = Exam.objects.create(**validated_data)

        return instance.set_taker(taker).set_device(device)

    class Meta:
        model = Exam
        fields = ('duration', 'taker', 'exercise', 'device')


class ExamEvaluatorWriteSerializer(serializers.ModelSerializer):
    device = serializers.PrimaryKeyRelatedField(many=False, queryset=Device.objects.all())
    evaluator = serializers.PrimaryKeyRelatedField(many=False, queryset=User.objects.filter(role=User.TEACHER))

    def update(self, instance, validated_data):
        evaluator = validated_data.pop('evaluator')
        device = validated_data.pop('device')
        approved = validated_data.get('approved', False)
        notes = validated_data.get('notes', None)

        if not device.is_allowed_admin(evaluator):
            raise ModelValidationException(
                _("user {user_id} is not allowed to manage device {device_id}").format(user_id=evaluator.id,
                                                                                       device_id=device.id))
        if approved:
            instance.approve(notes)
        else:
            return instance.reject(notes)

        instance.set_evaluator(evaluator)

    class Meta:
        model = Tutorial
        fields = ('evaluator', 'notes' 'device', 'approved')
