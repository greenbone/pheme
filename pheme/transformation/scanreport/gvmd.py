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
import base64
import io
import logging
import urllib
from typing import Any, Union, Callable, Dict, List, Optional

import numpy as np
import squarify
import pandas as pd
from matplotlib.figure import Figure
from pandas import DataFrame
from pandas.core.series import Series

from pheme.transformation.scanreport.model import (
    CountGraph,
    Equipment,
    HostCount,
    HostResults,
    Overview,
    Report,
)

logger = logging.getLogger(__name__)

__severity_class_colors = {
    'High': 'tab:red',
    'Medium': 'tab:orange',
    'Low': 'tab:blue',
}


def __create_default_figure():
    return Figure()


def __create_chart(
    set_plot: Callable,
    *,
    fig: Union[Figure, Callable] = __create_default_figure,
    modify_fig: Callable = None,
) -> Optional[str]:
    try:
        fig = fig() if callable(fig) else fig
        # https://matplotlib.org/faq/howto_faq.html#how-to-use-matplotlib-in-a-web-application-server
        ax = fig.subplots()
        set_plot(ax)
        if modify_fig:
            modify_fig(fig)
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=300)
        buf.seek(0)
        base64_fig = base64.b64encode(buf.read())
        uri = 'data:image/png;base64,' + urllib.parse.quote(base64_fig)
        del fig
        return uri
    # pylint: disable=W0703
    except Exception as e:
        logger.warning("returning None due to exception: %e", e)
        return None


def __create_bar_h_chart(
    series: Series, *, stacked: bool = False, colors=None
) -> Optional[str]:
    # https://matplotlib.org/3.1.1/gallery/statistics/barchart_demo.html#sphx-glr-gallery-statistics-barchart-demo-py
    # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.plot.barh.html
    def set_plot(ax):
        series.plot.barh(
            ax=ax,
            stacked=stacked,
            color=colors,
            width=0.02,
        )

    if len(series) < 1:
        return None
    return __create_chart(set_plot)


def __create_tree_chart(values, labels, *, colors=None) -> Optional[str]:
    def set_plot(ax):
        squarify.plot(sizes=values, label=labels, color=colors, pad=True, ax=ax)

    def modify_fig(fig: Figure):
        for ax in fig.axes:
            ax.set_axis_off()

    def create_fig():
        fig = Figure(figsize=(33, 12))
        return fig

    return __create_chart(set_plot, fig=create_fig, modify_fig=modify_fig)


def __create_pie_chart(
    series: Series, *, title=None, colors=None
) -> Optional[str]:
    total = series.sum()

    def raw_value_pct(pct):
        return "{:d}".format(int(round(pct * total / 100.0)))

    def modify_fig(fig: Figure):
        for ax in fig.axes:
            ax.set_axis_off()

    def set_plot(ax):
        ax.set_title(title)
        series.plot.pie(
            legend=True, ax=ax, colors=colors, autopct=raw_value_pct
        )

    if len(series) < 1:
        return None
    return __create_chart(set_plot, modify_fig=modify_fig)


def __severity_class_to_color(severity_classes: List[str]):
    return [__severity_class_colors.get(v, 'white') for v in severity_classes]


def __create_host_top_ten(result_series_df: DataFrame) -> CountGraph:
    threat = result_series_df.get(['host.text', 'threat'])
    if threat is None:
        return None

    counted = threat.value_counts().head(10)
    return CountGraph(
        name="host_top_ten",
        chart=__create_bar_h_chart(
            counted.unstack('threat'),
            stacked=True,
            colors=__severity_class_colors,
        ),
        counts=[
            HostCount(ip=k[0], amount=v, name=None)
            for k, v in counted.to_dict().items()
        ],
    )


def __create_nvt(result_series_df: DataFrame) -> CountGraph:
    threat = result_series_df.get('threat')
    if threat is None:
        return None

    counted = threat.value_counts()
    return CountGraph(
        name="nvt_overview",
        chart=__create_pie_chart(
            counted,
            colors=__severity_class_to_color(counted.keys()),
            title="Total NVT",
        ),
        counts=None,
    )


