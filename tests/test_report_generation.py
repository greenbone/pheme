# -*- coding: utf-8 -*-
# tests/test_report_generation.py
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

from unittest.mock import patch
from typing import List, Optional
import pytest
from django.core.cache import cache
from django.urls import reverse
from rest_framework.test import APIClient

from pheme.datalink import as_datalink
from pheme.settings import SECRET_KEY
from pheme.transformation.scanreport import renderer

from tests.generate_test_data import gen_report


def generate(
    prefix: str, amount: int, number: Optional[int] = None
) -> List[str]:
    return [
        f"{prefix}_{number if number is not None else i}" for i in range(amount)
    ]


def test_report_contains_equipment():
    client = APIClient()
    url = reverse("transform")
    report = {
        "report": {
            "report": gen_report(generate("host", 10), generate("oid", 5))
        }
    }
    response = client.post(url, data=report, format="xml")
    assert response.status_code == 200
    result = cache.get(response.data)
    assert result["results"][0]["equipment"]["os"] == "rusty rust rust"
    assert result["results"][0]["equipment"]["ports"] is not None


def test_report_contains_charts():
    client = APIClient()
    url = reverse("transform")
    report = {
        "report": {
            "report": gen_report(generate("host", 10), generate("oid", 5))
        }
    }
    response = client.post(url, data=report, format="xml")
    assert response.status_code == 200
    result = cache.get(response.data)
    assert result["overview"] is not None
    assert result["overview"]["hosts"] is not None
    assert result["overview"]["nvts"] is not None
    # assert result['overview']['vulnerable_equipment'] is not None


@pytest.mark.parametrize(
    "html_contains",
    [
        ('<svg width="343"><g id="severity_arrows">', "svg"),  # missing end tag
        ('<svg width="343"><g id="severity_arrows"></svg>', "img"),  # replaced
        ('<div width="343"><g id="severity_arrows"></div>', "div"),  # not svg
    ],
)
def test_workaround_for_inline_svg_and_weasyprint(html_contains):
    # pylint: disable=W0212
    html, contains = html_contains
    result = renderer._replace_inline_svg_with_img_tags(html)
    assert contains in result


def test_dynamic_template():
    subtype = "html"
    css_key = f"vulnerability_report_{subtype}_css"
    template_key = f"vulnerability_report_{subtype}_template"
    client = APIClient()
    url = reverse(
        "put_parameter",
    )
    nvts_template = """
    <h1>{{ High }}</h1>
    """
    render_charts = """
    {% load dynamic_template %}
    <html>
    {{ overview.nvts | dynamic_template:"nvts_template" }}
    </html>
    """
    response = client.put(
        url,
        data={
            css_key: "html { background: #000; }",
            "nvts_template": nvts_template,
            template_key: render_charts,
        },
        HTTP_X_API_KEY=SECRET_KEY,
    )
    assert response.status_code == 200
    response = test_http_accept("text/html")
    nvts = response.data["overview"]["nvts"]
    html_report = response.getvalue().decode("utf-8")
    assert f"<h1>{nvts['High']}</h1>" in html_report


def test_charts_generation_on_zero_severity_report():
    report = gen_report(
        generate("host", 10),
        generate("oid", 10, 0),
        name="http_accept_test",
    )
    test_chart_keyword(report)


def test_charts_generation_on_zero_result_report():
    report = gen_report(
        generate("host", 0),
        generate("oid", 0),
        name="http_accept_test",
    )
    test_chart_keyword(report, 1)


def test_chart_keyword(report=None, expected=4):
    subtype = "html"
    css_key = f"vulnerability_report_{subtype}_css"
    template_key = f"vulnerability_report_{subtype}_template"
    client = APIClient()
    url = reverse(
        "put_parameter",
    )
    render_charts = """
    {% load charts %}
    <html>
    {{ overview.nvts | pie_chart}}
    {{ overview.hosts | h_bar_chart  }}
    {% h_bar_chart overview.hosts x_title="Vulnerabilitites" %}
    {{ overview.hosts | treemap  }}
    </html>
    """
    response = client.put(
        url,
        data={
            css_key: "html { background: #000; }",
            template_key: render_charts,
        },
        HTTP_X_API_KEY=SECRET_KEY,
    )
    assert response.status_code == 200
    response = test_http_accept("text/html", report)
    html_report = response.getvalue().decode("utf-8")
    assert html_report.count("<svg ") == expected


