from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from api.models import ModelValidationException, ExamVideo
from ..models import Exercise, User, Device, Exam
from ..serializers import ReadUserSerializer, ReadDeviceSerializer, ReadExerciseSerializer, ReadUserSerializerMin, \
    ReadExerciseSerializerMin, ReadDeviceSerializerMin


class NullableExamSerializer(serializers.ModelSerializer):
    pass

    class Meta:
        model = Exam
        exclude =  fields = (
            'id', 'created', 'modified', 'notes', 'duration', 'approved', 'taker', 'evaluator',
                  'exercise', 'device', 'videos', 'video_shares', 'video_views'
        )


class VideoExamReadSerializer(serializers.ModelSerializer):

    video_url = serializers.SerializerMethodField()

    class Meta:
        model = ExamVideo
        fields = ('id', 'created', 'modified', 'video_url', 'type', 'views')

    def get_video_url(self, video):
        request = self.context.get('request')
        if not video.file:
            return None
        video_url = video.file.url
        return request.build_absolute_uri(video_url)


class Exam2VideoReadSerializer(serializers.ModelSerializer):
    taker = ReadUserSerializer()
    videos = VideoExamReadSerializer(many=True, read_only=True)
    exercise = ReadExerciseSerializer()
    device = ReadDeviceSerializer()

    class Meta:
        model = Exam
        fields = ('id', 'created', 'modified', 'duration', 'taker',
                  'exercise', 'device', 'videos', 'video_views'
                  )


class ExamReadSerializerList(serializers.ModelSerializer):
    taker = ReadUserSerializerMin()
    evaluator = ReadUserSerializerMin()
    exercise = ReadExerciseSerializerMin()
    device = ReadDeviceSerializerMin()
    created = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    modified = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = Exam
        fields = (
            'id',
            'created',
            'modified',
            'notes',
            'duration',
            'approved',
            'taker',
            'evaluator',
            'exercise',
            'device'
        )


class ExamReadSerializer(serializers.ModelSerializer):
    taker = ReadUserSerializer()
    evaluator = ReadUserSerializer()
    exercise = ReadExerciseSerializer()
    device = ReadDeviceSerializer()
    videos = VideoExamReadSerializer(many=True, read_only=True)
    created = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    modified = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = Exam
        fields = ('id', 'created', 'modified', 'notes', 'duration', 'approved', 'taker', 'evaluator',
                  'exercise', 'device', 'videos'
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

    evaluator = serializers.PrimaryKeyRelatedField(many=False, queryset=User.objects.filter(role=User.TEACHER))

    def update(self, instance, validated_data):
        evaluator = validated_data.pop('evaluator')
        approved = validated_data.get('approved', False)
        notes = validated_data.get('notes', None)
        device = instance.device

        if not device.is_allowed_admin(evaluator):
            raise ModelValidationException(
                _("user {user_id} is not allowed to manage device {device_id}").format(user_id=evaluator.id,
                                                                                       device_id=device.id))
        if approved:
            instance.approve(notes)
        else:
            instance.reject(notes)

        instance.set_evaluator(evaluator)

        return instance

    class Meta:
        model = Exam
        fields = ('evaluator', 'notes', 'approved')
