from django.db.models import Q
from rest_framework import serializers
from ..serializers import ReadUserSerializer, ReadDeviceSerializer
from ..models import Exercise, Exam, User, Device, ModelValidationException
from django.utils.translation import ugettext_lazy as _


class ReadTutorialSerializer(serializers.ModelSerializer):
    videos = serializers.SerializerMethodField()

    class Meta:
        model = Exercise
        fields = ('id', 'created', 'modified', 'title', 'abstract', 'max_duration', 'type', 'author', 'videos')

    def get_videos(self, tutorial):
        request = self.context.get('request')
        videos = []
        for instance in tutorial.exams.all():
            for video in instance.videos.all():
                if not video.file:
                    continue
                video_url = video.file.url
                videos.append({
                    'video_url': request.build_absolute_uri(video_url),
                    'type': video.type
                })
        return videos


class ReadExerciseSerializer(serializers.ModelSerializer):
    author = ReadUserSerializer()
    allowed_devices = ReadDeviceSerializer(many=True)
    allowed_tutorials = ReadTutorialSerializer(many=True)
    is_shared = serializers.SerializerMethodField()

    def get_is_shared(self, exercise):
        request = self.context.get('request')
        current_user = request.user
        for device in current_user.my_devices:
            if exercise.is_shared_with(device):
                return True
        return False

    class Meta:
        model = Exercise
        fields = ('id', 'created', 'modified', 'title', 'abstract', 'max_duration', 'type', 'author',
                  'allowed_devices', 'allowed_tutorials', 'is_shared', 'daily_repetitions', 'practice_days')


class StudentReadExerciseSerializer(ReadExerciseSerializer):

    takes = serializers.SerializerMethodField()

    class Meta:
        model = Exercise
        fields = ('id', 'created', 'modified', 'title', 'abstract', 'max_duration', 'type', 'author',
                  'allowed_devices', 'takes', 'daily_repetitions', 'practice_days')

    def get_takes(self, exercise):
        request = self.context.get('request')
        current_user = request.user
        return Exam.objects.filter(Q(taker=current_user) & Q(exercise=exercise)).count()


class WriteableExerciseSerializer(serializers.ModelSerializer):
    EXERCISE_MAX_DURATION = 120 * 60
    EXERCISE_MIN_DURATION = 60

    author = serializers.PrimaryKeyRelatedField(many=False, queryset=User.objects.filter(role=User.TEACHER))
    allowed_devices = serializers.PrimaryKeyRelatedField(many=True, queryset=Device.objects.all(), required=False)
    allowed_tutorials = serializers.PrimaryKeyRelatedField(many=True,
                                                           queryset=Exercise.objects.filter(type=Exercise.TUTORIAL),
                                                           required=False)

    def create(self, validated_data):
        author = validated_data.pop('author')
        allowed_devices = []

        if 'allowed_devices' in validated_data:
            allowed_devices = validated_data.pop('allowed_devices')
            for device in allowed_devices:
                if not device.is_allowed_admin(author):
                    raise ModelValidationException(
                        _("user {user_id} is not allowed to admin device {device_id}").format(user_id=author.id,
                                                                                              device_id=device.id))
        allowed_tutorials = []
        if 'allowed_tutorials' in validated_data:
            allowed_tutorials = validated_data.pop('allowed_tutorials', [])

        instance = Exercise.objects.create(**validated_data)

        for device in allowed_devices:
            instance.add_allowed_device(device)

        for tutorial in allowed_tutorials:
            instance.add_tutorial(tutorial)

        instance.set_author(author)

        return instance

    def validate_max_duration(self, value):

        if value <= self.EXERCISE_MIN_DURATION:
            raise serializers.ValidationError(_("max duration can not be lower than {min_duration} seconds".format(
                min_duration=self.EXERCISE_MIN_DURATION)))

        if value > self.EXERCISE_MAX_DURATION:
            raise serializers.ValidationError(_("max duration can not be greater than {max_duration} seconds".format(
                max_duration=self.EXERCISE_MAX_DURATION)))
        return value

    class Meta:
        model = Exercise
        fields = ('id', 'title', 'abstract', 'max_duration', 'type', 'author', 'allowed_devices', 'allowed_tutorials',
                  'daily_repetitions', 'practice_days')
