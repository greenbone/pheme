.. role:: raw-html-m2r(raw)
   :format: html



.. image:: https://www.greenbone.net/wp-content/uploads/gb_logo_resilience_horizontal.png
   :target: https://www.greenbone.net/wp-content/uploads/gb_logo_resilience_horizontal.png
   :alt: Greenbone Logo


Pheme - Greenbone Static Report Generator :raw-html-m2r:`<!-- omit in toc -->`
==================================================================================

**pheme** is a service to create scan reports. It is maintained by `Greenbone Networks <https://www.greenbone.net/>`_.

`Pheme <https://en.wikipedia.org/wiki/Pheme>`_ is the personification of fame and renown.

Or in this case personification of a service to generate reports.

Table of Contents :raw-html-m2r:`<!-- omit in toc -->`
----------------------------------------------------------


* `Installation <#installation>`_

  * `Requirements <#requirements>`_

* `Development <#development>`_
* `API overview <#api-overview>`_
* `Maintainer <#maintainer>`_
* `Contributing <#contributing>`_
* `License <#license>`_

Installation
------------

Requirements
^^^^^^^^^^^^

Python 3.7 and later is supported.

Besides python ``pheme`` also needs to have


* libcairo2-dev
* pango1.0

installed.

Development
-----------

**pheme** uses `poetry <https://python-poetry.org/>`_ for its own dependency management and build
process.

First install poetry via pip

.. code-block::

   python3 -m pip install --user poetry


Afterwards run

.. code-block::

   poetry install


in the checkout directory of **pheme** (the directory containing the
``pyproject.toml`` file) to install all dependencies including the packages only
required for development.

Afterwards activate the git hooks for auto-formatting and linting via
`autohooks <https://github.com/greenbone/autohooks>`_.

.. code-block::

   poetry run autohooks activate


Validate the activated git hooks by running

.. code-block::

   poetry run autohooks check


API overview
------------

To get an overview of the API you can start this project

.. code-block::

   poetry run python manage.py runserver

and then go to `swagger <http://localhost:8000/docs/>`_

Usage
-----

In order to prepare the data structure the XML report data needs to be posted to ``pheme`` with a grouping indicator (either by host or nvt).

E.g.:

.. code-block::

   > curl -X POST 'http://localhost:8000/transform?grouping=nvt'\
       -H 'Content-Type: application/xml'\
       -H 'Accept: application/json'\
       -d @test_data/longer_report.xml

     "scanreport-nvt-9a233b0d-713c-4f22-9e15-f6e5090873e3"⏎

The returned identifier can be used to generate the actual report. 

So far a report can be either in:


* application/json
* application/xml
* text/csv
  E.g.

.. code-block::

   > curl -v 'http://localhost:8000/report/scanreport-nvt-9a233b0d-713c-4f22-9e15-f6e5090873e3' -H 'Accept: application/csv'

For visual report like


* application/pdf
* text/html

the corresponding css and html template needs to be put into pheme first:

.. code-block::

   > curl -X PUT localhost:8000/parameter\
       -H 'x-api-key: SECRET_KEY_missing_using_default_not_suitable_in_production'\
       --form vulnerability_report_html_css=@path_to_css_template\
       --form vulnerability_report_pdf_css=@path_to_css_template\
       --form vulnerability_report=@path_to_html_template

afterwards it can be get as usual:

.. code-block::

   > curl -v 'http://localhost:8000/report/scanreport-nvt-9a233b0d-713c-4f22-9e15-f6e5090873e3' -H 'Accept: application/pdf'

Maintainer
----------

This project is maintained by `Greenbone Networks GmbH <https://www.greenbone.net/>`_

Contributing
------------

Your contributions are highly appreciated. Please
`create a pull request <https://github.com/greenbone/pheme/pulls>`_
on GitHub. Bigger changes need to be discussed with the development team via the
`issues section at GitHub <https://github.com/greenbone/pheme/issues>`_
first.

License
-------

Copyright (C) 2020 `Greenbone Networks GmbH <https://www.greenbone.net/>`_

Licensed under the `GNU Affero General Public License v3.0 or later <LICENSE>`_.
