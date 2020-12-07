# -*- coding: utf-8 -*-
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

from typing import Dict
from django import template

_severity_class_colors = {
    'High': "#d4003e",
    'Medium': "#fcb900",
    'Low': "#7db4d0",
}

register = template.Library()

__LEGEND_TEMPLATE = """
<g transform="translate({x}, {y})">
{legend}
</g>
"""
__LEGEND_ELEMENT = """
<rect x="{x}" y="0" height="{font_size}" width="{font_size}" style="fill: {color};"></rect>
<text x="{text_x}" y="{half_font_size}" dominant-baseline="central">{label}</text>
"""


def _build_legend(
    start_height: int, width: int, font_size: int, label_color: Dict
) -> str:
    """
    Generates a legend at     start_height y position and at
    width / 2 - last_x of element / 2 x position.

    By iterating through the the label_color dict and using the key as a label
    and the value as a fill color for the rectangle.

    Parameters:
        start_height: x position of legend
        width: width: of the svg, used as an indicator for the middle
        font_size: size of used font, used to calculate x position of an element
        label_color: key is used as a label and the value as a fill color for an
            rectangle (font_size * font_size).
    Returns:
        A complete g element with legends as a string.

    """
    legend_elements = ""
    x_pos = 0
    for label, color in label_color.items():
        text_x = x_pos + font_size + 2
        legend_elements += __LEGEND_ELEMENT.format(
            x=x_pos,
            font_size=font_size,
            color=color,
            half_font_size=font_size / 2,
            label=label,
            text_x=text_x,
        )
        x_pos = text_x + len(label) * font_size

    return __LEGEND_TEMPLATE.format(
        x=width / 2 - x_pos / 2, y=start_height, legend=legend_elements
    )
