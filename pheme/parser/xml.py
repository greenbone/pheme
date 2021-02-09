# -*- coding: utf-8 -*-
# pheme/parser/xml.py
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
"""
Provides XML parsing support.

Although there is the project djangorestframework-xml xmltodict seems to be more
reliable for our usecase.

"""
from rest_framework.parsers import BaseParser
import xmltodict


class XMLFormParser(BaseParser):
    """
    XML parser based on xmltodict.
    """

    media_type = "multipart/form-data"

    def parse(self, stream, media_type=None, parser_context=None):
        for report in stream.FILES.values():
            if report.content_type == 'text/xml':
                return xmltodict.parse(
                    report.read(),
                    attr_prefix='',
                    cdata_key='text',
                    dict_constructor=dict,
                )
        return None


class XMLParser(BaseParser):
    """
    XML parser based on xmltodict.
    """

    media_type = "application/xml"

    def parse(self, stream, media_type=None, parser_context=None):
        return xmltodict.parse(
            stream, attr_prefix='', cdata_key='text', dict_constructor=dict
        )
