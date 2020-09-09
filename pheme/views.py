# -*- coding: utf-8 -*-
# pheme/views.py
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
import dataclasses
import rest_framework.renderers
from rest_framework.decorators import api_view, parser_classes, renderer_classes
from rest_framework.response import Response
from pheme.parser.xml import XMLParser
from pheme.transformation import scanreport
from pheme.storage import store, load


@api_view(['POST'])
@parser_classes([XMLParser])
@renderer_classes(
    [
        rest_framework.renderers.JSONRenderer,
    ]
)
def transform(request):
    grouping = request.GET.get('grouping')
    grouping_function = scanreport.gvmd.group_by_host
    if grouping == 'nvt':
        grouping_function = scanreport.gvmd.group_by_nvt
    name = store(
        "scanreport-{}".format(grouping),
        dataclasses.asdict(
            scanreport.gvmd.transform(request.data, grouping_function)
        ),
    )

    return Response(name)


@api_view(['GET'])
@renderer_classes(
    [
        rest_framework.renderers.JSONRenderer,
        scanreport.renderer.DetailScanHTMLReport,
        scanreport.renderer.DetailScanPDFReport,
    ]
)
def report(request, name: str):
    return Response(load(name))
