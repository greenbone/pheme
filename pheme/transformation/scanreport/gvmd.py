# -*- coding: utf-8 -*-
# pheme/transformation/scanreport/gvmd.py
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
import base64
import io
import logging
import time
import urllib
from typing import Callable, Dict, List, Optional, Union

from matplotlib.figure import Figure
from pheme.transformation.scanreport.model import (
    # CountGraph,
    # Equipment,
    HostResults,
    Overview,
    Report,
)

logger = logging.getLogger(__name__)


def measure_time(func):
    def measure(*args, **kwargs):
        startt = time.process_time()
        result = func(*args, **kwargs)
        logger.info("%s took %s", func.__name__, time.process_time() - startt)
        return result

    return measure


__severity_class_colors = {
    'High': 'tab:red',
    'Medium': 'tab:orange',
    'Low': 'tab:blue',
}


def __create_default_figure():
    return Figure()


@measure_time
def __create_chart(
    set_plot: Callable,
    *,
    fig: Union[Figure, Callable] = __create_default_figure,
    modify_fig: Callable = None,
) -> Optional[str]:
    try:
        fig = fig() if callable(fig) else fig
        # https://matplotlib.org/faq/howto_faq.html#how-to-use-matplotlib-in-a-web-application-server
        ax = fig.subplots()
        set_plot(ax)
        if modify_fig:
            modify_fig(fig)
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=300)
        buf.seek(0)
        base64_fig = base64.b64encode(buf.read())
        uri = 'data:image/png;base64,' + urllib.parse.quote(base64_fig)
        del fig
        return uri
    # pylint: disable=W0703
    except Exception as e:
        logger.warning("returning None due to exception: %e", e)
        return None


def __severity_class_to_color(severity_classes: List[str]):
    return [__severity_class_colors.get(v, 'white') for v in severity_classes]


def __tansform_tags(item) -> List[Dict]:
    if isinstance(item, str):
        splitted = [i.split('=') for i in item.split('|')]
        return {i[0]: i[1] for i in splitted if len(i) == 2}
    return None


@measure_time
def __create_results_per_host_wo_pandas(report: Dict) -> List[HostResults]:
    results = report.get('results', {}).get('result', [])
    by_host = {}
    host_count = {}
    nvt_count = [0, 0, 0]

    def return_highest_threat(old: str, new: str) -> str:
        if old == 'High' or new == 'High':
            return 'High'
        if old == 'Medium' or new == 'Medium':
            return 'Medium'
        return 'Low'

    def transform_key(prefix: str, vic: Dict) -> Dict:
        return {
            "{}_{}".format(prefix, key): value for key, value in vic.items()
        }

    def group_refs(refs: List[Dict]) -> Dict:
        refs_ref = {}
        for ref in refs.get('ref', []):
            typus = ref.get('type', 'unknown')
            refs_ref[typus] = refs.get(typus, []) + [ref.get('id')]
        return refs_ref

    def threat_to_index(threat: str) -> int:
        if threat == 'High':
            return 0
        if threat == 'Medium':
            return 1
        return 2

    for result in results:
        hostname = result.get('host', {}).get('text', 'unknown')
        host_dict = by_host.get(hostname, {})
        threat = result.get('threat', 'unknown')
        highest_threat = return_highest_threat(
            host_dict.get('threat', ''), threat
        )
        port = result.get('port')
        nvt = transform_key("nvt", result.get('nvt', {}))  # interprete tags
        nvt['nvt_tags_interpreted'] = __tansform_tags(nvt.get('nvt_tags', ''))
        nvt['nvt_refs_ref'] = group_refs(nvt.get('nvt_refs', {}))
        # add equipment information
        qod = transform_key('qod', result.get('qod', {}))
        new_host_result = {
            "port": port,
            "threat": threat,
            "severity": result.get('severity'),
            "description": result.get('description'),
            **nvt,
            **qod,
        }
        host_results = host_dict.get('results', [])
        host_results.append(new_host_result)
        equipment = host_dict.get('equipment', {})
        equipment['ports'] = equipment.get('ports', []) + [port]
        # filter for best_os_cpe
        equipment['os'] = "unknown"
        by_host[hostname] = {
            "host": hostname,
            "threat": highest_threat,
            "equipment": equipment,
            "results": host_results,
        }
        # needs hostname, high, medium, low and total
        host_threats = host_count.get(hostname, [0, 0, 0])
        threat_index = threat_to_index(threat)
        host_threats[threat_index] += 1
        host_count[hostname] = host_threats
        # needs high, medium, low
        nvt_count[threat_index] += 1
    return list(by_host.values()), host_count, nvt_count


@measure_time
def transform(data: Dict[str, str]) -> Report:
    if not data:
        raise ValueError("Need data to process")
    report = data.get("report")
    # sometimes gvmd reports have .report.report sometimes just .report
    report = report.get("report", report)

    task = report.get('task') or {}
    gmp = report.get('gmp') or {}
    # n_df = pd.json_normalize(report)
    # hosts, nvts, vulnerable_equipment, results = __result_report(n_df)
    logger.info("data transformation")
    results, _, _ = __create_results_per_host_wo_pandas(report)
    return Report(
        report.get('id'),
        task.get('name'),
        task.get('comment'),
        gmp.get('version'),
        report.get('scan_start'),
        Overview(
            hosts=None,
            nvts=None,
            vulnerable_equipment=None,
        ),
        results,
    )
