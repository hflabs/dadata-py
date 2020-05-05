"""
Dadata API client.
"""

import json
from typing import Optional
import requests

CLEANER_URL = "https://cleaner.dadata.ru"
SUGGESTIONS_URL = "https://suggestions.dadata.ru"
TIMEOUT_SEC = 3
SUGGESTION_COUNT = 10


class Dadata:
    """Dadata API client"""

    def __init__(self, token: str, secret: str = None):
        headers = {
            "Content-type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Token {token}",
        }
        if secret:
            headers["X-Secret"] = secret
        self.cleaner_url = CLEANER_URL
        self.suggestions_url = SUGGESTIONS_URL
        self.session = requests.Session()
        self.session.headers.update(headers)

    def clean(self, name: str, source: str) -> Optional[dict]:
        """Cleanse `source` as `name` data type."""
        url = f"{self.cleaner_url}/api/v1/clean/{name}"
        data = [source]
        response = self._post(url, data)
        return response[0] if response else None

    def geolocate(
        self, lat: float, lon: float, radius_meters: int = 100, count: int = SUGGESTION_COUNT
    ) -> list:
        """Find places near given coordinates in given radius."""
        url = f"{self.suggestions_url}/suggestions/api/4_1/rs/geolocate/address"
        data = {"lat": lat, "lon": lon, "radius_meters": radius_meters, "count": count}
        response = self._post(url, data)
        return response["suggestions"]

    def iplocate(self, query: str) -> Optional[dict]:
        """Detect city by IPv4 or IPv6 address."""
        url = f"{self.suggestions_url}/suggestions/api/4_1/rs/iplocate/address"
        data = {"ip": query}
        response = self._get(url, data)
        return response["location"] if "location" in response else None

    def suggest(self, name, query, count=SUGGESTION_COUNT, params=None):
        """Suggest from `name` directory according to given `query`."""
        url = f"{self.suggestions_url}/suggestions/api/4_1/rs/suggest/{name}"
        data = {"query": query, "count": count}
        if params:
            data.update(params)
        response = self._post(url, data)
        return response["suggestions"]

    def find_by_id(self, name: str, query: str, count: int = SUGGESTION_COUNT) -> list:
        """Find record in `name` directory by its ID."""
        url = f"{self.suggestions_url}/suggestions/api/4_1/rs/findById/{name}"
        data = {"query": query, "count": count}
        response = self._post(url, data)
        return response["suggestions"]

    def find_affiliated(self, query: str, count: int = SUGGESTION_COUNT) -> list:
        """Find affiliated parties by INN."""
        url = f"{self.suggestions_url}/suggestions/api/4_1/rs/findAffiliated/party"
        data = {"query": query, "count": count}
        response = self._post(url, data)
        return response["suggestions"]

    def _get(self, url, data, timeout=TIMEOUT_SEC):
        response = self.session.get(url, params=data, timeout=timeout)
        response.raise_for_status()
        return response.json()

    def _post(self, url, data, timeout=TIMEOUT_SEC):
        response = self.session.post(url, data=json.dumps(data), timeout=timeout)
        response.raise_for_status()
        return response.json()
