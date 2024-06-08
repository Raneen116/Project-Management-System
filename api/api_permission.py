from api.utils import custom_response
from rest_framework import status
from functools import wraps


def permit_if_role_in(roles=[]):

    def wrapper(decorated_function):
        @wraps(decorated_function)
        def check_permission(self, request, *args, **kwargs):
            if request.user.role in roles:
                return decorated_function(self, request, *args, **kwargs)
            return custom_response(
                message="You don't have the permission to access this endpoint.",
                status=status.HTTP_401_UNAUTHORIZED,
            )

        return check_permission

    return wrapper
