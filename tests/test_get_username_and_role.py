from unittest.mock import patch
from pheme.authentication import get_username_role

GSAD_FAKE_RESPONSE = """
<envelope>
    <version>21.04.0~git-96347f1-master</version>
    <vendor_version>docker-companion</vendor_version>
    <token>e93d3012-14f9-4bd0-aeff-3a70e3bd132c</token>
    <time>Mon Nov 2 12:03:43 2020 UTC</time>
    <timezone>UTC</timezone>
    <login>admin</login>
    <session>1604319495</session>
    <role>Admin</role>
    <i18n>en_US</i18n>
    <client_address>172.19.0.9</client_address>
    <backend_operation>0.02</backend_operation>
    <get_users>
        <get_users_response status="200" status_text="OK">
            <user id="10aa5b90-d42e-4442-8589-490002dea087">
                <owner>
                    <name></name>
                </owner>
                <name>admin</name>
                <comment></comment>
                <creation_time>2020-10-30T10:08:09Z</creation_time>
                <modification_time>
                2020-10-30T10:08:09Z</modification_time>
                <writable>1</writable>
                <in_use>0</in_use>
                <permissions>
                    <permission>
                        <name>get_users</name>
                    </permission>
                </permissions>
                <hosts allow="0"></hosts>
                <sources>
                    <source>file</source>
                </sources>
                <ifaces allow="0"></ifaces>
                <role id="7a8cb5b4-b74d-11e2-8187-406186ea4fc5">
                    <name>Admin</name>
                </role>
                <groups></groups>
            </user>
            <filters id="0">
                <term>first=1 rows=10 sort=name</term>
                <keywords>
                    <keyword>
                        <column>first</column>
                        <relation>=</relation>
                        <value>1</value>
                    </keyword>
                    <keyword>
                        <column>rows</column>
                        <relation>=</relation>
                        <value>10</value>
                    </keyword>
                    <keyword>
                        <column>sort</column>
                        <relation>=</relation>
                        <value>name</value>
                    </keyword>
                </keywords>
            </filters>
            <sort>
                <field>name
                <order>ascending</order></field>
            </sort>
            <users start="1" max="1000" />
            <user_count>1
            <filtered>1</filtered>
            <page>1</page></user_count>
        </get_users_response>
    </get_users>
</envelope>
"""


@patch("rest_framework.request.HttpRequest")
@patch("requests.models.Response")
def test_get_username_and_role(request, response):
    # pylint: disable=W0613
    def fake_get(url, params, **kwargs):
        response.text = GSAD_FAKE_RESPONSE
        return response

    request.query_params = dict(token="TOKEN")
    request.COOKIES = dict(GSAD_SID="GSAD_SID")
    username, role = get_username_role(request, get=fake_get)
    assert username == "admin"
    assert role == "Admin"


@patch("rest_framework.request.HttpRequest")
def test_return_none_on_missing_url(request):
    username, role = get_username_role(request, gsad_url=None)
    assert username is None
    assert role is None


@patch("rest_framework.request.HttpRequest")
def test_not_call_on_missing_token_gsadsid(request):
    def fake_get(url, params, **kwargs):
        raise Exception("should not be called")

    request.query_params = {}
    request.COOKIES = {}
    username, role = get_username_role(request, get=fake_get)
    assert username is None
    assert role is None
