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
    def _get_css(self, name: str) -> CSS:
        return loader.get_template(name).render(
            {
                'background_image': settings.TEMPLATE_COVER_IMAGE_ADDRESS,
                'indicator': 'file://{}/heading.svg'.format(
                    settings.STATIC_DIR
                ),
            }
        )

    def _template_based_on_request(self, request: HttpRequest) -> str:
        try:
            sort = self.media_type[self.media_type.index('/') + 1 :]
            return (
                '{}_host_detail_scan_report.html'.format(sort)
                if request.GET.get('grouping') == 'host'
                else '{}_nvt_detail_scan_report.html'.format(sort)
            )
        except:
            raise ValueError(
                'Unable to identify template type based on {}'.format(
                    self.media_type
                )
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

    def _enrich(self, data, request):
        data = super()._enrich(data, request)
        data['css'] = self._get_css('html_report.css')
        return data

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
        css = self._get_css('pdf_report.css')
        pdf = HTML(string=html).write_pdf(stylesheets=[CSS(string=css)])
        logger.debug("created pdf")
        return pdf
