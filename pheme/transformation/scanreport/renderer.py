# -*- coding: utf-8 -*-
# pheme/transformation/scanreport/renderer.py
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
import logging
from typing import Dict

from base64 import b64encode

from django.core.cache import cache
from django.template import Template, Context
from rest_framework import renderers
from rest_framework.request import Request
from weasyprint import CSS, HTML
from pheme.settings import DEBUG
from pheme.parameter import load_params
from pheme.authentication import get_username_role
from pheme.errors import TemplateNotFoundError

logger = logging.getLogger(__name__)


def _load_template(name: str, params: Dict = None) -> Template:
    if not params:
        params = load_params()
    templ = params.get(name)
    if not templ:
        raise TemplateNotFoundError(name)
    return Template(templ)


def _enrich(name: str, data: Dict, parameter: Dict) -> Dict:
    data["internal_name"] = name
    return {**parameter, **data}


def _get_request(renderer_context: Dict) -> Request:
    renderer_context = renderer_context or {}  # to throw key error
    return renderer_context["request"]


def _default_not_found_response(
    renderer_context: Dict, request: Request
) -> str:
    resp = renderer_context["response"]
    resp.status_code = 404
    # pylint: disable=W0212
    path = request._request.path
    report_id = path[path.rfind("/") + 1 :]
    return '"not data found for %s"' % report_id


class Report(renderers.BaseRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        request = _get_request(renderer_context)
        if not data:
            return _default_not_found_response(renderer_context, request)

        name = data.get("internal_name")
        cache_key = "{}/{}".format(self.media_type, name) if name else None
        logger.debug("generating report %s", cache_key)

        if cache_key and not DEBUG:
            cached = cache.get(cache_key)
            if cached:
                return cached
        params = load_params()
        # separate user specific parameter
        user_parameter = params.pop("user_specific", {})
        username, _ = get_username_role(request)
        if username:
            params = {**params, **user_parameter.get(username, {})}

        result = self.apply(name, data, params)
        if cache_key:
            cache.set(cache_key, result)
        return result

    def apply(self, name: str, data: Dict, parameter: Dict):
        raise NotImplementedError(
            "Report class requires .apply() to be implemented"
        )


class VulnerabilityHTMLReport(Report):
    __template = "vulnerability_report_html_template"
    __css_template = "vulnerability_report_html_css"
    media_type = "text/html"
    format = "html"

    def apply(self, name: str, data: Dict, parameter: Dict):
        css = _load_template(self.__css_template, parameter).render(
            Context(parameter)
        )
        data["css"] = css

        return _load_template(self.__template).render(
            Context(_enrich(name, data, parameter))
        )


def _replace_inline_svg_with_img_tags(
    html: str, from_index: int = 0, open_tag="<svg ", close_tag="</svg>"
) -> str:
    """
    Is a workaround because WeasyPrint is not capable of dealing with inline svg

    It searches for svg tags and replaces the inline svg within a given
    html document with img containing a base64 encoded data link.

    It is known that we lose the css styling with that hack, but in the moment
    it is considered better than losing the image altogether or trying to
    produce the images before rendering the template.

    Please replace this method as soon as possible with a proper solution.
    """
    # abort condition is when either open_tag or close_tag was not found
    while True:
        from_index = html.find(open_tag, from_index)
        if from_index == -1:
            return html
        to_index = html.find(close_tag, from_index + len(open_tag))
        if to_index == -1:
            return html
        to_index += len(close_tag)
        to_encode = html[from_index:to_index]
        encoded = b64encode(to_encode.encode()).decode()
        img = (
            '<img src="data:image/svg+xml;charset=utf-8;base64, {}" />'.format(
                encoded
            )
        )
        html = html[:from_index] + img + html[to_index:]
        from_index = to_index


class VulnerabilityPDFReport(Report):
    """
    Is used to generate vulnerability reports in PDF.
    It renders html and css templates given data struct and then translate
    the html document to PDF
    """

    __template = "vulnerability_report_pdf_template"
    __css_template = "vulnerability_report_pdf_css"
    media_type = "application/pdf"
    format = "binary"

    def apply(self, name: str, data: Dict, parameter: Dict):
        logger.debug("got template: %s", self.__template)
        css = _load_template(self.__css_template, parameter).render(
            Context(parameter)
        )
        html_template = _load_template(self.__template)
        html = html_template.render(Context(_enrich(name, data, parameter)))
        html = _replace_inline_svg_with_img_tags(html)
        logger.debug("created html")
        pdf = HTML(string=html).write_pdf(stylesheets=[CSS(string=css)])
        logger.debug("created pdf")
        return pdf


class ReportFormatHTMLReport(renderers.BaseRenderer):
    media_type = "text/html+report_format_editor"
    format = "html"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        request = _get_request(renderer_context)
        if not data:
            return _default_not_found_response(renderer_context, request)
        template = Template(data["template"])
        data["vulnerability_report"]["css"] = data["html_css"]
        data["vulnerability_report"]["images"] = data.get("images")
        context = Context(data["vulnerability_report"])
        html = template.render(context)
        logger.debug("created html")
        return html


class ReportFormatPDFReport(renderers.BaseRenderer):
    media_type = "application/pdf+report_format_editor"
    format = "binary"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        request = _get_request(renderer_context)
        if not data:
            return _default_not_found_response(renderer_context, request)
        data["vulnerability_report"]["images"] = data.get("images")
        template = Template(data["template"])
        context = Context(data["vulnerability_report"])
        html = template.render(context)
        logger.debug("created html")
        css = Template(data["pdf_css"]).render(context)
        pdf = HTML(string=html).write_pdf(stylesheets=[CSS(string=css)])
        logger.debug("created pdf")
        return pdf
