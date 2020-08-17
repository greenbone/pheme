"""
Provides XML parsing support.

Although there is the project djangorestframework-xml xmltodict seems to be more
reliable for our usecase.

"""
from typing import Any, Dict, Tuple
from rest_framework.parsers import BaseParser
import xmltodict


class XMLParser(BaseParser):
    """
    XML parser based on xmltodict.
    """

    media_type = "application/xml"

    def parse(self, stream, media_type=None, parser_context=None):
        return xmltodict.parse(stream, postprocessor=normalize_keys)


def normalize_keys(_: str, key: str, value: any) -> Tuple[str, Any]:
    """
    Due to expat some keys may have values like '@' or '#' as a
    first character.

    This method is used in a postprocessor for xmltodict to remove starting non
    alpha character in keys.
    """

    def normalize_dict_keys(data: Dict) -> Dict:
        return dict(
            (
                k if k[0].isalpha() else k[1:],
                normalize_dict_keys(v) if isinstance(v, dict) else v,
            )
            for k, v in data.items()
        )

    normalized_value = (
        normalize_dict_keys(value) if isinstance(value, dict) else value
    )
    if key[0].isalpha():
        return (key, normalized_value)
    return (
        key[1:],
        normalized_value,
    )
