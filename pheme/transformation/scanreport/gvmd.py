# -*- coding: utf-8 -*-
# pheme/transformation/scanreport/gvmd.py
# Copyright (C) 2020-2021 Greenbone AG
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
import logging
import time

from typing import Dict, List, Optional


from pheme.transformation.scanreport.model import (
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


def __tansform_tags(item) -> Optional[Dict[str, str]]:
    if isinstance(item, str):
        split = [i.split("=") for i in item.split("|")]
        return {i[0]: i[1].replace("\n", " ") for i in split if len(i) == 2}
    return None


def __group_refs(refs: Dict[str, str]) -> Dict:
    refs_ref = {}
    for ref in refs.get("ref", []):
        if isinstance(ref, dict):
            typus = ref.get("type", "unknown")
            refs_ref[typus] = refs_ref.get(typus, []) + [ref.get("id")]
    return refs_ref


def __get_host_ip_from_result(result) -> str:
    if isinstance(result, str):
        return result
    if isinstance(result, dict):
        host = result.get("host", {})
        if isinstance(host, dict):
            return host.get("text", "unknown")
        return host
    return "unknown"


def __get_hostname_from_result(result) -> str:
    if isinstance(result, dict):
        host = result.get("host", {})
        if isinstance(host, dict):
            return host.get("hostname", "")
    return ""


def __return_highest_threat(threats: List[int]) -> str:
    """
    returns the highest threat
    """
    for i, value in enumerate(threats):
        if value > 0:
            return __threats[i]
    return "NA"


def __host_threat_overview(threat_count: Dict) -> Dict:
    """
    returns nvt statistics mostly used in the per host overview
    """
    result = {**threat_count}
    result["total"] = sum(threat_count.values())
    result["highest"] = __return_highest_threat(threat_count.values())
    return result


def __return_highest_severity(severities: List[int]) -> str:
    """
    returns the highest severity within a list
    """
    for i in range(len(severities) - 1, -1, -1):
        if severities[i] > 0:
            return str(i + 1)
    return "NA"


def __host_severity_overview(nvt_count: List[int]) -> Dict:
    """
    returns nvt severity statistics mostly used in the per host overview
    """
    result = {str(i + 1): value for i, value in enumerate(nvt_count)}
    result["total"] = sum(nvt_count)
    result["highest"] = __return_highest_severity(nvt_count)
    return result


def __create_host_information_lookup(report: Dict) -> Dict:
    """
    created a lookup table for available host information
    """
    # lookup for host information name and dict name
    information_key = {"best_os_txt": "os"}

    def filter_per_host(host: Dict) -> Dict:
        information = {}
        found = 0

        def check_host_detail(detail: Dict) -> int:
            name = detail.get("name", "")
            if name in information_key:
                information[information_key.get(name)] = detail.get("value")
                return 1
            return 0

        details = host.get("detail", [])
        if isinstance(details, dict):
            check_host_detail(details)
            return information
        elif isinstance(details, list):
            for detail in details:
                found += check_host_detail(detail)
                if found == len(information_key):
                    return information
            return information
        else:
            return information

    result = {}
    hosts = report.get("host")
    if isinstance(hosts, dict):
        result[hosts.get("ip", "unknown")] = filter_per_host(hosts)
    elif isinstance(hosts, list):
        # best_os_txt seems to be in the end
        for host in hosts[::-1]:
            result[host.get("ip", "unknown")] = filter_per_host(host)
    return result


@measure_time
def __create_results_per_host(report: Dict) -> List[Dict]:
    """
    creates the results dict used by a vulnerability-report based on a given
    gvmd report.
    """
    host_information_lookup = __create_host_information_lookup(report)
    results = report.get("results", {}).get("result", [])
    hosts = report.get("host", [])
    by_host = {}
    host_threat_count = {}
    host_severity_count = {}
    threat_count = [0] * len(__threats)

    def transform_key(prefix: str, vic: Dict) -> Dict:
        return {f"{prefix}_{key}": value for key, value in vic.items()}

    def per_result(result):
        host_ip = __get_host_ip_from_result(result)
        hostname = __get_hostname_from_result(result)
        host_dict = by_host.get(host_ip, {})
        threat = result.get("threat", "unknown")
        port = result.get("port")
        nvt = transform_key("nvt", result.get("nvt", {}))
        nvt["nvt_tags_interpreted"] = __tansform_tags(nvt.get("nvt_tags", ""))
        nvt["nvt_refs_ref"] = __group_refs(nvt.get("nvt_refs", {}))
        qod = transform_key("qod", result.get("qod", {}))
        severity = float(result.get("severity", "0.0"))
        notes = result.get("notes", {}).get("note", [])
        overrides = result.get("overrides", {}).get("override", [])

        new_host_result = {
            "hostname": hostname,
            "port": port,
            "threat": threat,
            "severity": severity,
            "description": result.get("description"),
            **nvt,
            **qod,
            "notes": [],
            "overrides": [],
        }
        host_results = host_dict.get("results", [])
        host_results.append(new_host_result)
        hostnames = host_dict.get("hostnames", [])
        if hostname is not None and hostname not in hostnames:
            hostnames.append(hostname)
        equipment = host_dict.get("equipment", {})
        ports = list(dict.fromkeys(equipment.get("ports", [])))
        if port and not port.startswith("general"):
            ports = set(ports + [port])
        equipment["ports"] = ports
        if not equipment.get("os"):
            equipment["os"] = host_information_lookup.get(host_ip, {}).get(
                "os", "unknown"
            )

        # needs host_ip, high, medium, low
        host_threats = host_threat_count.get(
            host_ip, {threat: 0 for threat in __threats}
        )
        threat_index = __threat_index_lookup.get(threat)
        if threat_index is not None:
            threat_count[threat_index] += 1
        if host_threats.get(threat) is not None:
            host_threats[threat] += 1
        host_threat_count[host_ip] = host_threats

        # needs high, medium, low

        # severity 1 to 10
        host_severities = host_severity_count.get(host_ip, [0] * 10)
        if severity > 0:
            host_severities[int(severity) - 1] += 1
        host_severity_count[host_ip] = host_severities

        def per_note(note):
            result_notes = new_host_result.get("notes", [])
            text = ""
            excerpt = "0"
            if isinstance(note["text"], dict):
                if "text" in note["text"]:
                    text = note["text"]["text"]
                if "excerpt" in note["text"]:
                    excerpt = note["text"]["excerpt"]
            else:
                text = note["text"]

            new_note = {
                "text": text,
                "text_excerpt": excerpt,
            }
            result_notes.append(new_note)

        def per_override(override):
            result_overrides = new_host_result.get("overrides", [])
            severity = override["severity"]
            severity_description = severity
            if not severity:
                severity_description = "Any severity"
            elif float(severity) == 0.0:
                severity_description = "Log"
            elif float(severity) > 0.0:
                severity_description = "Any positive severity"

            text = ""
            excerpt = "0"
            if isinstance(override["text"], dict):
                if "text" in override["text"]:
                    text = override["text"]["text"]
                if "excerpt" in override["text"]:
                    excerpt = override["text"]["excerpt"]
            else:
                text = override["text"]

            new_override = {
                "text": text,
                "text_excerpt": excerpt,
                "severity": severity,
                "severity_description": severity_description,
                "new_severity": override["new_severity"],
            }
            result_overrides.append(new_override)

        # lists with just one element can be parsed as dict by xmltodict
        if isinstance(notes, dict):
            per_note(notes)
        else:
            for note in notes:
                per_note(note)

        if isinstance(overrides, dict):
            per_override(overrides)
        else:
            for override in overrides:
                per_override(override)

        by_host[host_ip] = {
            "host": host_ip,
            "hostname": "",
            "hostnames": hostnames,
            "threats": __host_threat_overview(host_threats),
            "severities": __host_severity_overview(host_severities),
            "equipment": equipment,
            "results": host_results,
        }

    def per_host(host):
        host_ip = host.get("ip")
        if host_ip not in by_host:
            return

        def per_detail(detail):
            name = detail.get("name", "")
            value = detail.get("value", "")

            if name == "EXIT_CODE":
                return

            if name == "hostname" and by_host[host_ip]["hostname"] == "":
                by_host[host_ip]["hostname"] = value

        details = host.get("detail", [])
        if isinstance(details, dict):
            per_detail(details)
        else:
            for detail in details:
                per_detail(detail)

    # lists with just one element can be parsed as dict by xmltodict
    if isinstance(results, dict):
        per_result(results)
    else:
        for result in results:
            per_result(result)

    if isinstance(hosts, dict):
        per_host(hosts)
    elif isinstance(hosts, list):
        for host in hosts:
            per_host(host)

    threat_count_dict = {
        __threats[i]: count for i, count in enumerate(threat_count)
    }
    # sort by amount descending
    host_threat_count = dict(
        sorted(
            host_threat_count.items(),
            key=lambda x: sum(x[1].values()),
            reverse=True,
        )
    )

    return list(by_host.values()), host_threat_count, threat_count_dict


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

    task = report.get("task") or {}
    logger.info("data transformation")
    results, host_counts, nvts_counts = __create_results_per_host(report)

    return Report(
        report.get("id"),
        task.get("name"),
        task.get("comment"),
        report.get("scan_start"),
        Overview(
            hosts=host_counts, nvts=nvts_counts, vulnerable_equipment=None
        ),
        results,
    )
