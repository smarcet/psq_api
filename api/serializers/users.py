from rest_framework import serializers
from ..models import User


class ReadUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'bio', 'is_active', 'first_name', 'last_name', 'role')


class WritableUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'bio', 'is_active', 'first_name', 'last_name')


class WritableAdminUserSerializer(WritableUserSerializer):

    def create(self, validated_data):
        validated_data['role'] = User.TEACHER
        instance = User.objects.create(**validated_data)
        return instance


class WritableRawUserSerializer(WritableUserSerializer):

    def create(self, validated_data):
        validated_data['role'] = User.STUDENT
        instance = User.objects.create(**validated_data)
        return instance