from functools import reduce
from typing import Callable, Optional


def group_by_host(first, second):
    host = second.pop('host')
    host = host if isinstance(host, str) else host["text"]
    to_add = [second]
    previous = first.get(host)
    if previous:
        to_add += previous
    first[host] = to_add
    return first


def group_by_nvt(first, second):
    nvt = second.pop('nvt')
    host = second.pop('host')
    second.pop('owner', None)
    host = host if isinstance(host, str) else host["text"]
    to_add = [{host: second}]
    oid = nvt['oid']
    previous = first.get(oid)
    to_add += previous['hosts'] if previous else []
    nvt['hosts'] = to_add
    first[oid] = nvt
    return first


def transform(data: dict, group_by: Optional[Callable] = group_by_host) -> dict:
    # add flavours ...
    result = dict(data)
    if group_by:
        raw_results = result["report"]["report"]["results"]["result"]
        grouped = reduce(group_by, raw_results, {})
        result['report']['report']['results']['result'] = grouped
    # delete detailed host information
    result['report']['report'].pop('host', None)
    result['report'] = result['report']['report']
    # delete filter information
    result['report'].pop('filters', None)
    result['report'].pop('sort', None)
    result['report'].pop('severity_class', None)
    # already in result information
    result['report'].pop('ports', None)
    return result
