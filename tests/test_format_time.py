from django.urls import reverse
from rest_framework.test import APIClient

from pheme.settings import SECRET_KEY
from tests.test_report_generation import http_accept_helper


def test_format_time_within_template():
    subtype = "html"
    css_key = f"vulnerability_report_{subtype}_css"
    template_key = f"vulnerability_report_{subtype}_template"
    client = APIClient()
    url = reverse(
        "put_parameter",
    )
    render_charts = """
    {% load readable_timeformat %}
    <html>
    {{ start | format_time }}
    {{ unknown_key | format_time }}
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
    response = http_accept_helper("text/html")
    assert response.status_code == 200
    html_report = response.getvalue().decode("utf-8")
    assert "Mon, Jan 01, 2018 12 AM UTC+01:00" in html_report
