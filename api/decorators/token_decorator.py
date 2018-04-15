from django.utils.functional import wraps
from rest_framework import status
from rest_framework.response import Response
from ..exceptions.authz_error import AuthzError
from ..jwt.utils import JSONWebTokenValidator
from django.utils.translation import ugettext_lazy as _


def token_required(required_role = None):
    def _decorator(view_func):
        def __decorator(view, *args, **kwargs):
            request = view.request
            token = request.query_params.get('token')
            if token is None:
                return Response(status=status.HTTP_401_UNAUTHORIZED, data=_("missing token param"))

            validator = JSONWebTokenValidator()

            result = validator.validate(token=token)
            user = result['user']
            if required_role is not None and required_role != user.role:
                raise AuthzError(_("you need role {role}").format(role=required_role))

            response = view_func(view, request)
            return response

        return wraps(view_func)(__decorator)
    return _decorator
