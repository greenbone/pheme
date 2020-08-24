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
import logging
from typing import Dict

from django.template import loader
from django.conf import settings
from rest_framework import renderers
from rest_framework.request import HttpRequest
from weasyprint import CSS, HTML

logger = logging.getLogger(__name__)


class DetailScanReport(renderers.BaseRenderer):
    def _template_based_on_request(self, request: HttpRequest) -> str:
        return (
            'pdf_host_detail_scan_report.html'
            if request.GET.get('grouping') == 'host'
            else 'nvt_detailed_report.html'
        )

    def _enrich(self, data: Dict, request: HttpRequest) -> Dict:
        data['logo'] = settings.TEMPLATE_LOGO_ADDRESS
        data['grouping'] = (
            'host' if request.GET.get('grouping') == 'host' else 'nvt'
        )
        return data

    def render(self, data, accepted_media_type=None, renderer_context=None):
        raise NotImplementedError(
            'Renderer class requires .render() to be implemented'
        )


class DetailScanHTMLReport(DetailScanReport):
    media_type = 'text/html'
    format = 'html'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        logger.debug("generating html template")
        renderer_context = renderer_context or {}  # to throw key error
        request = renderer_context['request']
        template = self._template_based_on_request(request)
        return loader.get_template(template).render(self._enrich(data, request))


class DetailScanPDFReport(DetailScanReport):
    media_type = 'application/pdf'
    format = 'binary'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        logger.debug("generating html template")
        renderer_context = renderer_context or {}  # to throw key error
        request = renderer_context['request']
        template = self._template_based_on_request(request)
        html = loader.get_template(template).render(self._enrich(data, request))
        logger.debug("created html")
        css = loader.get_template('report.css').render(
            {
                'background_image': 'file://{}/Greenbone_Radar.png'.format(
                    settings.STATIC_DIR
                ),
                'indicator': 'file://{}/heading.svg'.format(
                    settings.STATIC_DIR
                ),
            }
        )

        pdf = HTML(string=html).write_pdf(stylesheets=[CSS(string=css)])
        logger.debug("created pdf")
        return pdf
