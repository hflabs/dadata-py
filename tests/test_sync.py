"""
Tests for synchronous Dadata API client.
"""

import datetime as dt
from unittest import mock
import httpx
import pytest
from pytest_httpx import HTTPXMock
from dadata.sync import CleanClient, DadataClient, ProfileClient, SuggestClient

dadata = DadataClient(token="token", secret="secret")


def test_init_cleaner():
    cleaner = CleanClient(token="token", secret="secret")
    assert cleaner._client.headers["Authorization"] == "Token token"
    assert cleaner._client.headers["X-Secret"] == "secret"


def test_init_suggester():
    suggester = SuggestClient(token="token")
    assert suggester._client.headers["Authorization"] == "Token token"
    suggester = SuggestClient(token="token", secret="secret")
    assert suggester._client.headers["Authorization"] == "Token token"
    assert suggester._client.headers["X-Secret"] == "secret"


def test_init_profile():
    profile = ProfileClient(token="token", secret="secret")
    assert profile._client.headers["Authorization"] == "Token token"
    assert profile._client.headers["X-Secret"] == "secret"


def test_timeout(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{SuggestClient.BASE_URL}suggest/address",
        json={"suggestions": []},
    )
    dadata = DadataClient(token="token", timeout=5)
    dadata.suggest(name="address", query="samara")
    request = httpx_mock.get_request()
    assert request.extensions["timeout"] == {
        "connect": 5.0,
        "pool": 5.0,
        "read": 5.0,
        "write": 5.0,
    }


def test_clean(httpx_mock: HTTPXMock):
    expected = {"source": "Сережа", "result": "Сергей", "qc": 1}
    httpx_mock.add_response(method="POST", url=f"{CleanClient.BASE_URL}clean/name", json=[expected])
    actual = dadata.clean(name="name", source="Сережа")
    assert actual == expected


def test_clean_record(httpx_mock: HTTPXMock):
    structure = ["AS_IS", "AS_IS", "AS_IS"]
    record = ["1", "2", "3"]
    expected = [{"source": "1"}, {"source": "2"}, {"source": "3"}]
    response = {"structure": structure, "data": [expected]}
    httpx_mock.add_response(method="POST", url=f"{CleanClient.BASE_URL}clean", json=response)
    actual = dadata.clean_record(structure=structure, record=record)
    assert actual == expected


def test_geolocate(httpx_mock: HTTPXMock):
    expected = [
        {"value": "г Москва, ул Сухонская, д 11", "data": {"kladr_id": "7700000000028360004"}}
    ]
    httpx_mock.add_response(
        method="POST",
        url=f"{SuggestClient.BASE_URL}geolocate/address",
        json={"suggestions": expected},
    )
    actual = dadata.geolocate(name="address", lat=55.8782557, lon=37.65372)
    assert actual == expected


def test_geolocate_request(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{SuggestClient.BASE_URL}geolocate/address",
        json={"suggestions": []},
    )
    dadata.geolocate(name="address", lat=55.8782557, lon=37.65372, radius_meters=200, count=5)
    body = b'{"lat":55.8782557,"lon":37.65372,"radius_meters":200,"count":5}'
    request = httpx_mock.get_request()
    assert request.read() == body


def test_geolocate_not_found(httpx_mock: HTTPXMock):
    expected = []
    httpx_mock.add_response(
        method="POST",
        url=f"{SuggestClient.BASE_URL}geolocate/address",
        json={"suggestions": expected},
    )
    actual = dadata.geolocate(name="address", lat=1, lon=1)
    assert actual == expected


def test_iplocate(httpx_mock: HTTPXMock):
    expected = {"value": "г Москва", "data": {"kladr_id": "7700000000000"}}
    httpx_mock.add_response(
        method="GET",
        url=f"{SuggestClient.BASE_URL}iplocate/address?ip=212.45.30.108",
        json={"location": expected},
    )
    actual = dadata.iplocate("212.45.30.108")
    assert actual == expected


def test_iplocate_not_found(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=f"{SuggestClient.BASE_URL}iplocate/address?ip=1.1.1.1",
        json={"location": None},
    )
    actual = dadata.iplocate("1.1.1.1")
    assert actual is None


def test_suggest(httpx_mock: HTTPXMock):
    expected = [
        {"value": "г Москва, ул Сухонская", "data": {"kladr_id": "77000000000283600"}},
        {"value": "г Москва, ул Сухонская, д 1", "data": {"kladr_id": "7700000000028360009"}},
    ]
    httpx_mock.add_response(
        method="POST",
        url=f"{SuggestClient.BASE_URL}suggest/address",
        json={"suggestions": expected},
    )
    actual = dadata.suggest(name="address", query="мск сухонская")
    assert actual == expected


def test_suggest_request(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{SuggestClient.BASE_URL}suggest/address",
        json={"suggestions": []},
    )
    dadata.suggest(name="address", query="samara", to_bound={"value": "city"})
    body = b'{"query":"samara","count":10,"to_bound":{"value":"city"}}'
    request = httpx_mock.get_request()
    assert request.read() == body


def test_suggest_not_found(httpx_mock: HTTPXMock):
    expected = []
    httpx_mock.add_response(
        method="POST",
        url=f"{SuggestClient.BASE_URL}suggest/address",
        json={"suggestions": expected},
    )
    actual = dadata.suggest(name="address", query="whatever")
    assert actual == expected


def test_find_by_id(httpx_mock: HTTPXMock):
    expected = [{"value": "ООО МОТОРИКА", "data": {"inn": "7719402047"}}]
    httpx_mock.add_response(
        method="POST", url=f"{SuggestClient.BASE_URL}findById/party", json={"suggestions": expected}
    )
    actual = dadata.find_by_id(name="party", query="7719402047")
    assert actual == expected


