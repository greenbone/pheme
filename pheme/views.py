# -*- coding: utf-8 -*-
# pheme/views.py
# Copyright (C) 2020-2021 Greenbone Networks GmbH
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
from rest_framework.request import Request


from pheme.parser.xml import XMLFormParser, XMLParser
from pheme.transformation import scanreport
from pheme.storage import store, load
from pheme.renderer import MarkDownTableRenderer, XMLRenderer, CSVRenderer
from pheme.transformation.scanreport import model


@api_view(['GET'])
@renderer_classes(
    [
        rest_framework.renderers.JSONRenderer,
    ]
)
def load_cache(request, key):
    return Response(load(key))


@api_view(['POST'])
@parser_classes([rest_framework.parsers.JSONParser])
@renderer_classes(
    [
        rest_framework.renderers.JSONRenderer,
    ]
)
def store_cache(request):
    key = request.data.get("key", "unknown")
    data = request.data.get('value')
    if request.data.get('append'):
        if isinstance(data, dict):
            cached = load(key) or {}
            cached[data.get('name', 'unknown')] = data.get('content')
            data = cached
    name = store(key, data, id_generator=str)
    return Response(name)


@api_view(['POST'])
@parser_classes([XMLParser, XMLFormParser])
@renderer_classes(
    [
        rest_framework.renderers.JSONRenderer,
    ]
)
def transform(request):
    name = store(
        "scanreport",
        dataclasses.asdict(scanreport.gvmd.transform(request.data)),
    )
    return Response(name)


@api_view(['POST'])
@parser_classes([XMLParser])
@renderer_classes(
    [
        rest_framework.renderers.JSONRenderer,
    ]
)
def unmodified(request):
    return Response(request.data)


@api_view(['GET'])
@renderer_classes(
    [
        rest_framework.renderers.JSONRenderer,
    ]
)
def template_elements(request: Request, name: str):
    def load_value_of(key) -> str:
        may_val = load(key) or {}
        return may_val

    images = load_value_of("{}images".format(name))
    return Response(
        {
            "template": load_value_of("{}html_template".format(name)),
            "pdf_css": load_value_of("{}pdf_css".format(name)),
            "html_css": load_value_of("{}html_css".format(name)),
            "images": images,
        }
    )


@api_view(['GET'])
@renderer_classes(
    [
        rest_framework.renderers.JSONRenderer,
        scanreport.renderer.ReportFormatPDFReport,
        scanreport.renderer.ReportFormatHTMLReport,
        scanreport.renderer.VulnerabilityHTMLReport,
        scanreport.renderer.VulnerabilityPDFReport,
        XMLRenderer,
        CSVRenderer,
    ]
)
def report(request: Request, name: str):
    def load_value_of(key) -> str:
        may_val = load(key) or {}
        return may_val

    if "report_format_editor" in request.accepted_media_type:
        images = load_value_of("{}images".format(name))
        return Response(
            {
                "template": load_value_of("{}html_template".format(name)),
                "vulnerability_report": load(name),
                "pdf_css": load_value_of("{}pdf_css".format(name)),
                "html_css": load_value_of("{}html_css".format(name)),
                "images": images,
            }
        )
    data = load(name)
    if request.GET.get('without_overview'):
        # remove charts
        data.pop('overview', None)
    if request.META.get('HTTP_ACCEPT') == "application/xml":
        # XML needs exactly one root
        data = {'report': data}
    return Response(data)


@api_view(['GET'])
@renderer_classes(
    [
        rest_framework.renderers.JSONRenderer,
        MarkDownTableRenderer,
    ]
)
def scanreport_data_description(request):
    return Response(dataclasses.asdict(model.describe()))
