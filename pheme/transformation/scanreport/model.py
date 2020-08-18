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
class Version:
    version: str


@dataclass
class Count:
    count: str


@dataclass
class Identifiable:
    id: str
    name: str
    comment: str


@dataclass
class Target(Identifiable):
    trash: str


@dataclass
class Task(Identifiable):
    progress: str
    target: Target


@dataclass
class Scan:
    task: Task


@dataclass
class Filtered:
    full: str
    filtered: str


@dataclass
class ResultCount(Filtered):
    debug: Filtered
    hole: Filtered
    info: Filtered
    log: Filtered
    warning: Filtered
    false_positive: Filtered
    text: str


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
class NVT:
    oid: str
    type: str
    name: str
    family: str
    cvss_base: str
    tags: str
    solution: Solution
    refs: List[Ref]


@dataclass
class HostSpecific:
    name: str
    description: str


@dataclass
class Result(NVT):
    port: str
    threat: str
    severity: str
    qod: QOD


@dataclass
class NVTResult(Result):
    hosts: List[HostSpecific]


@dataclass
class HostResult(Result):
    description: str


@dataclass
class HostResults:
    host: str
    results: List[HostResult]


@dataclass
class Results:
    max: str
    start: str
    scans: List[Union[NVTResult, HostResults]]


@dataclass
class Report:
    id: str
    gmp: Version
    scan_run_status: str
    hosts: Count
    closed_cves: Count
    vulns: Count
    os: Count
    apps: Count
    ssl_certs: Count
    task: Task
    timestamp: str
    scan_start: str
    timezone: str
    timezone_abbrev: str
    scan_end: str
    errors: Count
    results: Results
    severity: Filtered
    result_count: ResultCount
