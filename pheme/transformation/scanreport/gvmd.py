# -*- coding: utf-8 -*-
# pheme/transformation/scanreport/gvmd.py
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
"""
pheme.transformation.scanreport.gvmd

contrains the function

- transform

it is a specialized module for gvmd scanreports.
"""
import base64
import io
import logging
import time
import urllib

from typing import Callable, Dict, List, Optional, Union

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.colors import CSS4_COLORS, hex2color
from matplotlib.figure import Figure

import numpy as np

from pheme.transformation.scanreport.model import (
    CountGraph,
    # Equipment,
    Overview,
    Report,
)

logger = logging.getLogger(__name__)

__threats = ["High", "Medium", "Low"]
__threat_index_lookup = {v: i for i, v in enumerate(__threats)}


def measure_time(func):
    def measure(*args, **kwargs):
        startt = time.process_time()
        result = func(*args, **kwargs)
        logger.info("%s took %s", func.__name__, time.process_time() - startt)
        return result

    return measure


__severity_class_colors = {
    'High': CSS4_COLORS['red'],
    'Medium': CSS4_COLORS['orange'],
    'Low': CSS4_COLORS['blue'],
}


def __create_default_figure():
    return Figure()


@measure_time
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
    fig.savefig(buf, format='png', dpi=300)
    buf.seek(0)
    base64_fig = base64.b64encode(buf.read())
    uri = 'data:image/png;base64,' + urllib.parse.quote(base64_fig)
    return uri


@measure_time
def __create_host_distribution_chart(host_count: Dict[str, List[int]]) -> str:
    def set_plot(ax):
        # pylint: disable=C0103
        data = np.array(list(host_count.values()))
        h_sum = np.sum(data, axis=1)
        idx = (-h_sum).argsort()
        keys = np.array(list(host_count.keys()))
        sorted_data = np.take(data, idx[:10], axis=0)
        labels = np.take(keys, idx[:10], axis=0)
        ax.invert_yaxis()
        ax.xaxis.set_visible(False)
        ax.set_xlim(0, np.sum(sorted_data, axis=1).max())
        category_names = list(__severity_class_colors.keys())
        category_colors = list(__severity_class_colors.values())

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
    return __create_chart(set_plot, fig=create_fig)


@measure_time
def __create_pie_chart(values, *, title=None) -> Optional[str]:
    total = sum(values)

    def raw_value_pct(pct):
        value = pct * total / 100.0
        return "{:d}".format(int(round(value)))

    def modify_fig(fig: Figure):
        for ax in fig.axes:
            ax.set_axis_off()

    def set_plot(ax):
        category_names = list(__severity_class_colors.keys())
        category_colors = list(__severity_class_colors.values())
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
    return __create_chart(set_plot, modify_fig=modify_fig)


def __tansform_tags(item) -> List[Dict]:
    if isinstance(item, str):
        splitted = [i.split('=') for i in item.split('|')]
        return {i[0]: i[1] for i in splitted if len(i) == 2}
    return None


def __return_highest_threat(threats: List[int]) -> str:
    """
    retuns the highest threat within a list of threats based on __threats
    """
    for i, value in enumerate(threats):
        if value > 0:
            return __threats[i]
    return 'NA'


def __group_refs(refs: List[Dict]) -> Dict:
    refs_ref = {}
    for ref in refs.get('ref', []):
        typus = ref.get('type', 'unknown')
        refs_ref[typus] = refs.get(typus, []) + [ref.get('id')]
    return refs_ref


def __get_hostname_from_result(result) -> str:
    if isinstance(result, str):
        return result
    if isinstance(result, dict):
        host = result.get('host', {})
        if isinstance(host, dict):
            return host.get('text', 'unknown')
        return host
    return 'unknown'


def __host_nvt_overview(nvt_count: List[int]) -> Dict:
    """
    returns nvt statistics mostly used in the per host overview
    """
    result = {__threats[i].lower(): value for i, value in enumerate(nvt_count)}
    result['total'] = sum(nvt_count)
    result['highest'] = __return_highest_threat(nvt_count)
    return result


@measure_time
def __create_results_per_host(report: Dict) -> List[Dict]:
    results = report.get('results', {}).get('result', [])
    by_host = {}
    host_count = {}
    nvt_count = [0, 0, 0]

    def transform_key(prefix: str, vic: Dict) -> Dict:
        return {
            "{}_{}".format(prefix, key): value for key, value in vic.items()
        }

    def per_result(result):
        hostname = __get_hostname_from_result(result)
        host_dict = by_host.get(hostname, {})
        threat = result.get('threat', 'unknown')
        port = result.get('port')
        nvt = transform_key("nvt", result.get('nvt', {}))
        nvt['nvt_tags_interpreted'] = __tansform_tags(nvt.get('nvt_tags', ''))
        nvt['nvt_refs_ref'] = __group_refs(nvt.get('nvt_refs', {}))
        qod = transform_key('qod', result.get('qod', {}))
        new_host_result = {
            "port": port,
            "threat": threat,
            "severity": result.get('severity'),
            "description": result.get('description'),
            **nvt,
            **qod,
        }
        host_results = host_dict.get('results', [])
        host_results.append(new_host_result)
        equipment = host_dict.get('equipment', {})
        equipment['ports'] = list(
            dict.fromkeys(equipment.get('ports', []) + [port])
        )
        # filter for best_os_cpe
        equipment['os'] = "unknown"

        # needs hostname, high, medium, low
        host_threats = host_count.get(hostname, [0, 0, 0])
        threat_index = __threat_index_lookup.get(threat, 2)
        host_threats[threat_index] += 1
        host_count[hostname] = host_threats

        # needs high, medium, low
        nvt_count[threat_index] += 1

        by_host[hostname] = {
            "host": hostname,
            "threats": __host_nvt_overview(host_threats),
            "equipment": equipment,
            "results": host_results,
        }

    # lists with just one element can be parsed as dict by xmltodict
    if isinstance(results, dict):
        per_result(results)
    else:
        for result in results:
            per_result(result)

    return list(by_host.values()), host_count, nvt_count


@measure_time
def transform(data: Dict[str, str]) -> Report:
    """
    transform will use the given dict of a scanreport from gvmd
    to create an easy to use data representation for visual reports.
    """
    if not data:
        raise ValueError("Need data to process")
    report = data.get("report")
    # sometimes gvmd reports have .report.report sometimes just .report
    report = report.get("report", report)

    task = report.get('task') or {}
    gmp = report.get('gmp') or {}
    logger.info("data transformation")
    results, host_counts, nvts_counts = __create_results_per_host(report)

    nvt = CountGraph(
        name="nvt_count", chart=__create_pie_chart(nvts_counts), counts=None
    )
    host_chart = CountGraph(
        name="host_top_ten",
        chart=__create_host_distribution_chart(host_counts),
        counts=None,
    )
    return Report(
        report.get('id'),
        task.get('name'),
        task.get('comment'),
        gmp.get('version'),
        report.get('scan_start'),
        Overview(
            hosts=host_chart,
            nvts=nvt,
            vulnerable_equipment=None,
        ),
        results,
    )
