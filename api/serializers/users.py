from rest_framework import serializers
from ..models import Device
from ..models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.password_validation import validate_password


class InternalReadDeviceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Device
        fields = (
            'id', 'mac_address', 'last_know_ip', 'friendly_name', 'is_verified', 'stream_key', 'serial',
            'slots', 'is_active')


class ReadUserSerializerMin(serializers.ModelSerializer):
    pic_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'bio', 'is_active',
                  'is_verified', 'first_name', 'last_name', 'role', 'pic',
                  'pic_url', 'locale',
                  'hand', 'organization', 'title', 'enrollment', 'country', 'state')

    def get_pic_url(self, user):
        request = self.context.get('request')
        if not user.pic:
            return None
        pic_url = user.pic.url
        return request.build_absolute_uri(pic_url)


class ReadUserSerializer(serializers.ModelSerializer):
    pic_url = serializers.SerializerMethodField()

    assigned_devices = InternalReadDeviceSerializer(many=True)
    managed_devices = InternalReadDeviceSerializer(many=True)
    owned_devices = InternalReadDeviceSerializer(many=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'bio', 'is_active',
                  'is_verified', 'first_name', 'last_name', 'role', 'pic',
                  'pic_url', 'assigned_devices', 'managed_devices', 'owned_devices', 'locale',
                  'hand', 'organization', 'title', 'enrollment', 'country', 'state')

    def get_pic_url(self, user):
        request = self.context.get('request')
        if not user.pic:
            return None
        pic_url = user.pic.url
        return request.build_absolute_uri(pic_url)


class WritableUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'email', 'bio', 'is_active', 'first_name', 'last_name', 'locale')


class RoleWritableUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'email', 'bio', 'is_active', 'first_name', 'last_name', 'role', 'locale', 'hand',
                  'organization', 'title', 'enrollment', 'country', 'state')

    def validate(self, data):
        """
        Check that the start is before the stop.
        """
        valid_roles = [
            User.TEACHER,
            User.STUDENT,
            User.SUPERVISOR,
            User.GUEST
        ]

        if not data['role'] in valid_roles :
            raise serializers.ValidationError(_("role has a non valid value"))
        return data


class WritableOwnUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'email', 'bio', 'first_name', 'last_name', 'locale',
                  'hand', 'organization', 'title', 'enrollment', 'country', 'state')

    def update(self, instance, validated_data):
        instance.set_email(validated_data.get('email', instance.email))
        instance.bio = validated_data.get('bio', instance.bio)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.locale = validated_data.get('locale', instance.locale)
        instance.hand = validated_data.get('hand', instance.hand)
        instance.organization = validated_data.get('organization', instance.organization)
        instance.title = validated_data.get('title', instance.title)
        instance.enrollment = validated_data.get('enrollment', instance.enrollment)
        instance.country = validated_data.get('country', instance.country)
        instance.state = validated_data.get('state', instance.state)
        instance.save()
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """
    password = serializers.CharField(required=True, min_length=8)
    password_confirmation = serializers.CharField(required=True)

    def validate(self, data):
        """
        Check that the start is before the stop.
        """
        if data['password'] != data['password_confirmation']:
            raise serializers.ValidationError(_("password and password confirmation should match"))

        validate_password(data['password'] )
        return data


class UserPicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','pic')


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


class WritableGuestUserSerializer(WritableUserSerializer):

    def create(self, validated_data):
        validated_data['role'] = User.GUEST
        instance = User.objects.create(**validated_data)
        return instance
