# -*- coding: utf-8 -*-
# Copyright (C) 2020-2021 Greenbone Networks GmbH
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
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


def __load_params(from_path: str) -> Dict:
    """
    either loads json file from given_path or returns an empty dict when file
    does not exist.

    """
    param_file_obj = Path(from_path)
    return (
        json.loads(param_file_obj.read_text())
        if param_file_obj.exists()
        else {}
    )


def load_params(
    system_parameter_path: str = settings.PARAMETER_FILE_ADDRESS,
    default_parameter_path: str = settings.DEFAULT_PARAMETER_ADDRESS,
) -> Dict:
    """
    loads default and system parameter and combines them so that system
    parameter may override default parameter.

    A system parameter is set and handled by an individual system while default
    parameter usually come from data-objects.
    """
    return {
        **__load_params(default_parameter_path),
        **__load_params(system_parameter_path),
    }


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
    params = __load_params(from_path=from_path)
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
    if not isinstance(request.data, dict):
        raise TypeError(
            "Request data is expected to be a dict, but it is {}".format(
                type(request.data)
            )
        )
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
