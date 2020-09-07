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
from functools import reduce
from typing import Callable, Optional, Dict
import logging

from .model import (
    Count,
    Filtered,
    HostResult,
    HostResults,
    HostSpecific,
    NVTResult,
    QOD,
    Ref,
    Report,
    ResultCount,
    Results,
    Solution,
    Target,
    Task,
    Version,
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
    shr = HostResult(
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


def group_by_nvt(first: Dict[str, NVTResult], second: Dict[str, str]):
    nvt = second.pop('nvt')
    host = second.pop('host')
    host = host if isinstance(host, str) else host["text"]
    oid = nvt['oid']
    nvt_result = first.get(oid)
    hs = HostSpecific(host, second.get('description'))
    if nvt_result:
        nvt_result.hosts.append(hs)
        first[oid] = nvt_result
    else:
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
        qod = (
            QOD(
                second['qod']['value'],
                second['qod']['type'],
            )
            if second.get('qod')
            else None
        )
        nvt_result = NVTResult(
            oid,
            nvt.get('type'),
            nvt.get('name'),
            nvt.get('family'),
            nvt['cvss_base'],
            nvt.get('tags'),
            solution,
            refs,
            second.get('port'),
            second.get('threat'),
            second.get('severity'),
            qod,
            [hs],
        )
        first[oid] = nvt_result
    del nvt

    return first


logger = logging.getLogger(__name__)


def transform(
    data: Dict[str, str], group_by: Callable = group_by_host
) -> Report:
    report = data.pop("report")
    # sometimes gvmd reports have .report.report sometimes just .report
    report = report.pop("report", None) or report
    del data
    logger.info("data transformation; grouped by %s.", group_by)

    def may_create_version(key: str) -> Optional[Count]:
        value = report.pop(key, None)
        if not value:
            return None
        return Version(value.get('version'))

    def may_create_count(key: str) -> Optional[Count]:
        value = report.pop(key, None)
        if not value:
            return None
        return Count(value.get('count'))

    def may_create_target(data: Dict[str, str]) -> Target:
        target_dict = data.pop('target', None)
        if not target_dict:
            return None
        return Target(
            target_dict.get('id'),
            target_dict.get('name'),
            target_dict.get('comment'),
            target_dict.get('trash'),
        )

    def may_create_task() -> Task:
        task = report.pop('task', None)
        if not task:
            return None
        return Task(
            task.get('id'),
            task.get('name'),
            task.get('comment'),
            may_create_target(task),
            task.get('progress'),
        )

    def may_create_filtered(data: Dict[str, str], key: str) -> Filtered:
        filtered = data.pop(key, None)
        if not filtered:
            return None
        return Filtered(filtered.get('full'), filtered.get('filtered'))

    def may_create_result_count() -> ResultCount:
        result_count = report.pop('result_count', None)
        if not result_count:
            return None
        return ResultCount(
            result_count.get('full'),
            result_count.get('filtered'),
            may_create_filtered(result_count, 'debug'),
            may_create_filtered(result_count, 'hole'),
            may_create_filtered(result_count, 'info'),
            may_create_filtered(result_count, 'log'),
            may_create_filtered(result_count, 'warning'),
            may_create_filtered(result_count, 'false_positive'),
            result_count.get('text'),
        )

    original_results = report.pop('results')
    grouped = reduce(group_by, original_results.pop("result"), {})
    result = Report(
        report.get('id'),
        may_create_version('gmp'),
        report.get('scan_run_status'),
        may_create_count('hosts'),
        may_create_count('closed_cves'),
        may_create_count('vulns'),
        may_create_count('os'),
        may_create_count('apps'),
        may_create_count('ssl_certs'),
        may_create_task(),
        report.get('timestamp'),
        report.get('scan_start'),
        report.get('timezone'),
        report.get('timezone_abbrev'),
        report.get('scan_end'),
        may_create_count('errors'),
        Results(
            original_results.get('max'),
            original_results.get('start'),
            list(grouped.values()),
        ),
        may_create_filtered(report, 'severity'),
        may_create_result_count(),
    )
    del grouped
    del original_results
    del report
    return result
