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
from typing import Dict, List, Optional, Callable
import logging
import io
import urllib
import base64

import pandas as pd
from pandas import DataFrame
from pandas.core.groupby.generic import DataFrameGroupBy
from pandas.core.series import Series
import numpy as np

from matplotlib.figure import Figure


from pheme.transformation.scanreport.model import (
    CVSSDistributionCount,
    HostCount,
    HostResults,
    NVTCount,
    PortCount,
    Report,
    Results,
    Scan,
    Summary,
    SummaryReport,
    SummaryResults,
    CountGraph,
    VulnerabilityOverview,
)


logger = logging.getLogger(__name__)


def __create_chart(set_plot: Callable, fig: Figure = Figure()) -> Optional[str]:
    try:
        # https://matplotlib.org/faq/howto_faq.html#how-to-use-matplotlib-in-a-web-application-server
        ax = fig.subplots()
        set_plot(ax)
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        base64_fig = base64.b64encode(buf.read())
        uri = 'data:image/png;base64,' + urllib.parse.quote(base64_fig)
        return uri
    # pylint: disable=W0703
    except Exception as e:
        logger.warning("returning None due to exception: %e", e)
        return None


def __create_bar_h_chart(series: Series) -> Optional[str]:
    def set_plot(ax):
        series.plot.barh(
            ax=ax,
            tick_label='string',
        )

    def create_figure():
        # cm to inch
        fig = Figure(figsize=(6 * 2.54, 2 * 2.54))
        fig.subplots_adjust(left=0.4)
        return fig

    if len(series) < 1:
        return None
    return __create_chart(set_plot, create_figure())


def __create_pie_chart(series: Series, colors=None) -> Optional[str]:
    def set_plot(ax):
        series.plot.pie(ax=ax, colors=colors)

    if len(series) < 1:
        return None
    return __create_chart(set_plot)


def __create_nvt_top_ten(
    threat_level: str, group_by_threat: DataFrameGroupBy
) -> CountGraph:
    try:
        threat = group_by_threat.get_group(threat_level)
        threat_nvts = threat[['nvt.oid', 'nvt.name']]
        counted = threat_nvts.value_counts()
        top_ten = counted.head(10)
        return CountGraph(
            name=threat_level,
            chart=__create_bar_h_chart(top_ten),
            counts=[
                NVTCount(oid=k[0], amount=v, name=k[1])
                for k, v in top_ten.to_dict().items()
            ],
        )
    except KeyError:
        logger.warning('Threat: %s not found', threat_level)
        return None


def __create_host_top_ten(result_series_df: DataFrame) -> CountGraph:
    threat = result_series_df.get(['host.text', 'host.hostname'])
    if threat is None:
        threat = result_series_df.get(['host.text'])
    if threat is None:
        return None

    counted = threat.value_counts().head(10)
    return CountGraph(
        name="host_top_ten",
        chart=__create_bar_h_chart(counted),
        counts=[
            HostCount(ip=k[0], amount=v, name=k[1] if len(k) > 1 else None)
            for k, v in counted.to_dict().items()
        ],
    )


def __create_port_top_ten(result_series_df: DataFrame) -> CountGraph:
    threat = result_series_df.get(['port'])
    if threat is None:
        return None
    counted = threat.value_counts().head(10)
    return CountGraph(
        name="port_top_ten",
        chart=__create_bar_h_chart(counted),
        counts=[
            PortCount(port=k, amount=v) for k, v in counted.to_dict().items()
        ],
    )


def __create_cvss_distribution_port_top_ten(
    result_series_df: DataFrame,
) -> CountGraph:
    threat = result_series_df.get(['port', 'nvt.cvss_base'])
    if threat is None:
        return None
    counted = threat.value_counts().head(10)
    return CountGraph(
        name="cvss_distribution_ports_top_ten",
        chart=__create_bar_h_chart(counted),
        counts=[
            CVSSDistributionCount(identifier=k[0], amount=v, cvss=k[1])
            for k, v in counted.to_dict().items()
        ],
    )


def __create_cvss_distribution_host_top_ten(
    result_series_df: DataFrame,
) -> CountGraph:
    threat = result_series_df.get(
        ['host.text', 'host.hostname', 'nvt.cvss_base']
    )
    if threat is None:
        return None
    counted = threat.value_counts().head(10)
    return CountGraph(
        name="cvss_distribution_host_top_ten",
        chart=__create_bar_h_chart(counted),
        counts=[
            CVSSDistributionCount(identifier=k[0], amount=v, cvss=k[1])
            for k, v in counted.to_dict().items()
        ],
    )


