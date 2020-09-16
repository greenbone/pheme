# pylint: disable=W0614,W0511,W0401,C0103
# -*- coding: utf-8 -*-
# tests/generate_test_data.py
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
# pylint: disable=W0621,C0103
from pathlib import Path
import random
import string
import uuid


from typing import Dict, List
import xmltodict


def _random_text(length: int) -> str:
    return ''.join([random.choice(string.ascii_letters) for i in range(length)])


def gen_solution() -> Dict:
    return {
        'type': _random_text(15),
        'text': _random_text(250),
    }


def gen_host(hostname='localhost') -> Dict:
    return {
        'text': "{}.{}.{}.{}".format(
            random.randint(1, 254),
            random.randint(1, 254),
            random.randint(1, 254),
            random.randint(1, 254),
        ),
        'hostname': "{}.{}.org".format(
            hostname, _random_text(random.randint(10, 70))
        ),
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


def generate_nvt(oid: str, with_optional: bool = True) -> Dict:
    return {
        'oid': oid,
        'solution': gen_solution() if with_optional else None,
        'refs': gen_refs(10) if with_optional else None,
        'type': _random_text(15) if with_optional else None,
        'name': "faked example {}".format(oid) if with_optional else None,
        'family': _random_text(15) if with_optional else None,
        'cvss_base': _random_text(15) if with_optional else None,
        'tags': _random_text(150) if with_optional else None,
    }


threats = ['Low', 'Medium', 'High']


def gen_result(host: dict, oid: str, with_optional: bool = True) -> Dict:

    return {
        'host': host,
        'nvt': generate_nvt(oid),
        'port': '{}/tcp'.format(random.randint(80, 1001))
        if with_optional
        else None,
        'threat': random.choice(threats) if with_optional else None,
        'original_threat': random.choice(threats),
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
        'target': {
            **gen_identifiable(),
            'trash': _random_text(2),
        },
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


def generate_result_count(full: int, filtered: int) -> Dict:
    return {
        'full': str(full),
        'filtered': str(filtered),
    }


def gen_report(
    hosts: List[str], oids: List[str], with_optional: bool = True
) -> Dict:
    hosts = [gen_host(v) for v in hosts]
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
        'errors': gen_count() if with_optional else None,
        'results': {
            'max': '{}'.format(random.randint(1, 1000))
            if with_optional
            else None,
            'start': '{}'.format(random.randint(0, 1000))
            if with_optional
            else None,
            'result': [
                gen_result(host, oids[random.randint(0, len(oids) - 1)])
                for host in hosts
                for _ in range(1, len(oids) * 2)
            ],
        },
        'severity': gen_filtered() if with_optional else None,
        'result_count': gen_result_count() if with_optional else None,
    }


if __name__ == '__main__':
    own_path = Path(__file__).absolute()
    directory = own_path.__str__()[0 : (len(own_path.name) * -1)]
    number_of_hosts = 40
    print("generating {} hostnames".format(number_of_hosts))
    hosts = ["host_{}".format(i) for i in range(number_of_hosts)]
    print("generating oid for nvts")
    oids = ["oid_{}".format(i) for i in range(100)]
    print("generating report data")
    data = {'report': {'report': gen_report(hosts, oids, True)}}
    path = Path(
        '{}../test_data/artifical_{}_hosts_{}_oid_per_host.xml'.format(
            directory, number_of_hosts, len(oids)
        )
    )
    print("writing report data")
    path.write_text(xmltodict.unparse(data, pretty=True))
