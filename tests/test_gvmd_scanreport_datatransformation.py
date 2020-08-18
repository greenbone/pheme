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
import random
import string
import uuid
from typing import Dict


import pytest
from pheme.transformation.scanreport.gvmd import (
    transform,
    group_by_nvt,
    group_by_host,
)


def _random_text(length: int) -> str:
    return ''.join([random.choice(string.printable) for i in range(length)])


def gen_solution() -> Dict:
    return {
        'type': _random_text(15),
        'text': _random_text(250),
    }


def gen_host(hostname='localhost') -> Dict:
    return {
        'text': hostname,
    }


def gen_refs(length: int = 0) -> Dict:
    def ref():
        return {'id': uuid.uuid1().hex, 'type': _random_text(5)}

    return {'ref': [ref() for _ in range(length)]}


def gen_qod() -> Dict:
    return {
        'type': _random_text(10),
        'value': '{}'.format(random.randint(1, 254)),
    }


def generate_nvt(oid: str, with_optional: bool = False) -> Dict:
    return {
        'oid': oid,
        'solution': gen_solution() if with_optional else None,
        'refs': gen_refs(10) if with_optional else None,
        'type': _random_text(15) if with_optional else None,
        'name': _random_text(15) if with_optional else None,
        'family': _random_text(15) if with_optional else None,
        'cvss_base': _random_text(15) if with_optional else None,
        'tags': _random_text(150) if with_optional else None,
    }


threats = ['Log', 'Medium', 'High']


def gen_result(hostname: str, oid: str, with_optional: bool = False) -> Dict:
    return {
        'host': gen_host(hostname),
        'nvt': generate_nvt(oid),
        'port': '{}/tcp'.format(random.randint(80, 1001))
        if with_optional
        else None,
        'threat': random.choice(threats) if with_optional else None,
        'severity': '4.3' if with_optional else None,
        'qod': gen_qod() if with_optional else None,
        'description': _random_text(254) if with_optional else None,
    }


def gen_gmp() -> Dict:
    return {'version': '21.04'}


def gen_count(count: int = random.randint(1, 100)) -> Dict:
    return {'count': count}


def gen_identifiable() -> dict:
    return {
        'id': uuid.uuid1().hex,
        'name': _random_text(10),
        'comment': _random_text(150),
    }


def gen_task() -> Dict:
    return {
        **gen_identifiable(),
        'target': {**gen_identifiable(), 'trash': _random_text(2),},
        'progress': '100',
    }


def gen_filtered() -> Dict:
    return {'full': _random_text(25), 'filtered': _random_text(12)}


def gen_result_count() -> Dict:
    return {
        **gen_filtered(),
        'debug': gen_filtered(),
        'hole': gen_filtered(),
        'info': gen_filtered(),
        'log': gen_filtered(),
        'warning': gen_filtered(),
        'false_positive': gen_filtered(),
        'text': _random_text(25),
    }


oids = [uuid.uuid1().hex for _ in range(5)]


def gen_report(with_optional=False) -> Dict:
    return {
        'id': uuid.uuid1().hex if with_optional else None,
        'gmp': gen_gmp() if with_optional else None,
        'scan_run_status': '100' if with_optional else None,
        'hosts': gen_count(1) if with_optional else None,
        'closed_cves': gen_count() if with_optional else None,
        'vulns': gen_count() if with_optional else None,
        'os': gen_count() if with_optional else None,
        'apps': gen_count() if with_optional else None,
        'ssl_certs': gen_count() if with_optional else None,
        'task': gen_task() if with_optional else None,
        'timestamp': '2342' if with_optional else None,
        'scan_start': '2020-07-01T21:00' if with_optional else None,
        'timezone': 'timezone_abbrev' if with_optional else None,
        'timezone_abbrev': 'UTC' if with_optional else None,
        'scan_end': '2020-07-01T21:00' if with_optional else None,
        'erros': gen_count() if with_optional else None,
        'results': {
            'max': '{}'.format(random.randint(1, 1000))
            if with_optional
            else None,
            'start': '{}'.format(random.randint(0, 1000))
            if with_optional
            else None,
            'result': [
                gen_result(
                    '{}'.format(i % 2), oids[i % len(oids)], with_optional
                )
                for i in range(250)
            ],
        },
        'severity': gen_filtered() if with_optional else None,
        'result_count': gen_result_count() if with_optional else None,
    }


@pytest.mark.parametrize("scan_result", [gen_report(with_optional=True)])
def test_group_by_nvt(scan_result):
    data = {'report': {'report': scan_result}}
    result = transform(data, group_by=group_by_nvt)
    # we generate 250 scan results, there are exactly len(oids) possibilitites
    assert len(result.results.scans) == len(oids)


@pytest.mark.parametrize("scan_result", [gen_report()])
def test_group_by_host(scan_result):
    data = {'report': {'report': scan_result}}
    result = transform(data, group_by=group_by_host)
    # we generate 250 scan results, every second host is '0' every other '1'
    assert len(result.results.scans) == 2
