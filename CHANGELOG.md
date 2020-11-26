# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- nvt threat information in host result [114](https://github.com/greenbone/pheme/pull/114)
### Changed
- remove pandas due to too old debian version [112](https://github.com/greenbone/pheme/pull/112)
- add workaround for svg in pdf with wasyprint [120](https://github.com/greenbone/pheme/pull/120)

### Deprecated
### Removed
- libsass support: https://sass-lang.com/blog/libsass-is-deprecated [111](https://github.com/greenbone/pheme/pull/111)
- equipment treemap [112](https://github.com/greenbone/pheme/pull/112)
### Fixed

[Unreleased]: https://github.com/greenbone/pheme/compare/v0.0.1a3...HEAD


## [0.0.1a3] - 2020-11-06
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
- add distribution chart possibility [#33](https://github.com/greenbone/pheme/pull/45/)
- create a markdown table description of scanreport model [#37](https://github.com/greenbone/pheme/pull/37/)
```
curl -H 'accept: text/markdown+table' localhost:8000/scanreport/data/description
```
- Report Format Editor [#51](https://github.com/greenbone/pheme/pull/51)
```
http://localhost:8000/static/report_format_editor.html
```
- overridable design parameter [55](https://github.com/greenbone/pheme/pull/55)
- add possibility to not include overview information to remove charts and redundant information [63](https://github.com/greenbone/pheme/pull/63)
```
curl 'http://localhost:8000/report/$ID_OF_PREVIOUS_POST?without_overview=TRUE' -H 'Accept: text/csv'
```
- add xml response [63](https://github.com/greenbone/pheme/pull/63)
```
curl 'http://localhost:8000/report/$ID_OF_PREVIOUS_POST' -H 'Accept: application/xml'
```
- add csv response [63](https://github.com/greenbone/pheme/pull/63)
```
curl 'http://localhost:8000/report/$ID_OF_PREVIOUS_POST' -H 'Accept: text/csv'
```
- `pheme-create-parameter-json` to create `parameter.json` based on a directory ( `pheme-create-parameter-json $SOURCE_PATH > $TARGET_PATH/parameter.json` )
- possibility to have user specific changes [98](https://github.com/greenbone/pheme/pull/98)
[0.0.1a3]: https://github.com/greenbone/pheme/compare/v0.0.1a2...HEAD

## [0.0.1a2] - 2020-08-14
### Added
- django webserver
- openapi (/openapi-schema/)
- swagger (/docs/) 

[gvmd]: https://github.com/greenbone/gvmd
