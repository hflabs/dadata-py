# Dadata API Client

> Data cleansing, enrichment and suggestions via [Dadata API](https://dadata.ru/api)

[![PyPI Version][pypi-image]][pypi-url]
[![Build Status][build-image]][build-url]
[![Code Coverage][coverage-image]][coverage-url]
[![Code Quality][quality-image]][quality-url]

Thin Python wrapper over Dadata API.

**Only a stub for now**.

## Installation

```sh
pip install dadata
```

## Usage

```python
>>> import os
>>> import dadata
>>> token = os.getenv("DADATA_API_KEY")
>>> secret = os.getenv("DADATA_SECRET_KEY")
>>> dadata = Dadata(token, secret)
>>> dadata.clean("address", "мск сухонская 11 89")
```

## Development setup

```sh
$ pip install black coverage flake8 mypy pylint pytest tox
$ tox
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Make sure to add or update tests as appropriate.

Use [Black](https://black.readthedocs.io/en/stable/) for code formatting and [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0-beta.4/) for commit messages.

## [Changelog](CHANGELOG.md)

## License

[MIT](https://choosealicense.com/licenses/mit/)

<!-- Markdown link & img dfn's -->

[pypi-image]: https://img.shields.io/pypi/v/dadata?style=flat-square
[pypi-url]: https://pypi.org/project/dadata/
[build-image]: https://img.shields.io/travis/nalgeon/dadata-py?style=flat-square
[build-url]: https://travis-ci.org/nalgeon/dadata-py
[coverage-image]: https://img.shields.io/coveralls/github/nalgeon/dadata-py?style=flat-square
[coverage-url]: https://coveralls.io/github/nalgeon/dadata-py
[quality-image]: https://img.shields.io/codeclimate/maintainability/nalgeon/dadata-py?style=flat-square
[quality-url]: https://codeclimate.com/github/nalgeon/dadata-py
