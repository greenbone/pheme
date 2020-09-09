# -*- coding: utf-8 -*-
# pheme/transformation/storage.py
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
from pathlib import Path
from uuid import uuid4
from typing import Dict
import json


def __default_store_handler(name: str, value: Dict):
    json_value = json.dumps(value)
    Path('/tmp/{}.json'.format(name)).write_text(json_value)


def __default_load_handler(name: str) -> Dict:
    return json.loads(Path('/tmp/{}.json'.format(name)).read_text())


def load(name: str, *, handler=__default_load_handler) -> Dict:
    return handler(name)


def store(prefix: str, value: Dict, *, handler=__default_store_handler):
    name = "{}-{}".format(prefix, uuid4())
    value['internal_name'] = name
    handler(name, value)
    return name
