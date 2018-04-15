from ..models import User
from ..models import Device
from django.test import TestCase
from ..serializers import WriteableDeviceSerializer


class TestSerializers(TestCase):

    @classmethod
    def setUpTestData(cls):
        User.objects.create(email='test@test.com', first_name='Bob', last_name ='Uncle', role = User.TEACHER)
        User.objects.create(email='test1@test.com', first_name='Bob1', last_name='Uncle1', role=User.STUDENT)

    def test_device_create_serialization(self):

        data = {
            'serial': '123456',
            'friendly_name': 'device#1',
            'slots' : 3,
            'owner' : 1,
            'admins': [1],
            'users': [2]
        }

        device_serializer = WriteableDeviceSerializer(data=data)
        device_serializer.is_valid(raise_exception=True)
        device_serializer.save()

        device = Device.objects.get(id=1)

        self.assertTrue(device is not None)
        self.assertTrue(device.available_slots() == 1)

        return device

    def test_device_update_serialization(self):
        device = self.test_device_create_serialization()

        data = {
            'owner': 2,
            'users': [2]
        }

        device_serializer = WriteableDeviceSerializer(instance=device, data=data, partial=True)
        device_serializer.is_valid(raise_exception=True)
        device_serializer.save()

        device = Device.objects.get(id=1)

        return device

