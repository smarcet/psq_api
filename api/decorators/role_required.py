from django.utils.functional import wraps
from ..exceptions.authz_error import AuthzError
from django.utils.translation import ugettext_lazy as _


def role_required(required_role):
    def _decorator(view_func):
        def __decorator(view, *args, **kwargs):
            request = view.request
            user = request.user

            if user is None:
                raise AuthzError(_("user is not present"))

            if required_role is not None and required_role > user.role:
                raise AuthzError(_("you need role {role}").format(role=required_role))

            response = view_func(view, request)
            return response

        return wraps(view_func)(__decorator)
    return _decorator
