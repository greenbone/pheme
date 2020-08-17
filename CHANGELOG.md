# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- XMLParser (pheme/parser/xml.py)
- transformation for [gvmd] scan results to host grouped template data
```
curl -X POST\
    'http://localhost:8000/template/?grouping=host'\
     -H 'Content-Type: application/xml'\
     -H 'Accept: application/json; indent=2'\
     -d @path_to/scanreport.xml
```
- transformation for [gvmd] scan results to nvt grouped template data 
```
curl -X POST\
    'http://localhost:8000/template/?grouping=nvt'\
     -H 'Content-Type: application/xml'\
     -H 'Accept: application/json; indent=2'\
     -d @path_to/scanreport.xml
```
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

[GVMD]: https://github.com/greenbone/gvmd
