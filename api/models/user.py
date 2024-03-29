from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from ..models import MailRequest
from ..managers.user_manager import UserManager
from django.contrib.auth.models import PermissionsMixin
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils.crypto import get_random_string
from datetime import datetime
import hashlib


class User(AbstractBaseUser, PermissionsMixin):
    REGISTRATION_HASH_LEN = 255
    REGISTRATION_HASH_ALLOWED_CHARS = 'abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ0123456789'

    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    date_verified = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(_('active'), default=True)
    is_verified = models.BooleanField(_('verified'), default=False)
    is_staff = models.BooleanField(_('staff status'), default=False)
    registration_hash = models.CharField(max_length=REGISTRATION_HASH_LEN, blank=True)
    pic = models.ImageField(upload_to='users', null=True, blank=True)
    organization = models.CharField(_('organization'), max_length=255, blank=True)
    title = models.CharField(_('title'), max_length=255, blank=True)
    enrollment = models.CharField(_('enrollment'), max_length=255, blank=True)
    country = models.CharField(_('country'), max_length=3, blank=True)
    state = models.CharField(_('state'), max_length=255, blank=True)
    # relations

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL,
                                   related_name="created_users")

    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL,
                                   related_name="updated_users")
    GUEST = 0
    STUDENT = 1
    TEACHER = 2
    SUPERVISOR = 3
    ROLE_CHOICES = (
        (GUEST, 'Guest'),
        (STUDENT, 'Student'),
        (TEACHER, 'Teacher'),
        (SUPERVISOR, 'Supervisor'),
    )
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, null=True, blank=True)

    LEFT = 1
    RIGHT = 2
    HAND_CHOICES = (
        (LEFT, 'Left'),
        (RIGHT, 'Right'),

    )
    hand = models.PositiveSmallIntegerField(choices=HAND_CHOICES, null=True, blank=True)

    SPA = 1
    ENG = 2
    LANG_CHOICES = (
        (SPA, 'Spanish'),
        (ENG, 'English'),
    )
    locale = models.PositiveSmallIntegerField(choices=LANG_CHOICES, null=True, blank=True, default=SPA)

    bio = models.TextField(max_length=500, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    @property
    def is_guest(self):
        return self.role == User.GUEST

    @property
    def is_teacher(self):
        return self.role == User.TEACHER

    @property
    def is_supervisor(self):
        return self.role == User.SUPERVISOR

    @property
    def is_student(self):
        return self.role == User.STUDENT

    @property
    def allowed_admins(self):
        res = []
        assigned_devices = self.assigned_devices.all()
        for device in assigned_devices:
            if device.owner not in res:
                res.append(device.owner)
            for admin in device.admins.all():
                if admin not in res:
                    res.append(admin)
        return res

    @property
    def my_devices(self):
        managed_devices = self.managed_devices.all()
        owned_devices = self.owned_devices.all()
        return managed_devices | owned_devices

    @property
    def my_devices_ids(self):
        managed_devices = self.managed_devices.all().values_list('id', flat=True)
        owned_devices = self.owned_devices.all().values_list('id', flat=True)
        return managed_devices | owned_devices

    @staticmethod
    def generates_registration_token():
        return get_random_string(User.REGISTRATION_HASH_LEN, User.REGISTRATION_HASH_ALLOWED_CHARS)

    def can_create_role(self, role):
        current_role = self.role
        return int(current_role) >= int(role)

    def can_delete_user(self, user):
        current_role = self.role
        if current_role == User.SUPERVISOR:
            return True
        if user.created_by.id == self.id:
            return True
        return False

    def can_update_user(self, user):
        current_role = self.role
        if current_role == User.SUPERVISOR:
            return True
        if user.created_by.id == self.id:
            return True
        return False

    def get_full_name(self):
        '''
        Returns the first_name plus the last_name, with a space in between.
        '''
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def verify(self, raw_password):
        self.is_verified = True
        self.is_active = True
        self.date_verified = datetime.utcnow()
        self.set_password(raw_password)
        self.save()

    def set_email(self, new_email):
        old_email = self.email
        self.email = new_email
        if old_email != new_email and old_email != '' and self.id is not None:
            # reset email
            self._generate_user_verification_email()
        self.save()

    def _generate_user_verification_email(self):
        registration_token = User.generates_registration_token()
        self.registration_hash = hashlib.md5(registration_token.encode('utf-8')).hexdigest()
        self.is_verified = False
        self.is_active = False
        # defined on .po file
        body = _("Please Confirm your Email <a href='{href}'>Clicking Here</a>").format(
            href="%s/users/validate/%s" % (settings.WEB_DOMAIN, registration_token))

        mail_request = MailRequest(
            to_address=self.email,
            from_address=settings.FROM_EMAIL,
            subject=_("[PSQ] You have been invited to PSQ Application"),
            body=body
        )

        mail_request.save()

    def resend_verification(self):
        self._generate_user_verification_email()
        self.save()

    def save(self, *args, **kwargs):

        if self.id is None:
            self._generate_user_verification_email()

        return super(User, self).save(*args, **kwargs)
