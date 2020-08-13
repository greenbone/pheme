import pytest

from pheme.parser.xml import XMLParser


@pytest.mark.parametrize("xml", ['<data a="b"/>', '<data><a>b</a></data>',])
def test_parsing(xml):
    under_test = XMLParser()
    result = under_test.parse(xml)
    assert result == {'data': {'a': 'b'}}
