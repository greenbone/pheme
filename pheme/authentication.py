import logging
from typing import Callable, Tuple, Union

from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from rest_framework.request import HttpRequest

import requests
from requests.models import Response
import xmltodict

from pheme import settings


logger: logging.Logger = logging.getLogger(__name__)

# pylint falsly identifies Union as unsubscriptable-object in python 3.9
# pylint: disable=E1136


def __gsad_user_role(
    token: str, gsad_sid: str, *, gsad_url: str, get: Callable
) -> Tuple[Union[str, None], Union[str, None]]:
    if not gsad_url:
        logger.warning("no gsad url")
        return None, None
    params = {"token": token, "cmd": "get_users"}
    cookies = dict(GSAD_SID=gsad_sid)
    response: Response = get(gsad_url, params=params, cookies=cookies)
    resp = xmltodict.parse(
        response.text, attr_prefix="", cdata_key="text", dict_constructor=dict
    ).get("envelope")
    return resp.get("login"), resp.get("role")


def get_username_role(
    request: HttpRequest,
    *,
    gsad_url: str = settings.GSAD_URL,
    get: Callable = requests.get
) -> Tuple[Union[str, None], Union[str, None]]:
    """
    returns a username and a role when it got found based on the request.

    So far only gsad is supported.
    Parameter:
        request: HttpRequest, the incoming request is used to get information
        gsad_url: str, when using gsad the url of gsad must be set, default is
            pheme.settings.GSAD_URL
        get: Callable, a lambda to get the user and tole. It must return a
            requests.models.Response

    Returns:
        A tuple either None, None or user, role
    """
    gsad_sid = request.COOKIES.get("GSAD_SID")
    token = request.query_params.get("token")
    if token and gsad_sid:
        return __gsad_user_role(token, gsad_sid, gsad_url=gsad_url, get=get)
    return None, None


class SimpleApiKeyAuthentication(BaseAuthentication):
    def authenticate(self, request: HttpRequest):
        api_key = request.META.get("HTTP_X_API_KEY", "")
        if api_key != settings.SECRET_KEY:
            raise exceptions.AuthenticationFailed("Invalid api-key.")


class LoggedInAsAUser(BaseAuthentication):
    def authenticate(self, request: HttpRequest):
        username, role = get_username_role(request)
        if username is None:
            return None
        request.META["GVM_USERNAME"] = username
        request.META["GVM_ROLE"] = username
        return (username, role)
