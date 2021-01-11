# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
### Changed
### Deprecated
### Removed
### Fixed

[Unreleased]: https://github.com/greenbone/pheme/compare/v21.04-rc2...HEAD


## [21.04-rc2] - 2021-01-11
### Changed
- settings to default to GOS settings [153](https://github.com/greenbone/pheme/pull/153)
- KeyError to TemplateNotFoundError [155](https://github.com/greenbone/pheme/pull/155)
- move get_user_role to authentication [155](https://github.com/greenbone/pheme/pull/155)
### Removed
- parameter script [156](https://github.com/greenbone/pheme/pull/156)
### Fixed
- division by zero when a report does not contain results [154](https://github.com/greenbone/pheme/pull/154)

[21.04-rc2]: https://github.com/greenbone/pheme/compare/v21.04-rc1...v21.04-rc2

## [21.04-rc1] - 2020-12-10
### Added
- nvt threat information in host result [114](https://github.com/greenbone/pheme/pull/114)
- nvt severity information in host result [121](https://github.com/greenbone/pheme/pull/121)
- treemap as svg [128](https://github.com/greenbone/pheme/pull/128)
- dynamic template functionality [139](https://github.com/greenbone/pheme/pull/139/files)
### Changed
- remove pandas due to too old debian version [112](https://github.com/greenbone/pheme/pull/112)
- add workaround for svg in pdf with wasyprint [120](https://github.com/greenbone/pheme/pull/120)
- charts are not produced in the data struct but within a template [122](https://github.com/greenbone/pheme/pull/122)

### Removed
- libsass support: https://sass-lang.com/blog/libsass-is-deprecated [111](https://github.com/greenbone/pheme/pull/111)
- equipment treemap [112](https://github.com/greenbone/pheme/pull/112)
- openapi [127](https://github.com/greenbone/pheme/pull/127)
[21.04-rc1]: https://github.com/greenbone/pheme/compare/v0.0.1a3...HEAD

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
