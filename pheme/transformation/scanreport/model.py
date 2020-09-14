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
from typing import List, Union
from dataclasses import dataclass


@dataclass
class Identifiable:
    id: str
    name: str
    comment: str


@dataclass
class Target(Identifiable):
    trash: str


@dataclass
class Solution:
    type: str
    text: str


@dataclass
class Ref:
    id: str
    type: str


@dataclass
class QOD:
    value: str
    type: str


@dataclass
class Result:
    oid: str
    type: str
    name: str
    family: str
    cvss_base: str
    tags: str
    solution: Solution
    refs: List[Ref]
    port: str
    threat: str
    severity: str
    qod: QOD
    description: str


@dataclass
class HostResults:
    host: str
    results: List[Result]


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
class B64Chart:
    format: str  # png, jpg, ...
    chart: str  # b64 encoded binary, xml (on svg) content


@dataclass
class SummaryResults:
    available: int
    included: int
    chart: B64Chart  # base64,png


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
class TopTen:
    chart: B64Chart
    top_ten: List[Union[CVSSDistributionCount, NVTCount, HostCount, PortCount]]


@dataclass
class CommonVulnerabilities:
    high: TopTen
    medium: TopTen
    low: TopTen


@dataclass
class VulnerabilityOverview:
    hosts: TopTen
    network_topology: TopTen  # not there yet
    ports: TopTen
    cvss_distribution_ports: TopTen
    cvss_distribution_hosts: TopTen
    cvss_distribution_vulnerabilities: TopTen


@dataclass
class Report:
    id: str
    summary: Summary
    common_vulnerabilities: CommonVulnerabilities
    Vulnerability_overview: CommonVulnerabilities
    results: Results
