import urllib
import base64
from pathlib import Path


def as_datalink(data: bytes, file_format: str) -> str:
    img = urllib.parse.quote(base64.b64encode(data))
    return 'data:image/{};base64,{}'.format(file_format, img)


def filename_as_datalink(filename: str, data: bytes) -> str:
    file_format = filename.split('.')[-1]
    if file_format == 'svg':
        file_format += '+xml'
    return as_datalink(data, file_format)


def filepath_as_datalink(location: str) -> str:
    return filename_as_datalink(location, Path(location).read_bytes())
