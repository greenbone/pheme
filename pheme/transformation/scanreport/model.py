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
from typing import Dict, List, Union
from dataclasses import dataclass


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
