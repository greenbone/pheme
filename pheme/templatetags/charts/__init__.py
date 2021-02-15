# -*- coding: utf-8 -*-
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

from typing import Dict
from django import template

_severity_class_colors = {
    "High": "#d4003e",
    "Medium": "#fcb900",
    "Low": "#7db4d0",
}

register = template.Library()

__LEGEND_TEMPLATE = """
<g transform="translate({x}, {y})">
{legend}
</g>
"""
__LEGEND_ELEMENT = """
<rect x="{x}" y="{y}" height="{font_size}" width="{font_size}" style="fill: {color};"></rect>
<text style="font-size:{font_size};font-family:{font_family}" x="{text_x}" y="{text_y}" dominant-baseline="central">{label}</text>
"""


def calculate_legend_start_height(
    height: int, label_color: Dict, font_size: int
) -> int:
    return int(height / 2 - (len(label_color) * font_size) / 2)


def build_legend(
    start_height: int,
    label_color: Dict,
    font_family: str = "Droid Sans",
    font_size: int = 10,
) -> str:
    """
    Generates a legend at     start_height y position and at
    width / 2 - last_x of element / 2 x position.

    By iterating through the the label_color dict and using the key as a label
    and the value as a fill color for the rectangle.

    Parameters:
        start_height: x position of legend
        label_color: key is used as a label and the value as a fill color for an
            rectangle (font_size * font_size).
        font_family - the font family used within text elements
        font_size - the font size used within text elements
    Returns:
        A complete g element with legends as a string.

    """
    legend_elements = ""
    x_pos = 0
    y_pos = 0
    # offset of two to the rect element
    text_x_pos = font_size + 2
    for label, color in label_color.items():
        legend_elements += __LEGEND_ELEMENT.format(
            x=x_pos,
            y=y_pos,
            font_size=font_size,
            font_family=font_family,
            color=color,
            label=label,
            text_x=text_x_pos,
            # text position needs to aligned in the middle of the rect
            text_y=y_pos + font_size / 2,
        )
        y_pos += font_size + font_size / 2

    return __LEGEND_TEMPLATE.format(x=0, y=start_height, legend=legend_elements)