def __create_cvss_distribution_nvt_top_ten(
    result_series_df: DataFrame,
) -> CountGraph:
    threat = result_series_df.get(['nvt.oid', 'nvt.cvss_base'])
    if threat is None:
        return None
    counted = threat.value_counts().head(10)
    return CountGraph(
        name="cvss_distribution_nvt_top_ten",
        chart=__create_bar_h_chart(counted),
        counts=[
            CVSSDistributionCount(identifier=k[0], amount=v, cvss=k[1])
            for k, v in counted.to_dict().items()
        ],
    )


def __simple_data_frame_to_values(df: DataFrame) -> List:
    if df is None:
        return []
    return [v[0] for v in df.to_dict().values()]


def __create_scan(
    report: DataFrame,
) -> Scan:
    scan = report.get(
        [
            'task.name',
            'scan_start',
            'scan_end',
            'hosts.count',
            'task.comment',
        ]
    )
    if scan is None:
        return None
    return Scan(*__simple_data_frame_to_values(scan))


def __create_summary_report(report: DataFrame) -> SummaryReport:
    filters = report.get(['filters.term', 'filters.filter', 'timezone'])
    if filters is None:
        return None
    return SummaryReport(*__simple_data_frame_to_values(filters))


def __create_summary_results(
    report: DataFrame,
) -> SummaryResults:
    counts = report.get(['result_count.full', 'result_count.filtered'])
    if counts is None:
        logger.warning('result_count is missing, defaulting to None')
        counts = pd.DataFrame({'full': '0', 'filtered': '0'}, index=[0])
    data = __simple_data_frame_to_values(counts)
    if len(data) != 2:
        return None
    ot = report.get('original_threat')
    if ot is None:
        logger.warning('No original_threat found')
        data += [None]
    else:
        threat_distribution = ot.value_counts()

        colors = {'High': 'tab:red', 'Medium': 'tab:orange', 'Low': 'tab:blue'}
        data += [
            __create_pie_chart(
                threat_distribution,
                colors=[colors.get(v) for v in threat_distribution.keys()],
            )
        ]  # append graph
    return SummaryResults(*data)


def __create_results(report: DataFrame) -> List[Dict]:
    try:
        grouped_host = report.groupby('host.text')
        wanted_columns = [
            'nvt.oid',
            'nvt.type',
            'nvt.name',
            'nvt.family',
            'nvt.cvss_base',
            'nvt.tags',
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

        for host_text in grouped_host.groups.keys():
            host_df = grouped_host.get_group(host_text)
            columns = [x for x in host_df.columns if x in wanted_columns]
            if len(wanted_columns) != len(columns):
                logger.warning(
                    "report for %s -> missing keys: %s",
                    host_text,
                    np.setdiff1d(wanted_columns, columns),
                )
            flat_results = host_df[columns]
            result = []
            for key, series in flat_results.items():
                for i, value in enumerate(series):
                    if len(result) < i + 1:
                        result.append({})
                    if not (isinstance(value, float) and np.isnan(value)):
                        result[i][normalize_key(key)] = value
            results.append(HostResults(host_text, result))
        return results
    except KeyError as e:
        logger.warning('report does not contain host.text returning []; %s', e)
        return []


def transform(data: Dict[str, str]) -> Report:
    report = data.get("report")
    # sometimes gvmd reports have .report.report sometimes just .report
    report = report.get("report") or report

    n_df = pd.json_normalize(report)
    results_series = n_df.get('results.result')
    # pylint: disable=W0108
    result_series_df = results_series.map(lambda x: pd.json_normalize(x)).all()
    common_vulnerabilities = None
    try:
        group_by_threat = result_series_df.groupby('original_threat')

        common_vulnerabilities = [
            __create_nvt_top_ten('High', group_by_threat),
            __create_nvt_top_ten('Medium', group_by_threat),
            __create_nvt_top_ten('Low', group_by_threat),
        ]
    except KeyError as e:
        logger.warning('ignoring original_threat missing: %s', e)

    vulnerabilities_overview = VulnerabilityOverview(
        __create_host_top_ten(result_series_df),
        None,
        __create_port_top_ten(result_series_df),
        __create_cvss_distribution_port_top_ten(result_series_df),
        __create_cvss_distribution_host_top_ten(result_series_df),
        __create_cvss_distribution_nvt_top_ten(result_series_df),
    )
    summary = Summary(
        __create_scan(n_df),
        __create_summary_report(n_df),
        __create_summary_results(result_series_df),
    )
    results = __create_results(result_series_df)

    def get_single_result(key: str):
        value = n_df.get(key)
        if value is not None:
            return value.all()
        return None

    logger.info("data transformation")
    return Report(
        report.get('id'),
        summary,
        common_vulnerabilities,
        vulnerabilities_overview,
        Results(
            get_single_result('results.max'),
            get_single_result('results.start'),
            results,
        ),
    )
