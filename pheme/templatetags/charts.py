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
from typing import Callable, Union, Optional
import numpy as np
from django import template

from django.utils.safestring import mark_safe

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.colors import CSS4_COLORS, hex2color
from matplotlib.figure import Figure

__severity_class_colors = {
    'High': CSS4_COLORS['red'],
    'Medium': CSS4_COLORS['orange'],
    'Low': CSS4_COLORS['blue'],
}


register = template.Library()


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
def h_bar_chart(host_count, title_color=None) -> str:
    if not title_color:
        title_color = __severity_class_colors

    def set_plot(ax):
        # pylint: disable=C0103

        data = np.array(
            [list(values.values()) for values in host_count.values()]
        )
        category_names = set(
            [
                category
                for values in host_count.values()
                for category in values.keys()
            ]
        )
        category_colors = list([title_color.get(key) for key in category_names])

        h_sum = np.sum(data, axis=1)
        idx = (-h_sum).argsort()
        keys = np.array(list(host_count.keys()))
        sorted_data = np.take(data, idx[:10], axis=0)
        labels = np.take(keys, idx[:10], axis=0)
        ax.invert_yaxis()
        ax.xaxis.set_visible(False)
        ax.set_xlim(0, np.sum(sorted_data, axis=1).max())

        data_cum = sorted_data.cumsum(axis=1)
        for i, (colname, color) in enumerate(
            zip(category_names, category_colors)
        ):
            widths = sorted_data[:, i]
            starts = data_cum[:, i] - widths
            ax.barh(
                labels,
                widths,
                left=starts,
                height=0.5,
                label=colname,
                color=color,
            )
            xcenters = starts + widths / 2
            r, g, b = hex2color(color)
            text_color = 'white' if r * g * b < 0.5 else 'darkgrey'
            for y, (x, c) in enumerate(zip(xcenters, widths)):
                ax.text(
                    x,
                    y,
                    str(int(c)),
                    ha='center',
                    va='center',
                    color=text_color,
                )
        ax.legend(
            ncol=len(category_names),
            bbox_to_anchor=(0, 1),
            loc='lower left',
            fontsize='small',
        )

    def create_fig():
        return Figure(figsize=(9.2, 5))

    if len(host_count.keys()) == 0:
        return None
    return mark_safe(__create_chart(set_plot, fig=create_fig))


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
