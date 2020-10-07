# -*- coding: utf-8 -*-
# pheme/transformation/scanreport/renderer.py
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
import logging
import urllib
from pathlib import Path
from typing import Dict


from django.conf import settings
from django.core.cache import cache
from django.template import Template, Context, loader
from rest_framework import renderers
from rest_framework.request import Request
from weasyprint import CSS, HTML

logger = logging.getLogger(__name__)


def as_datalink(data: bytes, file_format: str) -> str:
    img = urllib.parse.quote(base64.b64encode(data))
    return 'data:image/{};base64,{}'.format(file_format, img)


def file_as_datalink(location: str) -> str:
    file_format = location.split('.')[-1]
    if file_format == 'svg':
        file_format += '+xml'
    return as_datalink(Path(location).read_bytes(), file_format=file_format)


def _load_design_elemets():
    return {
        'logo': file_as_datalink(settings.TEMPLATE_LOGO_ADDRESS),
        'cover_image': file_as_datalink(settings.TEMPLATE_COVER_IMAGE_ADDRESS),
        'indicator': file_as_datalink(
            '/{}/heading.svg'.format(settings.STATIC_DIR)
        ),
    }


def _get_css(name: str) -> CSS:
    return loader.get_template(name).render(_load_design_elemets())


def _enrich(name: str, data: Dict) -> Dict:
    data['internal_name'] = name
    return data


def _get_request(renderer_context: Dict) -> Request:
    renderer_context = renderer_context or {}  # to throw key error
    return renderer_context['request']


def _default_not_found_response(
    renderer_context: Dict, request: Request
) -> str:
    resp = renderer_context['response']
    resp.status_code = 404
    # pylint: disable=W0212
    path = request._request.path
    report_id = path[path.rfind('/') + 1 :]
    return '"not data found for %s"' % report_id


class DetailScanReport(renderers.BaseRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        request = _get_request(renderer_context)
        if not data:
            return _default_not_found_response(renderer_context, request)

        name = data.get('internal_name')
        cache_key = "{}/{}".format(self.media_type, name) if name else None
        logger.debug("generating report %s", cache_key)

        if cache_key:
            cached = cache.get(cache_key)
            if cached:
                return cached
        result = self.apply(name, data)
        if cache_key:
            cache.set(cache_key, result)
        return result

    def apply(self, name: str, data: Dict):
        raise NotImplementedError(
            'DetailScanReport class requires .apply() to be implemented'
        )


class DetailScanHTMLReport(DetailScanReport):
    __template = 'scan_report.html'
    media_type = 'text/html'
    format = 'html'

    def _enrich(self, name: str, data: Dict) -> Dict:
        data = _enrich(name, data)
        data['css'] = _get_css('html_report.css')
        return data

    def apply(self, name: str, data: Dict):
        return loader.get_template(self.__template).render(
            self._enrich(name, data)
        )


class DetailScanPDFReport(DetailScanReport):
    __template = 'scan_report.html'
    media_type = 'application/pdf'
    format = 'binary'

    def apply(self, name: str, data: Dict):
        logger.debug("got template: %s", self.__template)
        html = loader.get_template(self.__template).render(_enrich(name, data))
        logger.debug("created html")
        css = _get_css('pdf_report.css')
        pdf = HTML(string=html).write_pdf(stylesheets=[CSS(string=css)])
        logger.debug("created pdf")
        return pdf


class ReportFormatHTMLReport(renderers.BaseRenderer):
    media_type = 'text/html+report_format_editor'
    format = 'html'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        request = _get_request(renderer_context)
        if not data:
            return _default_not_found_response(renderer_context, request)
        template = Template(data['template'])
        data['scan_report']['css'] = data['html_css']
        data['scan_report']['images'] = data['images']
        context = Context(data['scan_report'])
        html = template.render(context)
        logger.debug("created html")
        return html


class ReportFormatPDFReport(renderers.BaseRenderer):
    media_type = 'application/pdf+report_format_editor'
    format = 'binary'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        request = _get_request(renderer_context)
        if not data:
            return _default_not_found_response(renderer_context, request)
        data['scan_report']['images'] = data['images']
        template = Template(data['template'])
        context = Context(data['scan_report'])
        html = template.render(context)
        logger.debug("created html")
        css = Template(data['pdf_css']).render(context)
        pdf = HTML(string=html).write_pdf(stylesheets=[CSS(string=css)])
        logger.debug("created pdf")
        return pdf
