![Greenbone Logo](https://www.greenbone.net/wp-content/uploads/gb_logo_resilience_horizontal.png)

# Pheme - Greenbone Static Report Generator <!-- omit in toc -->

**pheme** is a service to create scan reports. It is maintained by [Greenbone Networks].

[Pheme](https://en.wikipedia.org/wiki/Pheme) is the personification of fame and renown.

Or in this case personification of a service to generate reports.

## Table of Contents <!-- omit in toc -->

- [Installation](#installation)
  - [Requirements](#requirements)
- [Development](#development)
- [Maintainer](#maintainer)
- [Contributing](#contributing)
- [License](#license)

## Installation

### Requirements

Python 3.7 and later is supported.

## Development

**pheme** uses [poetry] for its own dependency management and build
process.

First install poetry via pip

    python3 -m pip install --user poetry

Afterwards run

    poetry install

in the checkout directory of **pheme** (the directory containing the
`pyproject.toml` file) to install all dependencies including the packages only
required for development.

Afterwards activate the git hooks for auto-formatting and linting via
[autohooks].

    poetry run autohooks activate

Validate the activated git hooks by running

    poetry run autohooks check

## API overview

To get an overview of the API you can start this project

```
python manage.py runserver
```

and then go to [swagger](http://localhost:8000/docs/)


## Maintainer

This project is maintained by [Greenbone Networks GmbH][Greenbone Networks]

## Contributing

Your contributions are highly appreciated. Please
[create a pull request](https://github.com/greenbone/pheme/pulls)
on GitHub. Bigger changes need to be discussed with the development team via the
[issues section at GitHub](https://github.com/greenbone/pheme/issues)
first.

## License

Copyright (C) 2020 [Greenbone Networks GmbH][Greenbone Networks]

Licensed under the [GNU General Public License v3.0 or later](LICENSE).

[Greenbone Networks]: https://www.greenbone.net/
[poetry]: https://python-poetry.org/
[autohooks]: https://github.com/greenbone/autohooks
