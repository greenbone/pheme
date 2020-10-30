from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from rest_framework.request import HttpRequest
from pheme.settings import SECRET_KEY
from pheme.get_user_information import get_username_role


class SimpleApiKeyAuthentication(BaseAuthentication):
    def authenticate(self, request: HttpRequest):
        api_key = request.META.get('HTTP_X_API_KEY', "")
        if api_key != SECRET_KEY:
            raise exceptions.AuthenticationFailed('Invalid api-key.')


class LoggedInAsAUser(BaseAuthentication):
    def authenticate(self, request: HttpRequest):
        username, role = get_username_role(request)
        if username is None:
            return None
        request.META['GVM_USERNAME'] = username
        request.META['GVM_ROLE'] = username
        return (username, role)
