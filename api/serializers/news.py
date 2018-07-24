
from rest_framework import serializers
from ..serializers.users import ReadUserSerializer
from ..models import News


class ReadNewsSerializer(serializers.ModelSerializer):

    created_by = ReadUserSerializer()

    class Meta:
        model = News
        fields = ('id', 'title', 'body', 'created_by', 'created')


class WriteNewsSerializer(serializers.ModelSerializer):

    class Meta:
        model = News
        fields = ('title', 'body')