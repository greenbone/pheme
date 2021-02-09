# -*- coding: utf-8 -*-
# pheme/urls.py
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

from django.urls import path
import pheme.version
import pheme.views
import pheme.parameter

urlpatterns = [
    path(
        'parameter/<str:key>',
        pheme.parameter.put_value,
        name='put_value_parameters',
    ),
    path(
        'parameter',
        pheme.parameter.put,
        name='put_parameter',
    ),
    path('cache/<str:key>', pheme.views.load_cache, name='load_cache'),
    path('cache', pheme.views.store_cache, name='store_cache'),
    path('unmodified', pheme.views.unmodified, name='unmodified'),
    path('transform', pheme.views.transform, name='transform'),
    path('transform/', pheme.views.transform),
    path(
        'scanreport/data/description',
        pheme.views.scanreport_data_description,
        name='scanreport_data_description',
    ),
    path('report/<str:name>', pheme.views.report, name='report'),
    path(
        'template/elements/<str:name>',
        pheme.views.template_elements,
        name='template_elements',
    ),
]
