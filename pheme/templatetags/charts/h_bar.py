# -*- coding: utf-8 -*-
# pheme/templatetags/bar_chart.py
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

import itertools
from typing import Dict
from django.utils.safestring import SafeText
from pheme.templatetags.charts import (
    register,
    _severity_class_colors,
    build_legend,
    calculate_legend_start_height,
)


__ORIENTATION_LINE_TEMPLATE = """
<rect x="{x}" y="0" height="{height}" width="1" style="fill: #000000;"></rect>
"""

__ORIENTATION_LINE_TEXT_TEMPLATE = """
<text class="orientation label" y="22" x="{x}" fill="#4C4C4D" dominant-baseline="central"
style="font-size:{font_size};font-family:{font_family};text-anchor: middle;" width="{width}">{label}
</text>
"""
__BAR_ELEMENT_TEMPLATE = """
<rect x="{x}" y="17" height="10" width="{width}" style="fill: {color};"></rect>
"""

__BAR_TEMPLATE = """
<g class="entry" transform="translate(0, {y})">
<text class="label category" y="22" x="87.5" fill="#4C4C4D" dominant-baseline="central"
style="font-size:{font_size};font-family:{font_family};text-anchor: right;" width="{max_hostname_len}">{key}
</text>
<g transform="translate({max_hostname_len}, 0)">
{orientation_lines}
{bar_elements}
</g>
<g transform="translate({begin_total}, 0)">
<text class="sum" y="22" x="10" fill="#4C4C4D" dominant-baseline="central"
style="font-size:{font_size};font-family:{font_family};text-anchor: left;" width="100">{total}</text>
</g>
</g>
"""
__BAR_CHART_TEMPLATE = """
<svg width="{width}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
{bars}
<g transform="translate({max_hostname_len}, {bar_legend_y})">
{bar_legend}
</g>
{legend}
</svg>
"""


@register.filter
def h_bar_chart(
    chart_data: Dict[str, Dict[str, int]],
    title_color=None,
    svg_width=800,
    bar_jump=44,
    orientation_basis=20,
    limit=10,
    font_family="Droid Sans",
    font_size=10,
) -> SafeText:

    """
    Returns a stacked horizontal bar chart in svg.

    In order to function it needs a dict with label as key containing a dict
    with color key and amount.

    An example for valid input is:

    {
      "192.168.123.52": {
        "High": 3,
        "Medium": 3,
        "Low": 1
      }
    }

    parameter:
        chart_data - The dict containing the values for the chart
        title_color - A colortable, defaulting to __severity_class_colors
        svg_width - The overall width of the output chart, default 800
        bar_jump - The amount of y pixels to jump from bar element to the next.
            Default is 44.
        orientation_basis - if higher than 0 than there will be a vertical line
            each orientation_basis.
        limit - limits the data by N first elements
        font_family - the font family used within text elements
        font_size - the font size used within text elements
    """

    data = dict(itertools.islice(chart_data.items(), limit))
    if not title_color:
        title_color = _severity_class_colors
    if not data.values():
        return SafeText("")
    # multiply by 1.25 for kerning
    max_hostname_len = max(len(k) for k in data.keys()) * font_size * 1.25
    max_width = svg_width - max_hostname_len - 100  # key and total placeholder
    # highest sum of counts
    max_sum = max([sum(list(counts.values())) for counts in data.values()])
    if max_sum == 0:
        max_sum = 1
    orientation_lines = ""
    orientation_labels = ""

    def __add_orientation(i: int, orientation_lines="", orientation_labels=""):
        x_pos = i * orientation_basis / max_sum * max_width
        label = str(i * orientation_basis)
        orientation_lines += __ORIENTATION_LINE_TEMPLATE.format(
            x=x_pos,
            height=bar_jump + 10,
            font_family=font_family,
            font_size=font_size,
        )
        orientation_labels += __ORIENTATION_LINE_TEXT_TEMPLATE.format(
            x=x_pos,
            width=len(label),
            label=label,
            font_family=font_family,
            font_size=font_size,
        )
        return orientation_lines, orientation_labels

    if orientation_basis > 0:
        overhead = max_sum % orientation_basis
        # if it's already adjusted we don't need to add anything
        if overhead == 0:
            overhead = orientation_basis
        max_sum = max_sum + orientation_basis - overhead

        for i in range(int(max_sum / orientation_basis + 1)):
            orientation_lines, orientation_labels = __add_orientation(
                i, orientation_lines, orientation_labels
            )

    bars = ""
    for i, (key, counts) in enumerate(data.items()):
        element_x = 0
        elements = ""
        for category, count in counts.items():
            color = title_color.get(category)
            width = count / max_sum * max_width
            elements += __BAR_ELEMENT_TEMPLATE.format(
                x=element_x,
                width=width,
                color=color,
                font_family=font_family,
                font_size=font_size,
                max_hostname_len=max_hostname_len,
            )
            element_x += width

        bars += __BAR_TEMPLATE.format(
            y=i * bar_jump,
            key=key,
            bar_elements=elements,
            orientation_lines=orientation_lines,
            total=sum(counts.values()),
            font_family=font_family,
            font_size=font_size,
            max_hostname_len=max_hostname_len,
            begin_total=svg_width - 100,
        )
    svg_element_lengths = len(data.keys()) * bar_jump + 50
    legend_start = calculate_legend_start_height(
        svg_element_lengths, title_color, font_size
    )
    svg_chart = __BAR_CHART_TEMPLATE.format(
        width=svg_width,
        height=svg_element_lengths,
        bars=bars,
        bar_legend=orientation_labels,
        bar_legend_y=len(data.keys()) * bar_jump + 20,
        legend=build_legend(legend_start, title_color),
        font_family=font_family,
        font_size=font_size,
        max_hostname_len=max_hostname_len,
    )
    return SafeText(svg_chart)
