from django.conf import settings
from django.db import models
from model_utils.models import TimeStampedModel
from slugify import slugify


class DeviceUsersGroup(TimeStampedModel):

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL,
                                   related_name="owned_groups")

    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL,
                                   related_name="update_groups")

    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=50, unique=True)

    device = models.ForeignKey("Device",
                               null=True, on_delete=models.SET_NULL,
                               related_name="user_groups")

    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="users_groups", blank=True)

    def add_member(self, member):
        self.members.add(member)

    def set_device(self, device):
        self.device = device

    def clear_members(self):
        self.members.clear()

    def save(self, *args, **kwargs):
        # create slug with friendly_name
        if self.name is not None:
            self.code = slugify(self.name)

        return super(DeviceUsersGroup, self).save(*args, **kwargs)
