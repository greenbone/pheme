# -*- coding: utf-8 -*-
# pheme/templatetags/dynamic_template.py
# Copyright (C) 2020-2021 Greenbone AG
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
Adds the possibility to print iso_8601 strings as %a, %b %d, %Y %I %p %Z', e.g.:
    2001-07-22T09:15:37Z -> Sun, Jul 22, 2001 09 AM UTC
"""
from datetime import datetime
from django.utils.safestring import SafeText, SafeString
from django import template


register = template.Library()


@register.filter
def format_time(iso_8601: str) -> SafeString:
    """
    Transforms iso string to %a, %b %d, %Y %I %p %Z.

    Parameter:
        iso_8601 - the string to format

    Returns:
        An the input parameter on failure or an transformed SafeString with
        human readable time format.
    """

    try:
        time = datetime.strptime(iso_8601, "%Y-%m-%dT%H:%M:%S%z")
        return SafeText(datetime.strftime(time, "%a, %b %d, %Y %I %p %Z"))
    except (ValueError, TypeError) as _:
        return SafeText(iso_8601)
