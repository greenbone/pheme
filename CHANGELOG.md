# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- XMLParser (pheme/parser/xml.py) [#5](https://github.com/greenbone/pheme/pull/5)
- transformation for [gvmd] scan results to host grouped template data [#5](https://github.com/greenbone/pheme/pull/5)
```
curl -X POST\
    'http://localhost:8000/transform'\
     -H 'Content-Type: application/xml'\
     -H 'Accept: application/json; indent=2'\
     -d @path_to/scanreport.xml
```
- report generation for pdf [#24](https://github.com/greenbone/pheme/pull/24)

```
curl 'http://localhost:8000/report/$ID_OF_PREVIOUS_POST' -H 'Accept: application/pdf'
```
- report generation for html [#24](https://github.com/greenbone/pheme/pull/24)

```
curl 'http://localhost:8000/report/$ID_OF_PREVIOUS_POST' -H 'Accept: text/html'
```
- rudimentary chart support [#30](https://github.com/greenbone/pheme/pull/30)
- endpoint to get the xml as json [#30](https://github.com/greenbone/pheme/pull/30)

```
curl -X POST 'http://localhost:8000/unmodified'\
     -H 'Content-Type: application/xml'\
     -H 'Accept: application/json'\
     -d @path_to/scanreport.xml
```
- add stack bar chart possibility
### Changed
### Deprecated
### Removed
### Fixed

[Unreleased]: https://github.com/greenbone/pheme/compare/v0.0.1a2...HEAD


## [0.0.1a2] - 2020-08-14
### Added
- django webserver
- openapi (/openapi-schema/)
- swagger (/docs/) 

[gvmd]: https://github.com/greenbone/gvmd
