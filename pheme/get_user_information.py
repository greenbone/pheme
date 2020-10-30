from typing import Optional

import requests
import xmltodict
from requests.models import Response
from rest_framework.request import HttpRequest

from pheme import settings


def __gsad_user_role(
    token: str, gsad_sid: str, gsad_url: str = settings.GSAD_URL
) -> Optional[str]:
    if not gsad_url:
        print("no gsad url")
        return None, None
    params = {"token": token, "cmd": "get_users"}
    cookies = dict(GSAD_SID=gsad_sid)
    response: Response = requests.get(gsad_url, params=params, cookies=cookies)
    resp = xmltodict.parse(
        response.text, attr_prefix='', cdata_key='text', dict_constructor=dict
    ).get('envelope')
    return resp.get('login'), resp.get('role')


def get_username_role(request: HttpRequest):
    gsad_sid = request.COOKIES.get('GSAD_SID')
    token = request.query_params.get('token')
    if token and gsad_sid:
        return __gsad_user_role(token, gsad_sid)
    return None, None