def __create_results(report: DataFrame, os_lookup: DataFrame) -> List[Dict]:
    try:
        grouped_host = report.groupby('host.text')
        wanted_columns = [
            'nvt.oid',
            'nvt.type',
            'nvt.name',
            'nvt.family',
            'nvt.cvss_base',
            'nvt.tags_interpreted',
            'nvt.refs.ref',
            'nvt.solution.type',
            'nvt.solution.text',
            'port',
            'threat',
            'severity',
            'qod.value',
            'qod.type',
            'description',
        ]
        results = []

        def normalize_key(key: str) -> str:
            return key.replace('.', '_')

        def normalize_ref_value(ref_val) -> List[str]:
            return [v for v, _ in ref_val]

        for host_text, host_df in grouped_host:
            columns = [x for x in host_df.columns if x in wanted_columns]
            if len(wanted_columns) != len(columns):
                logger.warning(
                    "report for %s -> missing keys: %s",
                    host_text,
                    np.setdiff1d(wanted_columns, columns),
                )
            flat_results = host_df[columns]
            result = []
            os = None
            if os_lookup is not None:
                may_os = os_lookup.loc[
                    os_lookup['ip'] == host_text, 'detail'
                ].values
                os = may_os[0].value.all() if len(may_os) > 0 else None
            for key, series in flat_results.items():
                for i, value in enumerate(series):
                    if not (isinstance(value, float) and np.isnan(value)):
                        if key == 'nvt.refs.ref':
                            grouped_refs = pd.json_normalize(value).groupby(
                                'type'
                            )
                            value = {
                                key: normalize_ref_value(val.values)
                                for key, val in grouped_refs
                            }
                        if len(result) < i + 1:
                            result.append({})
                        result[i][normalize_key(key)] = value
            results.append(
                HostResults(
                    host=host_text,
                    equipment=Equipment(os=os, ports=[]),
                    results=result,
                )
            )
        return results
    except KeyError as e:
        logger.warning('report does not contain host.text returning []; %s', e)
        return []


def __create_vulnerable_equipment(report: DataFrame) -> CountGraph:
    df = report.get(['host.text', 'threat'])
    if df is None:
        return None

    def return_highest(item):
        if 'High' in item:
            return __severity_class_colors.get('High')
        if 'Medium' in item:
            return __severity_class_colors.get('Medium')
        if 'Medium' in item:
            return __severity_class_colors.get('Low')
        return "white"

    values = []
    labels = []
    colors = []
    max_count_nvt = df.groupby('host.text').count().count().item()

    for host, df in df.groupby('host.text'):
        count_nvt = len(df)
        until = round(len(host) * count_nvt / max_count_nvt)
        labels.append(host[0:until] if until else "")
        values.append(count_nvt)
        colors.append(return_highest(df.groupby('threat').groups.keys()))

    return CountGraph(
        name="vulnerable_equipment",
        counts=None,
        chart=__create_tree_chart(values, labels, colors=colors),
    )


def __tansform_tags(item) -> List[Dict]:
    if isinstance(item, str):
        splitted = [i.split('=') for i in item.split('|')]
        return {i[0]: i[1] for i in splitted if len(i) == 2}
    return None


def __filter_os_based_on_name(item: Union[Any, List]) -> Union[Any, Series]:
    """
    filters operating system in host.details for best_os_cpe
    """
    if isinstance(item, list):
        return pd.json_normalize(item).query('name == "best_os_cpe"')
    return item


def __json_normalize(item) -> DataFrame:
    return pd.json_normalize(item)


def transform(data: Dict[str, str]) -> Report:
    report = data.get("report")
    # sometimes gvmd reports have .report.report sometimes just .report
    report = report.get("report", report)
    n_df = pd.json_normalize(report)
    result_series_df = n_df.get('results.result').map(__json_normalize).all()
    tags = result_series_df.get('nvt.tags')
    if tags is not None:
        result_series_df['nvt.tags_interpreted'] = tags.map(__tansform_tags)
    host_df = n_df.get('host')
    if host_df is not None:
        host_df = host_df.map(__json_normalize).all()
        host_df = host_df.get(['ip', 'detail'])
        if host_df is not None:
            host_df = host_df.applymap(__filter_os_based_on_name)
    results = __create_results(result_series_df, host_df)

    logger.info("data transformation")
    return Report(
        report.get('id'),
        None,
        Overview(
            hosts=__create_host_top_ten(result_series_df),
            nvts=__create_nvt(result_series_df),
            vulnerable_equipment=__create_vulnerable_equipment(
                result_series_df
            ),
        ),
        results,
    )
