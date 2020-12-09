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
    value_description = f"""The value for given key.
    If key is in {COLOR_KEYS} than it must represent color (e.g. #66c430).
    If the key is in {PICTURE_KEYS} than it must be a path to a svg, png or jpeg file.
    """
    key_description = (
        f'Identifier of a parameter to set. Valid keys are: {ALLOWED_KEYS}'
    )
    parser = ArgumentParser(
        description='Adds parameter to pheme.',
        prog='pheme-parameter',
    )
    parser.add_argument(
        '-k',
        '--key',
        help=key_description,
        required=True,
    )
    parser.add_argument(
        '-v',
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
        raise ValueError(f"Unknown mimetype {file_type} for {parent}.")
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
    print(headers)
    conn.request('PUT', url.path + '/parameter', params, headers)
    response = conn.getresponse()
    if response.status != 200:
        raise ValueError(
            f"failed to upload parameter. Response code is {response.status}."
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
        raise ValueError(f"{arguments.key} is not defined")
    return (arguments, __put(data))


if __name__ == "__main__":
    parsed_args, _ = main()
    print(f"successfully changed {parsed_args.key} to {parsed_args.value}")
