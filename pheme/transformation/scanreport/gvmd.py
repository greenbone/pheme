# pylint: disable=W0614,W0511,W0401,C0103
import dataclasses
from functools import reduce
from typing import Callable, Optional, List, Union, Tuple
from .model import *


def __find_first_occurance(
    candidates: List[Union[HostResults, NVTResult]], is_the_chosen_one: Callable
) -> Tuple[int, Optional[Union[HostResults, NVTResult]]]:
    for i, r in enumerate(candidates):
        if is_the_chosen_one(r):
            return i, r
    return -1, None


def group_by_host(first, second):
    host = second.pop('host')
    host = host if isinstance(host, str) else host["text"]
    index, hr = __find_first_occurance(first, lambda h: h.host == host)
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
    shr = HostResult(
        oid,
        nvt['type'],
        nvt['name'],
        nvt['family'],
        nvt['cvss_base'],
        nvt['tags'],
        solution,
        refs,
        second['port'],
        second['threat'],
        second['severity'],
        QOD(second['qod']['value'], second['qod']['type'],),
        second['description'],
    )
    if hr:
        hr.results.append(shr)
        first[index] = hr
    else:
        first.append(HostResults(host, [shr]))
    return first


def group_by_nvt(first, second):
    nvt = second.pop('nvt')
    host = second.pop('host')
    host = host if isinstance(host, str) else host["text"]
    oid = nvt['oid']
    index, nvt_result = __find_first_occurance(first, lambda n: n.oid == oid)
    hs = HostSpecific(host, second.get('description'))
    if nvt_result:
        nvt_result.hosts.append(hs)
        first[index] = nvt_result
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
        first.append(
            NVTResult(
                oid,
                nvt['type'],
                nvt['name'],
                nvt['family'],
                nvt['cvss_base'],
                nvt['tags'],
                solution,
                refs,
                second['port'],
                second['threat'],
                second['severity'],
                QOD(second['qod']['value'], second['qod']['type'],),
                [hs],
            )
        )
    return first


def transform(data: dict, group_by: Optional[Callable] = group_by_host) -> dict:
    result = dict(data)
    report = result["report"]["report"]
    raw_results = report["results"]["result"]
    grouped = reduce(group_by, raw_results, [])

    return dataclasses.asdict(
        Report(
            report['id'],
            Version(**report['gmp']),
            report['scan_run_status'],
            Count(**report['hosts']),
            Count(**report['closed_cves']),
            Count(**report['vulns']),
            Count(**report['os']),
            Count(**report['apps']),
            Count(**report['ssl_certs']),
            Task(
                report.get('task').get('id'),
                report.get('task').get('name'),
                report.get('task').get('comment'),
                Target(**report.get('task').get('target')),
                report.get('task').get('progress'),
            ),
            report.get('timestamp'),
            report.get('scan_start'),
            report.get('timezone'),
            report.get('timezone_abbrev'),
            report.get('scan_end'),
            Count(**report['errors']),
            Results(
                report['results']['max'], report['results']['start'], grouped
            ),
            Filtered(**report['severity']),
            ResultCount(
                report['result_count']['full'],
                report['result_count']['filtered'],
                Filtered(**report['result_count']['debug']),
                Filtered(**report['result_count']['hole']),
                Filtered(**report['result_count']['info']),
                Filtered(**report['result_count']['log']),
                Filtered(**report['result_count']['warning']),
                Filtered(**report['result_count']['false_positive']),
                report['result_count']['text'],
            ),
        ),
    )
