from rest_framework import serializers
from api.models import ModelValidationException
from ..serializers import ReadUserSerializer, ReadDeviceSerializer
from ..models import Device
from ..models import User
from ..models import Exercise
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

    class Meta:
        model = Exercise
        fields = ('id', 'created', 'modified', 'title', 'abstract', 'max_duration', 'type', 'author',
                  'allowed_devices', 'allowed_tutorials')


class WriteableExerciseSerializer(serializers.ModelSerializer):
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

    class Meta:
        model = Exercise
        fields = ('id', 'title', 'abstract', 'max_duration', 'type', 'author', 'allowed_devices', 'allowed_tutorials')
