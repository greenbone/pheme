"""pheme URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf.urls import url
from django.urls import path
from django.views.generic import TemplateView
from rest_framework.schemas import get_schema_view
import pheme.version
import pheme.views

urlpatterns = [
    path('template/', pheme.views.template),
    path('report/', pheme.views.report),
    url(
        r'^openapi-schema',
        get_schema_view(
            title="Pheme",
            description="static report generation",
            version=pheme.version.__version__,
            public=True,
        ),
        name='openapi-schema',
    ),
    path(
        'docs/',
        TemplateView.as_view(
            template_name='swagger-ui.html',
            extra_context={'schema_url': 'openapi-schema'},
        ),
    ),
]
