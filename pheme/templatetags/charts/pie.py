# -*- coding: utf-8 -*-
# pheme/templatetags/charts.py
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
import math
from typing import Dict
from django.utils.safestring import SafeText
from pheme.templatetags.charts import (
    register,
    _severity_class_colors,
    _build_legend,
)

__PIE_CHART_TEMPLATE = """
<svg width="{size}" viewBox="0 0 {size} {height}" xmlns="http://www.w3.org/2000/svg">
{donut}
{legend}
</svg>
"""

__SLICE_TEMPLATE = """
<g>
<circle cx="{cx}" cy="{cy}" r="{radius}" stroke="{color}" stroke-width="{stroke_width}" stroke-dasharray="{d_array}" stroke-dashoffset="{s_offset}" transform="rotate({r_start}, {cx}, {cy})" fill="transparent"></circle>
<text x="{t_x}" y="{t_y}" text-anchor="middle">{label}</text>
</g>
"""


@register.filter
def pie_chart(
    input_values: Dict,
    title_color: Dict = None,
    chart_size: int = 320,
    border_size: int = 0,
    slice_width: int = 60,
) -> SafeText:
    """
    creates a pie chart svg.

    The values parameter needs to be a dict with a categoryname: numeric_value.
    E.g.:
    {
        "High": 5,
        "Medium": 3,
        "Low": 2
    }

    The keys need to match the title_color keys. As a default the
    severity_classes: High , Medium, Low are getting used.

    Parameters:
        input_values: dict containing the data as label: numeric_value
        title_color: dict containing the data as label: color
        chart_size: int the height and width of the
        border_size: int size of the border of slice
        slice_width: int the width of slice

    Returns:
    A SafeString with SVG
    """
    if not title_color:
        title_color = _severity_class_colors
    total = sum(input_values.values())
    if total == 0:
        return SafeText("")
    # pylint: disable=C0103
    # we start at 12' o clock
    angle_offset = -90

    cx = chart_size / 2  # shift x
    cy = chart_size / 2  # shift y
    # need to cut out size of the slice_width, otherwise edges will be cut off
    radius = (chart_size - slice_width) / 2
    circumference = 2 * math.pi * radius
    dash_array = circumference - border_size

    donut = ""
    for (category, amount) in input_values.items():
        percent = amount / total
        color = title_color.get(category)
        dash_offset = circumference - percent * circumference
        degrees = angle_offset
        t_angle = (percent * 360) / 2 + angle_offset
        t_radians = t_angle * (math.pi / 180)
        t_x = radius * math.cos(t_radians) + cx
        t_y = radius * math.sin(t_radians) + cy

        angle_offset += percent * 360
        donut += __SLICE_TEMPLATE.format(
            cx=cx,
            cy=cy,
            radius=radius,
            color=color,
            stroke_width=slice_width,
            d_array=dash_array,
            s_offset=dash_offset,
            r_start=degrees,
            t_x=t_x,
            t_y=t_y,
            label=f"{round(percent * 100)}%",
        ).strip()

    legend = _build_legend(chart_size + 10, chart_size, 16, title_color)
    return SafeText(
        __PIE_CHART_TEMPLATE.format(
            size=chart_size, height=chart_size + 26, donut=donut, legend=legend
        ).strip()
    )
