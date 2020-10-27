import urllib
import base64


def as_datalink(data: bytes, file_format: str) -> str:
    img = urllib.parse.quote(base64.b64encode(data))
    return 'data:{};base64,{}'.format(file_format, img)
