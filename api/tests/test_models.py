from ..models import User
from ..models import Device
from ..models import ModelValidationException
from django.test import TestCase
from django.utils.translation import ugettext_lazy as _


class TestModels(TestCase):

    @classmethod
    def setUpTestData(cls):
        User.objects.create(email='test@test.com', first_name='Bob', last_name ='Uncle', role = User.TEACHER)

    def test_create_device(self):
        owner = User.objects.get(id=1)
        admin = User.objects.create(email='test1@test.com', first_name='Bob1', last_name='Uncle1', role=User.TEACHER)
        student = User.objects.create(email='test2@test.com', first_name='Bob2', last_name='Uncle2', role=User.STUDENT)

        device = Device.objects.create(owner=owner, serial= "1234567", slots=3)
        device.add_admin(admin)
        device.add_user(student)

        self.assertTrue(device.available_slots() == 1)

    def test_create_device_user_assigned_twice_fail(self):

        owner = User.objects.get(id=1)
        student = User.objects.create(email='test2@test.com', first_name='Bob2', last_name='Uncle2', role=User.STUDENT)

        device = Device.objects.create(owner=owner, serial="1234567", slots=3)
        device.add_user(student)
        # add the same user twice will fail
        with self.assertRaises(ModelValidationException) as cm:
            device.add_user(student)

        the_exception = cm.exception
        self.assertEqual(str(the_exception), _("user is already an user"))

    def test_create_device_empty_available_slots(self):
        owner = User.objects.get(id=1)
        student = User.objects.create(email='test2@test.com', first_name='Bob2', last_name='Uncle2', role=User.STUDENT)

        device = Device.objects.create(owner=owner, serial="1234567", slots=1)
        device.add_user(student)
        # add another user will fail bc no more available slots
        with self.assertRaises(ModelValidationException) as cm:
            device.add_admin(student)

        the_exception = cm.exception
        self.assertEqual(str (the_exception), _("no more available free slots"))