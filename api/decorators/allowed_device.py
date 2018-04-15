from django.utils.functional import wraps
from ..exceptions.authz_error import AuthzError
from django.utils.translation import ugettext_lazy as _
from ..models import Device


def allowed_device():
    def _decorator(view_func):
        def __decorator(view, *args, **kwargs):
            request = view.request
            device_id = request.query_params.get('pk')
            try:
                device = Device.objects.get(pk=device_id)
                if not device.is_allowed_admin(request.user):
                    raise AuthzError(_("you are not allowed to admin device {device_id}").format(device_id=device_id))
            except AuthzError as ex1:
                raise ex1
            finally:
                return view_func(view, request)
        return wraps(view_func)(__decorator)
    return _decorator
