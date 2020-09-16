# -*- coding: utf-8 -*-
# tests/test_report_generation.py
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

from uuid import uuid4
from typing import List

from rest_framework.test import APIClient
from django.urls import reverse
from django.core.cache import cache

from tests.generate_test_data import gen_report


def generate(amount: int) -> List[str]:
    return ["%s" % uuid4() for _ in range(amount)]


def test_report_contains_charts():
    client = APIClient()
    url = reverse('transform')
    report = {'report': {'report': gen_report(generate(10), generate(5))}}
    response = client.post(url, data=report, format='xml')
    assert response.status_code == 200
    result = cache.get(response.data)
    assert result['summary'] is not None
    assert result['summary']['results'] is not None
    assert result['summary']['results']['chart'] is not None
    assert len(result['common_vulnerabilities']) is 3
    for cv in result['common_vulnerabilities']:
        assert cv['chart'] is not None
    assert result['vulnerability_overview']['hosts']['chart'] is not None
    assert result['vulnerability_overview']['ports']['chart'] is not None
    assert (
        result['vulnerability_overview']['cvss_distribution_ports']['chart']
        is not None
    )
    assert (
        result['vulnerability_overview']['cvss_distribution_hosts']['chart']
        is not None
    )
    assert (
        result['vulnerability_overview']['cvss_distribution_vulnerabilities'][
            'chart'
        ]
        is not None
    )
