from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from rest_framework.request import Request
from pheme.settings import SECRET_KEY


class SimpleApiKeyAuthentication(BaseAuthentication):
    def authenticate(self, request: Request):
        api_key = request.META.get('HTTP_X_API_KEY', "")
        if api_key != SECRET_KEY:
            raise exceptions.AuthenticationFailed('Invalid api-key.')
