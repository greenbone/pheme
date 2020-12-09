from unittest.mock import patch, MagicMock
import pathlib
import http.client
import pytest

from pheme.scripts import parameter

_client_mock = MagicMock(spec=http.client)

_connection_mock = MagicMock(spec=http.client.HTTPSConnection)
_response_mock = MagicMock(spec=http.client.HTTPResponse)
_pathmock = MagicMock(spec=pathlib)
_path_mock = MagicMock(spec=pathlib.Path)


@patch("pheme.scripts.parameter.http.client", new=_client_mock)
@patch("pheme.scripts.parameter.pathlib", new=_pathmock)
@pytest.mark.parametrize(
    "args",
    [
        ("main_color", "#ccc"),
        ("logo", "/tmp/logo.png"),
        ("background", "/tmp/bg.svg"),
    ],
)
def test_upload(args):
    key, val = args
    _path_mock.name = val
    _path_mock.read_bytes.return_value = b""
    _pathmock.Path.return_value = _path_mock
    _response_mock.status = 200
    _response_mock.read.return_value = b'{}'
    _client_mock.HTTPSConnection.return_value = _connection_mock
    _connection_mock.getresponse.return_value = _response_mock
    parameter.PHEME_URL = "https://localhost:8000/pheme"
    _, result = parameter.main(["--key", key, "--value", val])
    assert result == {}


@patch("pheme.scripts.parameter.http.client", new=_client_mock)
@patch("pheme.scripts.parameter.pathlib", new=_pathmock)
def test_fail_unsupported_mimetype():
    _path_mock.name = "/tmp/shiny.css"
    _path_mock.read_bytes.return_value = b""
    _pathmock.Path.return_value = _path_mock
    parameter.PHEME_URL = "https://localhost:8000/pheme"
    with pytest.raises(ValueError):
        parameter.main(["--key", "logo", "--value", "/tmp/shiny.css"])


@patch("pheme.scripts.parameter.http.client", new=_client_mock)
def test_fail_on_wrong_status_code():
    _response_mock.status = 403
    _response_mock.read.return_value = b'{}'
    _client_mock.HTTPSConnection.return_value = _connection_mock
    _connection_mock.getresponse.return_value = _response_mock
    parameter.PHEME_URL = "http://localhost:8000/pheme"
    with pytest.raises(ValueError):
        parameter.main(["--key", "main_color", "--value", "#000"])


def test_fail_unknown_key():
    with pytest.raises(ValueError):
        parameter.main(["--key", "pdf_template", "--value", "<html></html>"])
