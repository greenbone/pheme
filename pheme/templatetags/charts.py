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
import io
import itertools
from typing import Callable, Optional, Union, Dict

from django import template
from django.utils.safestring import mark_safe
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

__severity_class_colors = {
    'High': "#d4003e",
    'Medium': "#fcb900",
    'Low': "#7db4d0",
}


register = template.Library()

__COUNTLINE_TEMPLATE = """
<rect x="{}" y="0" height="{}" width="1" style="fill: #000000;"></rect>
"""

__COUNTLINE_TEXT_TEMPLATE = """
<text class="countline label" y="22" x="{}" fill="#4C4C4D" font-size="1rem" dominant-baseline="central"
style="text-anchor: middle;" width="{}">{}
</text>
"""
__BAR_ELEMENT_TEMPLATE = """
<rect x="{}" y="17" height="10" width="{}" style="fill: {};"></rect>
"""

__BAR_TEMPLATE = """
<g class="entry" transform="translate(0, {y})">
<text class="label category" y="22" x="87.5" fill="#4C4C4D" font-size="1rem" dominant-baseline="central"
style="text-anchor: middle;" width="175">{key}
</text>
<g transform="translate(175, 0)">
{countlines}
{bar_elements}
</g>
<g transform="translate(700, 0)">
<text class="sum" y="22" x="10" fill="#4C4C4D" font-size="1rem" dominant-baseline="central"
style="text-anchor: left;" width="100">{total}</text>
</g>
</g>
"""
__BAR_CHART_TEMPLATE = """
<svg width="{width}" viewBox="0 0 1000 {height}" xmlns="http://www.w3.org/2000/svg">
{bars}
<g transform="translate(175, {bar_legend_y})">
{bar_legend}
</svg>
"""


@register.filter
def h_bar_chart(
    chart_data: Dict[str, Dict[str, int]],
    title_color=None,
    svg_width=800,
    bar_jump=44,
    countline_basis=20,
    limit=10,
) -> str:

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
        chart_data - The dict containg the values for the chart
        title_color - A colortable, defaulting to __severity_class_colors
        svg_width - The overall width of the output chart, default 800
        bar_jump - The amount of y pixels to jump from bar element to the next.
            Default is 44.
        countline_basis - if higher than 0 than there will be a vertical line
            each countline_basis. It will also add the next countline amount to
            the max_sum.
        limit - limits the data by N first elements
    """

    data = dict(itertools.islice(chart_data.items(), limit))
    if not title_color:
        title_color = __severity_class_colors
    max_width = svg_width - 175 - 100  # key and total placeholder
    # highest sum of counts
    max_sum = max([sum(list(counts.values())) for counts in data.values()])
    if max_sum == 0:
        return None
    calculated_rectangles = ""
    countline_labels = ""

    def __add_countline(i: int, calculated_rectangles="", countline_labels=""):
        x_pos = i * countline_basis / max_sum * max_width
        label = str(i * countline_basis)
        calculated_rectangles += __COUNTLINE_TEMPLATE.format(
            x_pos, bar_jump + 10
        )
        countline_labels += __COUNTLINE_TEXT_TEMPLATE.format(
            x_pos, len(label), label
        )
        return calculated_rectangles, countline_labels

    if countline_basis > 0:
        overhead = max_sum % countline_basis
        # if it's already adjusted we don't need to add anything
        if overhead == 0:
            overhead = countline_basis
        max_sum = max_sum + countline_basis - overhead

        for i in range(int(max_sum / countline_basis)):
            calculated_rectangles, countline_labels = __add_countline(
                i, calculated_rectangles, countline_labels
            )

        calculated_rectangles, countline_labels = __add_countline(
            int(max_sum / countline_basis),
            calculated_rectangles,
            countline_labels,
        )

    bars = ""
    for i, (key, counts) in enumerate(data.items()):
        element_x = 0
        elements = ""
        for category, count in counts.items():
            color = title_color.get(category)
            width = count / max_sum * max_width
            elements += __BAR_ELEMENT_TEMPLATE.format(element_x, width, color)
            element_x += width

        bars += __BAR_TEMPLATE.format(
            y=i * bar_jump,
            key=key,
            bar_elements=elements,
            countlines=calculated_rectangles,
            total=sum(counts.values()),
        )
    svg_chart = __BAR_CHART_TEMPLATE.format(
        width=svg_width,
        height=len(data.keys()) * bar_jump + 50,
        bars=bars,
        bar_legend=countline_labels,
        bar_legend_y=len(data.keys()) * bar_jump + 20,
    )
    return mark_safe(svg_chart)


def __create_default_figure():
    return Figure()


def __create_chart(
    set_plot: Callable,
    *,
    fig: Union[Figure, Callable] = __create_default_figure,
    modify_fig: Callable = None,
) -> Optional[str]:
    fig = fig() if callable(fig) else fig
    # there is a bug in 3.0.2 (debian buster)
    # that canvas is not set automatically
    canvas = FigureCanvas(fig)
    ax = fig.subplots()
    set_plot(ax)
    if modify_fig:
        modify_fig(fig)
    buf = io.BytesIO()
    fig.canvas = canvas
    fig.savefig(buf, format='svg', dpi=300)
    buf.seek(0)
    # base64_fig = base64.b64encode(buf.read())
    # uri = 'data:image/png;base64,' + urllib.parse.quote(base64_fig)
    return buf.read().decode()


@register.filter
def pie_chart(input_values, title_color=None, title=None) -> Optional[str]:
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
    """
    if not title_color:
        title_color = __severity_class_colors
    category_names = list(input_values.keys())
    category_colors = list([title_color.get(key) for key in category_names])
    values = list(input_values.values())

    total = sum(values)

    def raw_value_pct(pct):
        value = pct * total / 100.0
        return "{:d}".format(int(round(value)))

    def modify_fig(fig: Figure):
        for ax in fig.axes:
            ax.set_axis_off()

    def set_plot(ax):
        ax.set_title(title)
        wedges, _, _ = ax.pie(
            values,
            colors=category_colors,
            autopct=raw_value_pct,
            wedgeprops=dict(width=0.5),
            startangle=-40,
        )

        ax.legend(
            wedges,
            category_names,
            bbox_to_anchor=(1, 0, 0, 1),
            loc='lower right',
            fontsize='small',
        )

    if total == 0:
        return None
    return mark_safe(__create_chart(set_plot, modify_fig=modify_fig))
