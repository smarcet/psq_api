from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.core.mail import send_mail
from ..managers.user_manager import UserManager
from django.contrib.auth.models import PermissionsMixin
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils.crypto import get_random_string
from django.utils.timezone import now
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
    pic = models.ImageField(upload_to = 'users', null=True, blank=True)
    # relations

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL,
                                   related_name="created_users")

    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL,
                                   related_name="updated_users")
    STUDENT = 1
    TEACHER = 2
    SUPERVISOR = 3
    ROLE_CHOICES = (
        (STUDENT, 'Student'),
        (TEACHER, 'Teacher'),
        (SUPERVISOR, 'Supervisor'),
    )
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    @staticmethod
    def generates_registration_token():
        return get_random_string(User.REGISTRATION_HASH_LEN, User.REGISTRATION_HASH_ALLOWED_CHARS)

    def get_full_name(self):
        '''
        Returns the first_name plus the last_name, with a space in between.
        '''
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def verify(self, raw_password):
        self.is_verified = True
        self.is_active = True
        self.date_verified = now()
        self.set_password(raw_password)
        self.save()

    def save(self, *args, **kwargs):

        if self.id is None:
            registration_token = User.generates_registration_token();
            self.registration_hash = hashlib.md5(registration_token.encode('utf-8')).hexdigest()
            # defined on .po file
            body=_("Please Confirm your Email <a href='{href}'>Clicking Here</a>").format(
                    href="%s/users/validate/%s" % (settings.WEB_DOMAIN, registration_token))
            send_mail(
                subject=_("Attention: You have been invited to PSQ Application!!!"),
                message=body,
                from_email=settings.FROM_EMAIL,
                recipient_list=[self.email, ],
                html_message=body,
            )
            # send registration email

        return super(User, self).save(*args, **kwargs)
