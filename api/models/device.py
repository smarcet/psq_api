from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel
from ..models import ModelValidationException


class Device(TimeStampedModel):

    serial = models.CharField(max_length=100, unique=True)
    mac_address = models.CharField(max_length=100, blank=True, null=True, unique=True)
    last_know_ip = models.CharField(max_length=50, blank=True)
    friendly_name = models.CharField(max_length=100, unique=True)
    slots = models.PositiveSmallIntegerField(default=3, null=False)
    is_active = models.BooleanField(_('active'), default=True)
    is_live =  models.BooleanField(_('live'), default=False)
    # relations

    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              null=True, on_delete=models.SET_NULL,
                              related_name="owned_devices")

    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="assigned_devices", blank=True)

    admins = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="managed_devices", blank=True)

    def add_user(self, user):
        if self.available_slots() == 0:
            raise ModelValidationException(_("no more available free slots"))

        if user in self.users.all():
            raise ModelValidationException(_("user %s is already an allowed user") % user.id)

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
        if self.owner == user:
            return True

        if user in self.admins:
            return True

        return False

    def clean(self):
        pass

