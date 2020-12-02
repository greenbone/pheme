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
from typing import Callable, Optional, Union

from django.utils.safestring import mark_safe
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from pheme.templatetags.charts import register, _severity_class_colors


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
        title_color = _severity_class_colors
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