@pytest.mark.parametrize(
    "http_accept",
    [
        "application/pdf",
        "text/html",
    ],
)
def test_http_accept_visual(http_accept):
    subtype = http_accept.split("/")[-1]
    css_key = f"vulnerability_report_{subtype}_css"
    template_key = f"vulnerability_report_{subtype}_template"
    client = APIClient()
    url = reverse(
        "put_parameter",
    )
    render_charts = """
    {% load charts %}
    <html>
    {{ overview.nvts | pie_chart}}
    {{ overview.hosts | h_bar_chart  }}
    {{ overview.hosts | treemap  }}
    </html>
    """
    response = client.put(
        url,
        data={
            css_key: "html { background: #000; }",
            template_key: render_charts,
        },
        HTTP_X_API_KEY=SECRET_KEY,
    )
    assert response.status_code == 200
    test_http_accept(http_accept)


@pytest.mark.parametrize(
    "http_accept",
    [
        "application/json",
        "application/xml",
        "text/csv",
    ],
)
def test_http_accept(
    http_accept,
    report=None,
):
    if not report:
        report = gen_report(
            generate("host", 1),
            generate("oid", 1),
            name="http_accept_test",
        )
    url = reverse("transform")
    report = {"report": {"report": report}}
    client = APIClient()
    response = client.post(url, data=report, format="xml")
    assert response.status_code == 200
    key = response.data
    report_url = reverse("report", kwargs={"name": key})
    html_report = client.get(report_url, HTTP_ACCEPT=http_accept)
    assert html_report.status_code == 200
    return html_report


def test_generate_format_editor_html_report():
    def upload(key, data):
        cache_url = reverse("store_cache")
        to_send = {"key": key, "value": data}
        response = APIClient().post(cache_url, data=to_send, format="json")
        assert response.status_code == 200

    def upload_image(key, name, content):
        cache_url = reverse("store_cache")
        to_send = {
            "key": key,
            "value": {
                "name": name,
                "content": content,
            },
            "append": True,
        }
        response = APIClient().post(
            cache_url + "?append_image=true", data=to_send, format="json"
        )
        assert response.status_code == 200

    images = [
        as_datalink("p1".encode(), "png"),
        as_datalink("p2".encode(), "jpg"),
    ]
    client = APIClient()
    url = reverse("transform")
    report = {
        "report": {
            "report": gen_report(
                generate("host", 10),
                generate("oid", 5),
                name="report_format_editor_test",
            )
        }
    }
    response = client.post(url, data=report, format="xml")
    assert response.status_code == 200
    key = response.data
    report_url = reverse("report", kwargs={"name": key})
    html_template = """
        <html>
            <head>
                <style>{{ css }}</style>
            </head>
            <body>
            <p>{{ name }}</p>
            <img src="{{ images.0 }}"/>
            <img src="{{ images.1 }}"/>
            </body>
            </html>
        """
    html_css = "body { background-color: #000; }"
    for i, content in enumerate(images):
        upload_image(f"{key}images", str(i), content)
    upload(f"{key}html_template", html_template)
    upload(f"{key}html_css", html_css)
    # upload(images)
    html_report = client.get(
        report_url, HTTP_ACCEPT="text/html+report_format_editor"
    )
    assert html_report.status_code == 200
    report = str(html_report.getvalue())
    assert "report_format_editor_test" in report
    assert "background-color: #000" in report
    for content in images:
        assert f'<img src="{content}"/>' in report


@patch("pheme.parameter.pheme.authentication.get_username_role")
def test_html_report_contains_user_paramater(user_information):
    user_information.side_effect = [(None, None), ("test", "admin")]
    subtype = "html"
    css_key = f"vulnerability_report_{subtype}_css"
    template_key = f"vulnerability_report_{subtype}_template"
    client = APIClient()
    url = reverse(
        "put_parameter",
    )
    html_template = "<html><body><p>{{ main_color }}</p></body></html>" ""
    response = client.put(
        url,
        data={
            css_key: "html { background: {{ main_color }}; }",
            template_key: html_template,
            "main_color": "#fff",
        },
        HTTP_X_API_KEY=SECRET_KEY,
    )
    assert response.status_code == 200
    assert response.data["main_color"]
    client = APIClient()
    url = reverse(
        "put_value_parameters",
        kwargs={"key": "main_color"},
    )
    response = client.put(url, data="#000", format="json")
    assert response.status_code == 200
    assert response.data["user_specific"]["test"]["main_color"] == "#000"
    report_response = test_http_accept("text/html")
    html_report = report_response.getvalue().decode("utf-8")
    assert html_report == "<html><body><p>#fff</p></body></html>"
