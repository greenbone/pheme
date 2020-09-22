# -*- coding: utf-8 -*-
# pheme/transformation/scanreport/model.py
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
# pylint: disable=W0614,W0511,W0401,C0103
from dataclasses import dataclass
from typing import Dict, List, Union


@dataclass
class QOD:
    value: str
    type: str


@dataclass
class HostResults:
    host: str
    results: List[Dict]


@dataclass
class Results:
    max: str
    start: str
    scans: List[HostResults]


@dataclass
class Scan:
    name: str
    start: str
    duration: str
    hosts_scanned: str
    comment: str


@dataclass
class SummaryReport:
    applied_filter: str
    severities: List[str]
    timezone: str


@dataclass
class SummaryResults:
    available: int
    included: int
    chart: str  # base64,png


@dataclass
class Summary:
    scan: Scan
    report: SummaryReport
    results: SummaryResults


@dataclass
class NVTCount:
    oid: str
    amount: int
    name: str


@dataclass
class HostCount:
    ip: str
    amount: int
    name: str


@dataclass
class CVSSDistributionCount:
    identifier: str
    amount: int
    cvss: str


@dataclass
class PortCount:
    port: str
    amount: int


@dataclass
class CountGraph:
    name: str
    chart: str
    counts: List[Union[CVSSDistributionCount, NVTCount, HostCount, PortCount]]


@dataclass
class VulnerabilityOverview:
    hosts: CountGraph
    network_topology: CountGraph  # not there yet
    ports: CountGraph
    cvss_distribution_ports: CountGraph
    cvss_distribution_hosts: CountGraph
    cvss_distribution_vulnerabilities: CountGraph


@dataclass
class SeverityCount:
    severity: str
    amount: int


@dataclass
class HostOverview:
    host: str
    highest_severity: str
    counts: List[SeverityCount]


@dataclass
class Report:
    id: str
    summary: Summary
    common_vulnerabilities: List[CountGraph]
    vulnerability_overview: VulnerabilityOverview
    host_overviews: List[HostOverview]
    results: Results


def descripe():
    return Report(
        id="str; identifier of a report",
        summary=Summary(
            scan=Scan(
                name="str; name of the scan",
                start="str; start date",
                duration="str; end date (needs to be renamend)",
                hosts_scanned="str; number of scanned hosts",
                comment="str; comment of a report",
            ),
            report=SummaryReport(
                applied_filter="str; applied filter of reports",
                severities=[
                    "str; High",
                    "str; Medium",
                    "str; Low",
                ],
                timezone="str; the timezone of the report",
            ),
            results=None,
        ),
        common_vulnerabilities=[
            CountGraph(
                name="High",
                chart="str; link to chart image (base64 encoded datalink)",
                counts=[
                    NVTCount(
                        oid="str; oid of nvt",
                        amount="int; amount of nvts with severity high",
                        name="str; name of nvt",
                    )
                ],
            ),
            CountGraph(
                name="Medium",
                chart="str; link to chart image (base64 encoded datalink)",
                counts=[
                    NVTCount(
                        oid="str; oid of nvt",
                        amount="int; amount of nvts within severityh",
                        name="str; name of nvt",
                    )
                ],
            ),
            CountGraph(
                name="Low",
                chart="str; link to chart image (base64 encoded datalink)",
                counts=[
                    NVTCount(
                        oid="str; oid of nvt",
                        amount="int; amount of nvts within severityh",
                        name="str; name of nvt",
                    )
                ],
            ),
        ],
        vulnerability_overview=VulnerabilityOverview(
            hosts=CountGraph(
                name="str; hosts",
                chart="str; link to chart image (base64 encoded datalink)",
                counts=[
                    HostCount(
                        ip="str; IP Address of the host",
                        amount="int; amount of found security breaches",
                        name="str; hostname",
                    )
                ],
            ),
            network_topology=None,
            ports=CountGraph(
                name="str; ports",
                chart="str; link to chart image (base64 encoded datalink)",
                counts=[
                    PortCount(
                        port="str; port (e.g. tcp/20)",
                        amount="int; amount of found security breaches",
                    )
                ],
            ),
            cvss_distribution_ports=CountGraph(
                name="str; cvss distribution ports",
                chart="str; link to chart image (base64 encoded datalink)",
                counts=[
                    CVSSDistributionCount(
                        identifier="ports",
                        amount="int; amount of cvss across ports in report",
                        cvss="str; cvss",
                    ),
                ],
            ),
            cvss_distribution_hosts=CountGraph(
                name="str; cvss distribution hosts",
                chart="str; link to chart image (base64 encoded datalink)",
                counts=[
                    CVSSDistributionCount(
                        identifier="hosts",
                        amount="int; amount of cvss across hosts in report",
                        cvss="str; cvss",
                    ),
                ],
            ),
            cvss_distribution_vulnerabilities=CountGraph(
                name="str; cvss distribution hosts",
                chart="str; link to chart image (base64 encoded datalink)",
                counts=[
                    CVSSDistributionCount(
                        identifier="ports",
                        amount="int; amount of cvss across hosts in report",
                        cvss="str; cvss",
                    ),
                ],
            ),
        ),
        host_overviews=[
            HostOverview(
                host="str; ip address of the host",
                highest_severity="str; highest severity of the host",
                counts=[
                    SeverityCount(
                        severity="str; High", amount="int; amount of severity"
                    ),
                    SeverityCount(
                        severity="str; Medium", amount="int; amount of severity"
                    ),
                    SeverityCount(
                        severity="str; Low", amount="int; amount of severity"
                    ),
                ],
            )
        ],
        results=Results(
            max="str; max results",
            start="str; start of results",
            scans=[
                HostResults(
                    host="str; ip address of host",
                    results={
                        'nvt.oid': 'str; nvt.oid; optional',
                        'nvt.type': 'str; nvt.type; optional',
                        'nvt.name': 'str; nvt.name; optional',
                        'nvt.family': 'str; nvt.family; optional',
                        'nvt.cvss_base': 'str; nvt.cvss_base; optional',
                        'nvt.tags': 'str; nvt.tags; optional',
                        'nvt.refs.ref': 'str; nvt.refs.ref; optional',
                        'nvt.solution.type': 'str; nvt.solution.type; optional',
                        'nvt.solution.text': 'str; nvt.solution.text; optional',
                        'port': 'str; port; optional',
                        'threat': 'str; threat; optional',
                        'severity': 'str; severity; optional',
                        'qod.value': 'str; qod.value; optional',
                        'qod.type': 'str; qod.type; optional',
                        'description': 'str; description; optional',
                    },
                )
            ],
        ),
    )
