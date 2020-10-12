from unittest.mock import patch
from rest_framework.test import APIClient
from rest_framework.reverse import reverse
from pheme.settings import SECRET_KEY


def test_unauthorized_on_missing_x_api_key():
    client = APIClient()
    url = reverse(
        'put_value_parameters',
        kwargs={"key": "main_color"},
    )
    response = client.put(url, data="#66c430", format='json')
    assert response.status_code == 403
    url = reverse('put_file_parameter')
    response = client.put(url, data={})
    assert response.status_code == 403


@patch('django.core.files.uploadedfile.UploadedFile')
def test_put_image(upload_file):
    client = APIClient()
    url = reverse(
        'put_file_parameter',
    )
    # api_key = request.META.get('HTTP_X_API_KEY', "")
    response = client.put(
        url,
        data={"main_color": "#66c430", "cover_image": upload_file},
        HTTP_X_API_KEY=SECRET_KEY,
    )
    assert response.status_code == 200


def test_put_main_color():
    client = APIClient()
    url = reverse(
        'put_value_parameters',
        kwargs={"key": "main_color"},
    )
    # api_key = request.META.get('HTTP_X_API_KEY', "")
    response = client.put(
        url, data="#66c430", format='json', HTTP_X_API_KEY=SECRET_KEY
    )
    assert response.status_code == 200
