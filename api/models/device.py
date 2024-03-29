from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel
from api.models import User
from ..models import ModelValidationException
from django.utils.crypto import get_random_string
import uuid
import hashlib
from macaddress.fields import MACAddressField
from slugify import slugify


class Device(TimeStampedModel):

    STREAM_KEY_LEN = 255
    STREAM_KEY_ALLOWED_CHARS = 'abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ0123456789-_'

    serial = models.CharField(max_length=255, unique=True, null=False, default=uuid.uuid4)
    mac_address =  MACAddressField(integer=False, unique=True)
    last_know_ip = models.GenericIPAddressField()
    friendly_name = models.CharField(max_length=255, unique=True, null=True, blank=True)
    slots = models.PositiveSmallIntegerField(default=3, null=False)
    is_active = models.BooleanField( default=False)
    is_verified = models.BooleanField( default=False)
    stream_key = models.CharField(max_length=255, blank=True, null=True, unique=True)
    slug = models.CharField(max_length=255, blank=True, null=True, unique=True)

    # relations

    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              blank=True,
                              null=True, on_delete=models.SET_NULL,
                              related_name="owned_devices")

    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="assigned_devices", blank=True)

    admins = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="managed_devices", blank=True)

    def add_user(self, user):
        if self.available_slots() == 0:
            raise ModelValidationException(_("no more available free slots"))

        if user in self.users.all():
            raise ModelValidationException(_("user %s is already an allowed user") % user.id)

        if user.id == self.owner.id:
            raise ModelValidationException(_("user %s is already device owner") % user.id)

        self.users.add(user)
        self.save()

    def remove_user(self, user):
        if user not in self.users.all():
            raise ModelValidationException(_("user %s is not an allowed user") % user.id)
        self.users.remove(user)
        self.save()

    def add_admin(self, user):
        if self.available_slots() == 0:
            raise ModelValidationException(_("no more available free slots"))

        if user in self.admins.all():
            raise ModelValidationException(_("user %s is already an admin") % user.id)

        if user.id == self.owner.id:
            raise ModelValidationException(_("user %s is already device owner") % user.id)

        self.admins.add(user)
        self.save()

    def remove_admin(self, user):
        if user not in self.admins.all():
            raise ModelValidationException(_("user %s is not an admin") % user.id)
        self.admins.remove(user)
        self.save()

    def set_owner(self, owner):
        self.owner = owner
        self.save()

    def available_slots(self):
        consumed_slots = self.admins.count() + self.users.count()
        return self.slots - consumed_slots

    def is_allowed_admin(self, user):

        if user.role == User.SUPERVISOR:
            return True

        if self.owner == user:
            return True

        if user in self.admins.all():
            return True

        return False

    def is_allowed_user(self, user):
        if user in self.users.all():
            return True

        if self.is_allowed_admin(user):
            return True

        return False

    def clean(self):
        pass

    @staticmethod
    def generates_stream_token():
        return get_random_string(Device.STREAM_KEY_LEN, Device.STREAM_KEY_ALLOWED_CHARS)

    def do_verify(self):
        self.is_verified = True
        self.is_active = True
        if self.stream_key is None:
            while True:
                new_stream_token = Device.generates_stream_token()
                self.stream_key = hashlib.md5(new_stream_token.encode('utf-8')).hexdigest()
                if Device.objects.filter(stream_key=self.stream_key).count() == 0:
                    break

    def unlink_from_owner(self):
        self.owner = None
        self.save()

    def is_owned_by(self, user):
        return self.owner is not None and self.owner.id == user.id

    def link_to(self, user):
        if user.role != User.TEACHER:
            raise ModelValidationException(_("user %s is not an allowed admin user") % user.id)
        self.owner = user
        self.save()

    def save(self, *args, **kwargs):
        # create slug with friendly_name
        if self.friendly_name is not None:
            self.slug = slugify(self.friendly_name)

        return super(Device, self).save(*args, **kwargs)
