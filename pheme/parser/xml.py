# -*- coding: utf-8 -*-
# pheme/parser/xml.py
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
"""
Provides XML parsing support.

Although there is the project djangorestframework-xml xmltodict seems to be more
reliable for our usecase.

"""
from typing import Any, Dict, Tuple
from rest_framework.parsers import BaseParser
import xmltodict


class XMLParser(BaseParser):
    """
    XML parser based on xmltodict.
    """

    media_type = "application/xml"

    def parse(self, stream, media_type=None, parser_context=None):
        return xmltodict.parse(stream, attr_prefix='', dict_constructor=dict)


def normalize_keys(_: str, key: str, value: any) -> Tuple[str, Any]:
    """
    Due to expat some keys may have values like '@' or '#' as a
    first character.

    This method is used in a postprocessor for xmltodict to remove starting non
    alpha character in keys.
    """

    def normalize_dict_keys(data: Dict) -> Dict:
        return dict(
            (
                k if k[0].isalpha() else k[1:],
                normalize_dict_keys(v) if isinstance(v, dict) else v,
            )
            for k, v in data.items()
        )

    normalized_value = (
        normalize_dict_keys(value) if isinstance(value, dict) else value
    )
    if key[0].isalpha():
        return (key, normalized_value)
    return (
        key[1:],
        normalized_value,
    )
