import logging
from typing import Callable, Optional

import requests
import xmltodict
from requests.models import Response
from rest_framework.request import HttpRequest

from pheme import settings


logger: logging.Logger = logging.getLogger(__name__)


def __gsad_user_role(
    token: str, gsad_sid: str, *, gsad_url: str, get: Callable
) -> Optional[str]:
    if not gsad_url:
        logger.warning("no gsad url")
        return None, None
    params = {"token": token, "cmd": "get_users"}
    cookies = dict(GSAD_SID=gsad_sid)
    response: Response = get(gsad_url, params=params, cookies=cookies)
    resp = xmltodict.parse(
        response.text, attr_prefix='', cdata_key='text', dict_constructor=dict
    ).get('envelope')
    return resp.get('login'), resp.get('role')


def get_username_role(
    request: HttpRequest,
    *,
    gsad_url: str = settings.GSAD_URL,
    get: Callable = requests.get
):
    gsad_sid = request.COOKIES.get('GSAD_SID')
    token = request.query_params.get('token')
    if token and gsad_sid:
        return __gsad_user_role(token, gsad_sid, gsad_url=gsad_url, get=get)
    return None, None
