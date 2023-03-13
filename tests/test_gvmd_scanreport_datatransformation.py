# -*- coding: utf-8 -*-
# tests/test_gvmd_scanreport_datatransformation.py
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

import pytest
from pheme.transformation.scanreport.gvmd import (
    transform,
)

from tests.generate_test_data import gen_report

oids = [f"oid_{i}" for i in range(5)]
hosts = ["first", "second"]


def test_should_contain_non_general_ports():
    scan_results = gen_report(hosts, oids, port="80/tcp")
    data = {"report": {"report": scan_results}}
    report = transform(data)
    assert report.results[0]["equipment"]["ports"] == {"80/tcp"}


def test_remove_general_from_equipment_port_list():
    scan_results = gen_report(hosts, oids, port="general/tcp")
    data = {"report": {"report": scan_results}}
    report = transform(data)
    assert report.results[0]["equipment"]["ports"] == []


def test_grouping_nvt_oid_per_type():
    scan_results = gen_report(hosts, oids, with_optional=True)
    data = {"report": {"report": scan_results}}
    report = transform(data)
    results = report.results[0]["results"]
    # so far refs are hardcoded to ten
    assert len(results[0]["nvt_refs_ref"]["CVE"]) == 10


@pytest.mark.parametrize(
    "expected",
    [
        (2, gen_report(hosts, oids, with_optional=True)),
        (2, gen_report(hosts, oids, with_optional=False)),
        (0, gen_report([], [], with_optional=False)),
        (0, gen_report(None, [], with_optional=False)),
    ],
)
def test_report_generation_per_host(expected):
    amount_scans, scan_results = expected
    data = {"report": {"report": scan_results}}
    report = transform(data)
    assert len(report.results or []) == amount_scans
