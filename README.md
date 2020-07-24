# Dadata API Client

> Data cleansing, enrichment and suggestions via [Dadata API](https://dadata.ru/api)

[![PyPI Version][pypi-image]][pypi-url]
[![Build Status][build-image]][build-url]
[![Code Coverage][coverage-image]][coverage-url]
[![Code Quality][quality-image]][quality-url]

Thin Python wrapper over Dadata API.

## Installation

```sh
pip install dadata
```

Requirements:

- Python 3.7+
- [httpx](https://pypi.org/project/httpx/)

## Usage

Create API client instance:

```python
>>> from dadata import DadataAsync
>>> token = "Replace with Dadata API key"
>>> secret = "Replace with Dadata secret key"
>>> await dadata = Dadata(token, secret)
```

Then call API methods as specified below.

Examples use async client (`DadataAsync`), but there is also a sync one (`Dadata`) with the same features.

## Postal Address

### [Validate and cleanse address](https://dadata.ru/api/clean/address/)

```python
>>> await dadata.clean(name="address", source="мск сухонская 11 89")
{
    'source': 'мск сухонская 11 89',
    'result': 'г Москва, ул Сухонская, д 11, кв 89',
    'postal_code': '127642',
    'country': 'Россия',
    'region': 'Москва',
    'city_area': 'Северо-восточный',
    'city_district': 'Северное Медведково',
    'street': 'Сухонская',
    'house': '11',
    'flat': '89',
    'flat_area': '34.6',
    'flat_price': '6854710',
    'fias_id': '5ee84ac0-eb9a-4b42-b814-2f5f7c27c255',
    'timezone': 'UTC+3',
    'geo_lat': '55.8782557',
    'geo_lon': '37.65372',
    'qc_geo': 0,
    'qc': 0,
    'metro': [ ... ],
    ...
}
```

### [Geocode address](https://dadata.ru/api/geocode/)

Same API method as "validate and cleanse":

```python
>>> await dadata.clean(name="address", source="москва сухонская 11")
{
    'source': 'мск сухонская 11 89',
    'result': 'г Москва, ул Сухонская, д 11, кв 89',
    ...
    'geo_lat': '55.8782557',
    'geo_lon': '37.65372',
    'beltway_hit': 'IN_MKAD',
    'beltway_distance': None,
    'qc_geo': 0,
    ...
}
```

### [Reverse geocode address](https://dadata.ru/api/geolocate/)

```python
>>> await dadata.geolocate(name="address", lat=55.878, lon=37.653)
[
    { 'value': 'г Москва, ул Сухонская, д 11', ... },
    { 'value': 'г Москва, ул Сухонская, д 11А', ... },
    { 'value': 'г Москва, ул Сухонская, д 13', ... },
    ...
]
```

### [GeoIP city](https://dadata.ru/api/iplocate/)

```python
>>> await dadata.iplocate("46.226.227.20")
{
    'value': 'г Краснодар',
    'unrestricted_value': '350000, Краснодарский край, г Краснодар',
    'data': { ... }
}
```

### [Autocomplete (suggest) address](https://dadata.ru/api/suggest/address/)

```python
>>> await dadata.suggest(name="address", query="самара метал")
[
    { 'value': 'г Самара, пр-кт Металлургов', ... },
    { 'value': 'г Самара, ул Металлистов', ... },
    { 'value': 'г Самара, поселок Зубчаниновка, ул Металлургическая', ... },
    ...
]
```

Show suggestions in English:

```python
>>> await dadata.suggest(name="address", query="samara metal", language="en")
[
    { 'value': 'Russia, gorod Samara, prospekt Metallurgov', ... },
    { 'value': 'Russia, gorod Samara, ulitsa Metallistov', ... },
    { 'value': 'Russia, gorod Samara, poselok Zubchaninovka, ulitsa Metallurgicheskaya', ... },
    ...
]
```

Constrain by city (Yuzhno-Sakhalinsk):

```python
>>> locations = [{ "kladr_id": "6500000100000" }]
>>> await dadata.suggest(name="address", query="Ватутина", locations=locations)
[
    {'value': 'г Южно-Сахалинск, ул Ватутина' ... }
]
```

Constrain by specific geo point and radius (in Vologda city):

```python
>>> geo = [{ "lat": 59.244634,  "lon": 39.913355, "radius_meters": 200 }]
>>> await dadata.suggest(name="address", query="сухонская", locations_geo=geo)
[
    {'value': 'г Вологда, ул Сухонская' ... }
]
```

Boost city to top (Toliatti):

```python
>>> boost = [{ "kladr_id": "6300000700000" }]
>>> await dadata.suggest(name="address", query="авто", locations_boost=boost)
[
    {'value': 'Самарская обл, г Тольятти, Автозаводское шоссе' ... },
    {'value': 'Самарская обл, г Тольятти, ул Автомобилистов' ... },
    {'value': 'Самарская обл, г Тольятти, ул Автостроителей' ... },
    ...
]
```

### [Find address by FIAS ID](https://dadata.ru/api/find-address/)

```python
>>> await dadata.find_by_id(name="address", query="9120b43f-2fae-4838-a144-85e43c2bfb29")
[
    { 'value': 'г Москва, ул Снежная', ... }
]
```

Find by KLADR ID:

```python
>>> await dadata.find_by_id(name="address", query="77000000000268400")
```

### [Suggest postal office](https://dadata.ru/api/suggest/postal_unit/)

```python
>>> await dadata.suggest(name="postal_unit", query="дежнева 2а")
[
    {
        'value': '127642',
        'unrestricted_value': 'г Москва, проезд Дежнёва, д 2А',
        'data': { ... }
    }
]
```

### [Find postal office by code](https://dadata.ru/api/suggest/postal_unit/)

```python
>>> await dadata.find_by_id(name="postal_unit", query="127642")
[
    {
        'value': '127642',
        'unrestricted_value': 'г Москва, проезд Дежнёва, д 2А',
        'data': { ... }
    }
]
```

### [Find nearest postal office](https://dadata.ru/api/suggest/postal_unit/)

```python
>>> await dadata.geolocate(name="postal_unit", lat=55.878, lon=37.653, radius_meters=1000)
[
    {
        'value': '127642',
        'unrestricted_value': 'г Москва, проезд Дежнёва, д 2А',
        'data': { ... }
    }
]
```

### [Get City ID for delivery services](https://dadata.ru/api/delivery/)

```python
>>> await dadata.find_by_id(name="delivery", query="3100400100000")
[
    {
        'value': '3100400100000',
        'unrestricted_value': 'fe7eea4a-875a-4235-aa61-81c2a37a0440',
        'data': {
            ...
            'boxberry_id': '01929',
            'cdek_id': '344',
            'dpd_id': '196006461'
        }
    }
]
```

### [Get address strictly according to FIAS](https://dadata.ru/api/find-fias/)

```python
>>> await dadata.find_by_id(name="fias", query="9120b43f-2fae-4838-a144-85e43c2bfb29")
[
    { 'value': 'г Москва, ул Снежная', ... }
]
```

### [Suggest country](https://dadata.ru/api/suggest/country/)

```python
>>> await dadata.suggest(name="country", query="та")
[
    { 'value': 'Таджикистан', ... },
    { 'value': 'Таиланд', ... },
    { 'value': 'Тайвань', ... },
    ...
]
```

## Company or individual enterpreneur

## [Find company by INN](https://dadata.ru/api/find-party/)

```python
>>> await dadata.find_by_id(name="party", query="7707083893")
[
    {
        'value': 'ПАО СБЕРБАНК',
        'unrestricted_value': 'ПАО СБЕРБАНК',
        'data': {
            'inn': '7707083893',
            'kpp': '773601001',
            ...
        }
    },
    ...
]
```

Find by INN and KPP:

```python
>>> await dadata.find_by_id(name="party", query="7707083893", kpp="540602001")
[
    {
        'value': 'СИБИРСКИЙ БАНК ПАО СБЕРБАНК',
        'unrestricted_value': 'СИБИРСКИЙ БАНК ПАО СБЕРБАНК',
        'data': {
            'inn': '7707083893',
            'kpp': '540602001',
            ...
        }
    }
]
```

### [Suggest company](https://dadata.ru/api/suggest/party/)

```python
>>> await dadata.suggest(name="party", query="сбер")
[
    { 'value': 'ПАО СБЕРБАНК', ... },
    { 'value': 'АО "СБЕРБРОКЕР"', ... },
    { 'value': 'АО "СБЕРИНВЕСТКАПИТАЛ"', ... },
    ...
]
```

Constrain by specific regions (Saint Petersburg and Leningradskaya oblast):

```python
>>> locations = [{ "kladr_id": "7800000000000" }, { "kladr_id": "4700000000000"}]
>>> await dadata.suggest(name="party", query="сбер", locations=locations)
```

Constrain by active companies:

```python
>>> await dadata.suggest(name="party", query="сбер", status=["ACTIVE"])
```

Constrain by individual entrepreneurs:

```python
>>> await dadata.suggest(name="party", query="сбер", type="INDIVIDUAL")
```

Constrain by head companies, no branches:

```python
>>> await dadata.suggest(name="party", query="сбер", branch_type=["MAIN"])
```

### [Find affiliated companies](https://dadata.ru/api/find-affiliated/)

```python
>>> await dadata.find_affiliated("7736207543")
[
    { 'value': 'ООО "ДЗЕН.ПЛАТФОРМА"', ... },
    { 'value': 'ООО "ЕДАДИЛ"', ... },
    { 'value': 'ООО "ЗНАНИЕ"', ... },
    ...
]
```

Search only by manager INN:

```python
>>> await dadata.find_affiliated("773006366201", scope=["MANAGERS"])
[
    { 'value': 'ООО "ЯНДЕКС"', ... },
    { 'value': 'МФ "ФОИ"', ... },
    { 'value': 'АНО ДПО "ШАД"', ... },
]
```

## Bank

### [Find bank by BIC, SWIFT or INN](https://dadata.ru/api/find-bank/)

```python
>>> await dadata.find_by_id(name="bank", query="044525225")
[
    {
        'value': 'ПАО Сбербанк',
        'unrestricted_value': 'ПАО Сбербанк',
        'data': {
            'bic': '044525225',
            'swift': 'SABRRUMM',
            'inn': '7707083893',
            ...
        }
    }
]
```

Find by SWIFT code:

```python
>>> await dadata.find_by_id(name="bank", query="SABRRUMM")
```

Find by INN:

```python
>>> await dadata.find_by_id(name="bank", query="7728168971")
```

Find by INN and KPP:

```python
>>> await dadata.find_by_id(name="bank", query="7728168971", kpp="667102002")
```

Find by registration number:

```python
>>> await dadata.find_by_id(name="bank", query="1481")
```

### [Suggest bank](https://dadata.ru/api/suggest/bank/)

```python
>>> await dadata.suggest(name="bank", query="ти")
[
    { 'value': 'АО «Тимер Банк»', ... },
    { 'value': 'АО «Тинькофф Банк»', ... },
    { 'value': '«Азиатско-Тихоокеанский Банк» (ПАО)', ... },
    ...
]
```

## Personal name

### [Validate and cleanse name](https://dadata.ru/api/clean/name/)

```python
>>> await dadata.clean(name="name", source="Срегей владимерович иванов")
{
    'source': 'Срегей владимерович иванов',
    'result': 'Иванов Сергей Владимирович',
    ...
    'surname': 'Иванов',
    'name': 'Сергей',
    'patronymic': 'Владимирович',
    'gender': 'М',
    'qc': 1
}
```

### [Suggest name](https://dadata.ru/api/suggest/name/)

```python
>>> await dadata.suggest(name="fio", query="викт")
[
    { 'value': 'Виктор', ... },
    { 'value': 'Виктория', ... },
    { 'value': 'Викторова', ... },
    ...
]
```

Suggest female first name:

```python
>>> await dadata.suggest(name="fio", query="викт", parts=["NAME"], gender="FEMALE")
[
    { 'value': 'Виктория', ... },
    { 'value': 'Викторина', ... }
]
```

## Phone

### [Validate and cleanse phone](https://dadata.ru/api/clean/phone/)

```python
>>> await dadata.clean(name="phone", source="9168-233-454")
{
    'source': '9168-233-454',
    'type': 'Мобильный',
    'phone': '+7 916 823-34-54',
    'provider': 'ПАО "Мобильные ТелеСистемы"',
    'country': 'Россия',
    'region': 'Москва и Московская область',
    'timezone': 'UTC+3',
    'qc': 0,
    ...
}
```

## Passport

### [Validate passport](https://dadata.ru/api/clean/passport/)

```python
>>> await dadata.clean(name="passport", source="4509 235857")
{
    'source': '4509 235857',
    'series': '45 09',
    'number': '235857',
    'qc': 0
}
```

### [Suggest issued by](https://dadata.ru/api/suggest/fms_unit/)

```python
>>> await dadata.suggest(name="fms_unit", query="772 053")
[
    { 'value': 'ОВД ЗЮЗИНО Г. МОСКВЫ', ... },
    { 'value': 'ОВД РАЙОНА ЗЮЗИНО УВД ЮГО-ЗАО Г. МОСКВЫ', ... },
    { 'value': 'ПАСПОРТНО-ВИЗОВЫМ ОТДЕЛЕНИЕМ ОВД РАЙОНА ЗЮЗИНО Г. МОСКВЫ', ... },
    ...
]
```

## Email

### [Validate email](https://dadata.ru/api/clean/email/)

```python
>>> await dadata.clean(name="email", source="serega@yandex/ru")
{
    'source': 'serega@yandex/ru',
    'email': 'serega@yandex.ru',
    'local': 'serega',
    'domain': 'yandex.ru',
    'type': 'PERSONAL',
    'qc': 4
}
```

### [Suggest email](https://dadata.ru/api/suggest/email/)

```python
>>> await dadata.suggest(name="email", query="maria@")
[
    { 'value': 'maria@mail.ru', ... },
    { 'value': 'maria@gmail.com', ... },
    { 'value': 'maria@yandex.ru', ... },
    ...
]
```

## Other datasets

### [Tax office](https://dadata.ru/api/suggest/fns_unit/)

```python
>>> await dadata.find_by_id(name="fns_unit", query="5257")
[
    {
        'value': 'Инспекция ФНС России по Канавинскому району г.Нижнего Новгорода',
        'unrestricted_value': 'Инспекция ФНС России по Канавинскому району г.Нижнего Новгорода',
        'data': {
            'code': '5257'
            'oktmo': '22701000',
            'inn': '5257046101',
            'kpp': '525701001',
            ...
        }
    }
]
```

### [Regional court](https://dadata.ru/api/suggest/region_court/)

```python
>>> await dadata.suggest(name="region_court", query="таганско")
[
    { 'value': 'Судебный участок № 371 Таганского судебного района г. Москвы', ... },
    { 'value': 'Судебный участок № 372 Таганского судебного района г. Москвы', ... },
    { 'value': 'Судебный участок № 373 Таганского судебного района г. Москвы', ... },
    ...
]
```

### [Metro station](https://dadata.ru/api/suggest/metro/)

```python
>>> await dadata.suggest(name="metro", query="алек")
[
    { 'value': 'Александровский сад', ... },
    { 'value': 'Алексеевская', ... },
    { 'value': 'Площадь Александра Невского 1', ... },
    ...
]
```

Constrain by city (Saint Petersburg):

```python
>>> filters = [{ "city": "Санкт-Петербург" }]
>>> await dadata.suggest(name="metro", query="алек", filters=filters)
[
    { 'value': 'Площадь Александра Невского 1', ... },
    { 'value': 'Площадь Александра Невского 2', ... }
]
```

### [Car brand](https://dadata.ru/api/suggest/car_brand/)

```python
>>> await dadata.suggest(name="car_brand", query="фо")
[
    { 'value': 'Volkswagen', ... },
    { 'value': 'Ford', ... },
    { 'value': 'Foton', ... }
]
```

### [Currency](https://dadata.ru/api/suggest/currency/)

```python
>>> await dadata.suggest(name="currency", query="руб")
[
    { 'value': 'Белорусский рубль', ... },
    { 'value': 'Российский рубль', ... }
]
```

### [OKVED 2](https://dadata.ru/api/suggest/okved2/)

```python
>>> await dadata.suggest(name="okved2", query="космических")
[
    { 'value': 'Производство космических аппаратов (в том числе спутников), ракет-носителей', ... },
    { 'value': 'Производство автоматических космических аппаратов', ... },
    { 'value': 'Деятельность космических лабораторий', ... },
    ...
]
```

### [OKPD 2](https://dadata.ru/api/suggest/okpd2/)

```python
>>> await dadata.suggest(name="okpd2", query="калоши")
[
    { 'value': 'Услуги по обрезинованию валенок (рыбацкие калоши)', ... }
]
```

## Development setup

```sh
$ python3 -m venv env
$ . env/bin/activate
$ make deps
$ tox
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Make sure to add or update tests as appropriate.

Use [Black](https://black.readthedocs.io/en/stable/) for code formatting and [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0-beta.4/) for commit messages.

## [Changelog](CHANGELOG.md)

This library uses [CalVer](https://calver.org/) with YY.MM.MICRO schema. See changelog for details specific to each release.

## License

[MIT](https://choosealicense.com/licenses/mit/)

<!-- Markdown link & img dfn's -->

[pypi-image]: https://img.shields.io/pypi/v/dadata?style=flat-square
[pypi-url]: https://pypi.org/project/dadata/
[build-image]: https://img.shields.io/travis/hflabs/dadata-py?style=flat-square
[build-url]: https://travis-ci.org/hflabs/dadata-py
[coverage-image]: https://img.shields.io/coveralls/github/hflabs/dadata-py?style=flat-square
[coverage-url]: https://coveralls.io/github/hflabs/dadata-py
[quality-image]: https://img.shields.io/codeclimate/maintainability/hflabs/dadata-py?style=flat-square
[quality-url]: https://codeclimate.com/github/hflabs/dadata-py
