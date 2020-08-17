from functools import reduce
from typing import Callable, Optional, List, Union, Tuple, Dict
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


def __find_first_occurance(
    candidates: List[Union[HostResults, NVTResult]], is_the_chosen_one: Callable
) -> Tuple[int, Optional[Union[HostResults, NVTResult]]]:
    for i, candidate in enumerate(candidates):
        if is_the_chosen_one(candidate):
            return i, candidate
    return -1, None


def group_by_host(first, second):
    host = second.pop('host')
    host = host if isinstance(host, str) else host["text"]
    index, hr = __find_first_occurance(first, lambda h: h.host == host)
    # hr = first.get(host)
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
        QOD(second['qod']['value'], second['qod']['type'],)
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
        first[index] = hr
    # first[host] = hr
    else:
        # first[host] = HostResults(host, [shr])
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
        qod = (
            QOD(second['qod']['value'], second['qod']['type'],)
            if second.get('qod')
            else None
        )
        first.append(
            NVTResult(
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
        )
    return first


def transform(data: Dict[str, str], group_by: Callable = group_by_host) -> Report:
    report = data["report"]["report"]

    def may_create_version(key: str) -> Optional[Count]:
        return Version(**report[key]) if report.get(key) else None

    def may_create_count(key: str) -> Optional[Count]:
        return Count(**report[key]) if report.get(key) else None

    def may_create_target(data: Dict) -> Target:
        target_dict = data.get('target')
        if not target_dict:
            return None
        return Target(
            target_dict.get('id'),
            target_dict.get('name'),
            target_dict.get('comment'),
            target_dict.get('trash'),
        )

    def may_create_task() -> Task:
        task = report.get('task')
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
        filtered = data.get(key)
        if not filtered:
            return None
        return Filtered(**filtered)

    def may_create_result_count() -> ResultCount:
        result_count = report['result_count']
        if not result_count:
            return None
        return ResultCount(
            result_count['full'],
            result_count['filtered'],
            may_create_filtered(result_count, 'debug'),
            may_create_filtered(result_count, 'hole'),
            may_create_filtered(result_count, 'info'),
            may_create_filtered(result_count, 'log'),
            may_create_filtered(result_count, 'warning'),
            may_create_filtered(result_count, 'false_positive'),
            result_count['text'],
        )

    # grouped = reduce(group_by, report["results"]["result"], {})
    grouped = reduce(group_by, report["results"]["result"], [])

    return Report(
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
            report['results'].get('max'),
            report['results'].get('start'),
            grouped,
        ),
        may_create_filtered(report, 'severity'),
        may_create_result_count(),
    )
