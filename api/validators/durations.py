from ..models import ModelValidationException
from django.utils.translation import ugettext_lazy as _


def validate_duration(value):
    if value <= 0:
        raise ModelValidationException(_("duration should be greater than 0 seconds"))

def validate_max_duration(value):
    if value <= 0:
        raise ModelValidationException(_("max duration should be greater than 0 seconds"))
