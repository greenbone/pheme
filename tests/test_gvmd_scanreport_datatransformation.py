# -*- coding: utf-8 -*-
# tests/test_gvmd_scanreport_datatransformation.py
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
import uuid

import pytest
from pheme.transformation.scanreport.gvmd import (
    transform,
    group_by_nvt,
    group_by_host,
)

from tests.generate_test_data import gen_report


oids = [uuid.uuid1().hex for _ in range(5)]
hosts = ['first', 'second']

@pytest.mark.parametrize(
    "scan_result", [gen_report(hosts, oids, with_optional=True)]
)
def test_group_by_nvt(scan_result):
    data = {'report': {'report': scan_result}}
    result = transform(data, group_by=group_by_nvt)
    assert len(result.results.scans) == len(oids)


@pytest.mark.parametrize(
    "scan_result", [gen_report(hosts, oids, with_optional=False)]
)
def test_group_by_host(scan_result):
    data = {'report': {'report': scan_result}}
    result = transform(data, group_by=group_by_host)
    assert len(result.results.scans) == 2
