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
from typing import Dict, List
import logging

import pandas as pd
from pandas import DataFrame
from pandas.core.groupby.generic import DataFrameGroupBy
import numpy as np

from pheme.transformation.scanreport.model import (
    CommonVulnerabilities,
    CVSSDistributionCount,
    HostCount,
    HostResults,
    NVTCount,
    PortCount,
    QOD,
    Ref,
    Report,
    Result,
    Scan,
    Solution,
    Summary,
    SummaryReport,
    SummaryResults,
    TopTen,
    VulnerabilityOverview,
)


def group_by_host(first: Dict[str, HostResults], second: Dict[str, str]):
    host = second.pop('host')
    host = host if isinstance(host, str) else host.pop("text")
    hr: HostResults = first.get(host)
    nvt = second.pop('nvt')
    solution = (
        Solution(nvt['solution']['type'], nvt['solution']['text'])
        if nvt.get('solution')
        else None
    )
    refs = (
        [Ref(r['id'], r['type']) for r in nvt['refs']['ref']]
        if nvt.get('refs')
        else []
    )
    oid = nvt['oid']
    qod = (
        QOD(
            second['qod']['value'],
            second['qod']['type'],
        )
        if second.get('qod')
        else None
    )
    shr = Result(
        oid,
        nvt.get('type'),
        nvt.get('name'),
        nvt.get('family'),
        nvt.get('cvss_base'),
        nvt.get('tags'),
        solution,
        refs,
        second.get('port'),
        second.get('threat'),
        second.get('severity'),
        qod,
        second.get('description'),
    )
    if hr:
        hr.results.append(shr)
        first[host] = hr
    else:
        first[host] = HostResults(host, [shr])
    del nvt
    return first


logger = logging.getLogger(__name__)


def __create_nvt_top_ten(
    threat: str, group_by_threat: DataFrameGroupBy
) -> TopTen:
    threat = group_by_threat.get_group(threat)
    threat_nvts = threat[['nvt.oid', 'nvt.name']]
    counted = threat_nvts.value_counts()
    return TopTen(
        chart=None,
        top_ten=[
            NVTCount(oid=k[0], amount=v, name=k[1])
            for k, v in counted.head(10).to_dict().items()
        ],
    )


def __create_host_top_ten(result_series_df: DataFrame) -> TopTen:
    threat = result_series_df.get(['host.text', 'host.hostname'])
    if threat is None:
        threat = result_series_df.get(['host.text'])
    if threat is None:
        return None

    counted = threat.value_counts()
    return TopTen(
        chart=None,
        top_ten=[
            HostCount(ip=k[0], amount=v, name=k[1] if len(k) > 1 else None)
            for k, v in counted.head(10).to_dict().items()
        ],
    )


def __create_port_top_ten(result_series_df: DataFrame) -> TopTen:
    threat = result_series_df.get(['port'])
    if threat is None:
        return None
    counted = threat.value_counts()
    return TopTen(
        chart=None,
        top_ten=[
            PortCount(port=k, amount=v)
            for k, v in counted.head(10).to_dict().items()
        ],
    )


def __create_cvss_distribution_port_top_ten(
    result_series_df: DataFrame,
) -> TopTen:
    threat = result_series_df.get(['port', 'nvt.cvss_base'])
    if threat is None:
        return None
    counted = threat.value_counts()
    return TopTen(
        chart=None,
        top_ten=[
            CVSSDistributionCount(identifier=k[0], amount=v, cvss=k[1])
            for k, v in counted.head(10).to_dict().items()
        ],
    )


def __create_cvss_distribution_host_top_ten(
    result_series_df: DataFrame,
) -> TopTen:
    threat = result_series_df.get(
        ['host.text', 'host.hostname', 'nvt.cvss_base']
    )
    if threat is None:
        return None
    counted = threat.value_counts()
    return TopTen(
        chart=None,
        top_ten=[
            CVSSDistributionCount(identifier=k[0], amount=v, cvss=k[1])
            for k, v in counted.head(10).to_dict().items()
        ],
    )


def __create_cvss_distribution_nvt_top_ten(
    result_series_df: DataFrame,
) -> TopTen:
    threat = result_series_df.get(['nvt.oid', 'nvt.cvss_base'])
    if threat is None:
        return None
    counted = threat.value_counts()
    return TopTen(
        chart=None,
        top_ten=[
            CVSSDistributionCount(identifier=k[0], amount=v, cvss=k[1])
            for k, v in counted.head(10).to_dict().items()
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


def __create_summary_results(report: DataFrame) -> SummaryResults:
    counts = report.get(['result_count.full', 'result_count.filtered'])
    if counts is None:
        return None
    data = __simple_data_frame_to_values(counts)
    if len(data) != 2:
        return None
    data += [None]  # append graph
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
                        result[i][key] = value
            results.append(HostResults(host_text, result))
        return results
    except KeyError as e:
        logger.warning('report does not contain host.text returning []; %s', e)
        return None


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

        common_vulnerabilities = CommonVulnerabilities(
            __create_nvt_top_ten('High', group_by_threat),
            __create_nvt_top_ten('Medium', group_by_threat),
            __create_nvt_top_ten('Low', group_by_threat),
        )
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
        __create_summary_results(n_df),
    )
    results = __create_results(result_series_df)

    logger.info("data transformation")

    return Report(
        report.get('id'),
        summary,
        common_vulnerabilities,
        vulnerabilities_overview,
        results,
    )