def test_find_by_id_request(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{SuggestClient.BASE_URL}findById/party",
        json={"suggestions": []},
    )
    dadata.find_by_id(name="party", query="7719402047", count=5)
    body = b'{"query":"7719402047","count":5}'
    request = httpx_mock.get_request()
    assert request.read() == body


def test_find_by_id_not_found(httpx_mock: HTTPXMock):
    expected = []
    httpx_mock.add_response(
        method="POST", url=f"{SuggestClient.BASE_URL}findById/party", json={"suggestions": expected}
    )
    actual = dadata.find_by_id(name="party", query="1234567890")
    assert actual == expected


def test_find_by_email(httpx_mock: HTTPXMock):
    expected = [{"value": "info@dadata.ru", "data": {"company": {"inn": "7721581040"}}}]
    httpx_mock.add_response(
        method="POST",
        url=f"{SuggestClient.BASE_URL}findByEmail/company",
        json={"suggestions": expected},
    )
    actual = dadata.find_by_email(name="company", query="info@dadata.ru")
    assert actual == expected


def test_find_by_email_request(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{SuggestClient.BASE_URL}findByEmail/company",
        json={"suggestions": []},
    )
    dadata.find_by_email(name="company", query="info@dadata.ru", count=5)
    body = b'{"query":"info@dadata.ru","count":5}'
    request = httpx_mock.get_request()
    assert request.read() == body


def test_find_by_email_not_found(httpx_mock: HTTPXMock):
    expected = []
    httpx_mock.add_response(
        method="POST",
        url=f"{SuggestClient.BASE_URL}findByEmail/company",
        json={"suggestions": expected},
    )
    actual = dadata.find_by_email(name="company", query="info@dadata.ru")
    assert actual == expected


def test_find_affiliated(httpx_mock: HTTPXMock):
    expected = [
        {"value": "ООО ДЗЕН.ПЛАТФОРМА", "data": {"inn": "7704431373"}},
        {"value": "ООО ЕДАДИЛ", "data": {"inn": "7728237907"}},
    ]
    httpx_mock.add_response(
        method="POST",
        url=f"{SuggestClient.BASE_URL}findAffiliated/party",
        json={"suggestions": expected},
    )
    actual = dadata.find_affiliated("7736207543")
    assert actual == expected


def test_find_affiliated_request(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{SuggestClient.BASE_URL}findAffiliated/party",
        json={"suggestions": []},
    )
    dadata.find_affiliated("7736207543", count=5)
    body = b'{"query":"7736207543","count":5}'
    request = httpx_mock.get_request()
    assert request.read() == body


def test_find_affiliated_not_found(httpx_mock: HTTPXMock):
    expected = []
    httpx_mock.add_response(
        method="POST",
        url=f"{SuggestClient.BASE_URL}findAffiliated/party",
        json={"suggestions": expected},
    )
    actual = dadata.find_affiliated("1234567890")
    assert actual == expected


def test_get_balance(httpx_mock: HTTPXMock):
    response = {"balance": 9922.30}
    httpx_mock.add_response(
        method="GET", url=f"{ProfileClient.BASE_URL}profile/balance", json=response
    )
    actual = dadata.get_balance()
    assert actual == 9922.30


def test_get_daily_stats(httpx_mock: HTTPXMock):
    today_str = dt.date.today().isoformat()
    response = {"date": today_str, "services": {"merging": 0, "suggestions": 11, "clean": 1004}}
    httpx_mock.add_response(method="GET", url=f"{ProfileClient.BASE_URL}stat/daily", json=response)
    actual = dadata.get_daily_stats()
    assert actual == response


def test_get_daily_stats_date(httpx_mock: HTTPXMock):
    date = dt.date(2024, 5, 28)
    date_str = date.isoformat()
    response = {"date": date_str, "services": {"merging": 0, "suggestions": 11, "clean": 1004}}
    httpx_mock.add_response(
        method="GET", url=f"{ProfileClient.BASE_URL}stat/daily?date={date_str}", json=response
    )
    actual = dadata.get_daily_stats(date=date)
    assert actual == response


def test_get_versions(httpx_mock: HTTPXMock):
    response = {
        "dadata": {"version": "17.1 (5995:3d7b54a78838)"},
        "suggestions": {"version": "16.10 (5a2e47f29553)", "resources": {"ЕГРЮЛ": "13.01.2017"}},
        "factor": {"version": "8.0 (90780)", "resources": {"ФИАС": "30.01.2017"}},
    }
    httpx_mock.add_response(method="GET", url=f"{ProfileClient.BASE_URL}version", json=response)
    actual = dadata.get_versions()
    assert actual == response


@mock.patch("dadata.sync.ProfileClient", autospec=True)
@mock.patch("dadata.sync.SuggestClient", autospec=True)
@mock.patch("dadata.sync.CleanClient", autospec=True)
def test_context_manager(mock_clean, mock_suggest, mock_profile):
    with DadataClient("token", "secret") as client:
        client.get_versions()
    mock_clean.return_value.close.assert_called_once()
    mock_suggest.return_value.close.assert_called_once()
    mock_profile.return_value.close.assert_called_once()


@mock.patch("dadata.sync.httpx.Client", autospec=True)
def test_client_base_context_manager(mock_client):
    with CleanClient("token", "secret") as client:
        client.clean(name="name", source="source")
    mock_client.return_value.close.assert_called_once()


def test_request_failed(httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=504)
    with pytest.raises(httpx.HTTPError):
        dadata.clean(name="name", source="Сережа")
