#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pheme/scripts/parameter.py
# Copyright (C) 2020 Greenbone Networks GmbH
#
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


# Usage: pheme-parameter $path
import os
import json
import mimetypes
from argparse import ArgumentParser
from urllib.parse import urlparse, ParseResult
from typing import Dict
import http.client
import pathlib

from pheme.datalink import as_datalink

from pheme.settings import SECRET_KEY

PHEME_URL = os.getenv('PHEME_URL', 'https://localhost:8443/pheme')
COLOR_KEYS = ['main_color']
PICTURE_KEYS = ['logo', 'background']
ALLOWED_KEYS = COLOR_KEYS + PICTURE_KEYS


def __init_argument_parser() -> ArgumentParser:
    value_description = """The value for given key.
    If key is in {color} than it must represent color (e.g. #66c430).
    If the key is in {pics} than it must be a path to a svg, png or jpeg file.
    """.format(
        color=COLOR_KEYS, pics=PICTURE_KEYS
    )
    parser = ArgumentParser(
        description='Adds parameter to pheme.',
        prog='pheme-parameter',
    )
    parser.add_argument(
        '--key',
        help='Identifier of a parameter to set. Valid keys are: {}'.format(
            ALLOWED_KEYS
        ),
        required=True,
    )
    parser.add_argument(
        '--value',
        help=value_description,
        required=True,
    )
    return parser


def __load_data(parent: pathlib.Path) -> Dict:
    data = {}
    file_type, _ = mimetypes.guess_type(parent.name)
    key = parent.name[: -len(parent.suffix)]
    if file_type and file_type.startswith('image'):
        data[key] = as_datalink(parent.read_bytes(), file_type)
    else:
        raise ValueError(
            "Unknown mimetype {} for {}.".format(file_type, parent)
        )
    return data


def __put(data: Dict) -> (ParseResult, Dict):
    def connection():
        parsed = urlparse(PHEME_URL)
        if parsed.scheme == 'https':
            return parsed, http.client.HTTPSConnection(parsed.netloc)
        else:
            return parsed, http.client.HTTPConnection(parsed.netloc)

    url, conn = connection()
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': SECRET_KEY,
    }
    params = json.dumps(data)
    conn.request('PUT', url.path + '/parameter', params, headers)
    response = conn.getresponse()
    if response.status != 200:
        raise ValueError(
            "failed to upload parameter. Response code is {}.".format(
                response.status
            )
        )
    response_txt = response.read()
    response.close()
    conn.close()
    return json.loads(response_txt)


def main(args=None):
    data = {}
    parser = __init_argument_parser()
    arguments = parser.parse_args(args)
    if arguments.key in COLOR_KEYS:
        data[arguments.key] = arguments.value
    elif arguments.key in PICTURE_KEYS:
        parent = pathlib.Path(arguments.value)
        data = {**data, **__load_data(parent)}
    else:
        raise ValueError("{} is not defined".format(arguments.key))
    return __put(data)


if __name__ == "__main__":
    main()
    print("success")
