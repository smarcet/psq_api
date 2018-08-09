from django.conf import settings
from django.db import models
from model_utils.models import TimeStampedModel
from datetime import datetime
from django.utils.crypto import get_random_string
import hashlib
from ..models import MailRequest
from django.utils.translation import ugettext_lazy as _
import pytz


class ResetPasswordRequest(TimeStampedModel):
    REQUEST_HASH_LEN = 255
    REQUEST_HASH_ALLOWED_CHARS = 'abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ0123456789'

    request_hash = models.CharField(max_length=REQUEST_HASH_LEN, blank=True)

    processed_date = models.DateTimeField(null=True)
    is_processed = models.BooleanField(default=False)

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             null=True, on_delete=models.SET_NULL,
                             related_name="reset_password_request")

    def mark_as_sent(self):
        self.is_processed = True
        self.processed_date = datetime.utcnow().replace(tzinfo=pytz.UTC)

    @staticmethod
    def generates_registration_token():
        return get_random_string(ResetPasswordRequest.REQUEST_HASH_LEN, ResetPasswordRequest.REQUEST_HASH_ALLOWED_CHARS)

    def _generate_request_email(self):
        registration_token = ResetPasswordRequest.generates_registration_token()
        self.request_hash = hashlib.md5(registration_token.encode('utf-8')).hexdigest()
        # defined on .po file
        body = _("We heard that you lost your PSQ password. Sorry about that! \n" 
                 "But don’t worry! You can use the following link to reset your password: \n" 
                 "<a href='{href}'>Clicking Here</a> \n" 
                 "If you don’t use this link within 3 hours, it will expire. To get a new password \n" 
                 "reset link, visit {password_reset_link} \n" 
                 "Thanks, \n" 
                 "Your friends at PSQ \n"
                 ).format(
            href="{base_url}/password-reset/{registration_token}".format(base_url = settings.WEB_DOMAIN,
                                                                         registration_token = registration_token),
            password_reset_link="{base_url}/password-reset".format(base_url=settings.WEB_DOMAIN),
        )

        mail_request = MailRequest(
            to_address=self.user.email,
            from_address=settings.FROM_EMAIL,
            subject=_("[PSQ] Please reset your password"),
            body=body
        )

        mail_request.save()

    def save(self, *args, **kwargs):
        if self.id is None:
            self._generate_request_email()

        return super(ResetPasswordRequest, self).save(*args, **kwargs)