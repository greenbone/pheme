# -*- coding: utf-8 -*-
# pheme/transformation/storage.py
# Copyright (C) 2020-2021 Greenbone Networks GmbH
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
from uuid import uuid4
from typing import Dict

from django.core.cache import cache


def __default_store_handler(name: str, value: Dict):
    cache.set(name, value)


def __default_load_handler(name: str) -> Dict:
    return cache.get(name)


def __default_id_generator(prefix: str) -> str:
    return "{}-{}".format(prefix, uuid4())


def load(name: str, *, handler=__default_load_handler) -> Dict:
    return handler(name)


def store(
    prefix: str,
    value: Dict,
    *,
    handler=__default_store_handler,
    id_generator=__default_id_generator
):
    name = id_generator(prefix)
    if isinstance(value, dict):
        value['internal_name'] = name
    handler(name, value)
    return name
