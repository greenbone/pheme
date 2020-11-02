import mimetypes
import logging
from typing import Dict, Callable
from pathlib import Path
import json
import rest_framework
from django.core.files.uploadedfile import UploadedFile
from rest_framework.decorators import (
    api_view,
    parser_classes,
    renderer_classes,
    authentication_classes,
)
from rest_framework.request import HttpRequest
from rest_framework.response import Response
from pheme.datalink import as_datalink
from pheme import settings
import pheme.authentication


logger = logging.getLogger(__name__)

mimetypes.add_type('text/scss', '.scss')


def load_params(from_path: str = settings.PARAMETER_FILE_ADDRESS) -> Dict:
    param_file_obj = Path(from_path)
    return (
        json.loads(param_file_obj.read_text())
        if param_file_obj.exists()
        else {}
    )


def __store(params: Dict, *, from_path: str = None) -> Dict:
    Path(from_path).write_text(json.dumps(params))
    return params


def __put(
    request: HttpRequest,
    func: Callable[[HttpRequest, Dict], Dict],
    *,
    from_path: str = settings.PARAMETER_FILE_ADDRESS,
    store: Callable[[Dict, str], Dict] = __store
) -> Response:
    params = load_params(from_path=from_path)
    username = request.META.get('GVM_USERNAME')
    if username:
        all_user = params.get('user_specific', {})
        specific_user_params = all_user.get(username, {})
        specific_user_params = func(request, specific_user_params)
        all_user[username] = specific_user_params
        params['user_specific'] = all_user
        value = params
    else:
        value = func(request, params)
    return Response(store(value, from_path=from_path))


def __process_form_data(request: HttpRequest, data: Dict) -> Dict:
    for (key, value) in request.data.items():
        if isinstance(value, UploadedFile):
            file_type, _ = mimetypes.guess_type(value.name)
            logger.info(
                "uploading filetype %s/%s for %s",
                file_type,
                value.name,
                key,
            )
            if file_type and file_type.startswith('image'):
                data[key] = as_datalink(value.read(), file_type)
            elif file_type and file_type.startswith('text'):
                data[key] = value.read().decode()
            else:
                raise ValueError("Only image or text is permitted")
        else:
            data[key] = value
    return data


def __process_json_object(request: HttpRequest, data: Dict) -> Dict:
    return {**data, **request.data}


@api_view(['PUT'])
@parser_classes([rest_framework.parsers.JSONParser])
@renderer_classes(
    [
        rest_framework.renderers.JSONRenderer,
    ]
)
@authentication_classes(
    [
        pheme.authentication.LoggedInAsAUser,
        pheme.authentication.SimpleApiKeyAuthentication,
    ]
)
def put_value(
    request: HttpRequest,
    key: str,
) -> Response:
    def __process_single_value(request: HttpRequest, data: Dict) -> Dict:
        data[key] = request.data
        return data

    return __put(request, __process_single_value)


@api_view(['PUT'])
@parser_classes(
    [rest_framework.parsers.JSONParser, rest_framework.parsers.MultiPartParser]
)
@renderer_classes(
    [
        rest_framework.renderers.JSONRenderer,
    ]
)
@authentication_classes(
    [
        pheme.authentication.LoggedInAsAUser,
        pheme.authentication.SimpleApiKeyAuthentication,
    ]
)
def put(request: HttpRequest) -> Response:

    if request.content_type == "application/json":
        return __put(request, __process_json_object)
    return __put(request, __process_form_data)
