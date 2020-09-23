# -*- coding: utf-8 -*-
# pheme/renderer/xml.py
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
from rest_framework.renderers import BaseRenderer
import xmltodict


class MarkDownTableRenderer(BaseRenderer):
    media_type = 'text/markdown+table'
    format = 'text'
    charset = 'utf-8'

    def __as_md(self, previous_key, data):
        def append(value):
            return isinstance(value, str) or isinstance(value, int)

        if not (isinstance(data, dict) or isinstance(data, list)):
            return []
        items = None
        result = []

        def to_new_key(key: str):
            if not previous_key:
                return key
            if not key:
                return previous_key
            return "{}.{}".format(previous_key, key)

        if isinstance(data, list):
            result.append(
                "|{}|{}| a list of items|".format(
                    previous_key,
                    "{{% for item in {} %}} ... {{% endfor %}}".format(
                        previous_key
                    ),
                )
            )
            previous_key = 'item'
            items = [("", v) for v in data]
        else:
            items = data.items()
        for key, value in items:
            new_key = to_new_key(key)
            if append(value):
                result.append(
                    "|{}|{}|{}|".format(new_key, "{{ %s }}" % new_key, value)
                )
            else:
                result = result + self.__as_md(new_key, value)
        return result

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if data is None:
            return ''
        first_line = "|key|template_example|description|\n"
        table_indicator = "| :- | :--: | -: |\n"
        rest = "\n".join(self.__as_md("", data))
        return first_line + table_indicator + rest


class XMLRenderer(BaseRenderer):
    media_type = 'application/xml'
    format = 'xml'
    charset = 'utf-8'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if data is None:
            return ''

        return xmltodict.unparse(data)
