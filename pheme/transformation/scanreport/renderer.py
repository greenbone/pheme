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
import pdfkit

logger = logging.getLogger(__name__)


class DetailScanReport(renderers.BaseRenderer):
    def _template_based_on_request(self, request: HttpRequest) -> str:
        return (
            'host_detailed_report.html'
            if request.GET.get('grouping') == 'host'
            else 'nvt_detailed_report.html'
        )

    def _enrich(self, data: Dict) -> Dict:
        data['logo'] = settings.TEMPLATE_LOGO_ADDRESS
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
        return loader.get_template(template).render(self._enrich(data))


class DetailScanPDFReport(DetailScanReport):
    media_type = 'application/pdf'
    format = 'binary'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        logger.debug("generating html template")
        renderer_context = renderer_context or {}  # to throw key error
        request = renderer_context['request']
        template = self._template_based_on_request(request)
        html = loader.get_template(template).render(self._enrich(data))
        logger.debug("created html")
        # workaround for https://github.com/wkhtmltopdf/wkhtmltopdf/issues/4460
        pdf = pdfkit.from_string(
            html, False, options={'enable-local-file-access': None}
        )
        logger.debug("created pdf")
        return pdf
