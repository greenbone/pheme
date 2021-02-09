# -*- coding: utf-8 -*-
# pheme/templatetags/dynamic_template.py
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
Adds the possibility to dynamially render template snippets load via parameter
and render them into another template without having the need to declare them
as a dependency upfront.
"""

from django.utils.safestring import mark_safe, SafeString
from django import template
from pheme.parameter import load_params


register = template.Library()


@register.filter
def dynamic_template(data, key: str) -> SafeString:
    """
    Loads the template via key and renders the template with the given
    data.

    Parameter:
        data - used to create the context for the renderer
        key: str - identifier of the template to render

    Returns:
        The rendered template or an empty string when the key is not found
    """
    tmpl = load_params().get(key)
    if not tmpl:
        return mark_safe("")
    return mark_safe(template.Template(tmpl).render(template.Context(data)))
