"""
Dadata API client.
"""

import datetime as dt
import json
from typing import Optional, List, Dict
import requests

CLEANER_URL = "https://cleaner.dadata.ru"
DADATA_URL = "https://dadata.ru"
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
        self.cleaner_url = f"{CLEANER_URL}/api/v1/clean"
        self.dadata_url = f"{DADATA_URL}/api/v2"
        self.suggestions_url = f"{SUGGESTIONS_URL}/suggestions/api/4_1/rs"
        self.session = requests.Session()
        self.session.headers.update(headers)

    def clean(self, name: str, source: str) -> Optional[Dict]:
        """Cleanse `source` as `name` data type."""
        url = f"{self.cleaner_url}/{name}"
        data = [source]
        response = self._post(url, data)
        return response[0] if response else None

    # pylint: disable=too-many-arguments
    def geolocate(
        self,
        name: str,
        lat: float,
        lon: float,
        radius_meters: int = 100,
        count: int = SUGGESTION_COUNT,
        **kwargs,
    ) -> List[Dict]:
        """Find places near given coordinates in given radius."""
        url = f"{self.suggestions_url}/geolocate/{name}"
        data = {"lat": lat, "lon": lon, "radius_meters": radius_meters, "count": count}
        data.update(kwargs)
        response = self._post(url, data)
        return response["suggestions"]

    def iplocate(self, query: str, **kwargs) -> Optional[Dict]:
        """Detect city by IPv4 or IPv6 address."""
        url = f"{self.suggestions_url}/iplocate/address"
        data = {"ip": query}
        data.update(kwargs)
        response = self._get(url, data)
        return response["location"] if "location" in response else None

    def suggest(self, name: str, query: str, count: int = SUGGESTION_COUNT, **kwargs) -> List[Dict]:
        """Suggest from `name` directory according to given `query`."""
        url = f"{self.suggestions_url}/suggest/{name}"
        data = {"query": query, "count": count}
        data.update(kwargs)
        response = self._post(url, data)
        return response["suggestions"]

    def find_by_id(
        self, name: str, query: str, count: int = SUGGESTION_COUNT, **kwargs
    ) -> List[Dict]:
        """Find record in `name` directory by its ID."""
        url = f"{self.suggestions_url}/findById/{name}"
        data = {"query": query, "count": count}
        data.update(kwargs)
        response = self._post(url, data)
        return response["suggestions"]

    def find_affiliated(self, query: str, count: int = SUGGESTION_COUNT, **kwargs) -> List[Dict]:
        """Find affiliated parties by INN."""
        url = f"{self.suggestions_url}/findAffiliated/party"
        data = {"query": query, "count": count}
        data.update(kwargs)
        response = self._post(url, data)
        return response["suggestions"]

    def get_balance(self) -> float:
        """Get account balance."""
        url = f"{self.dadata_url}/profile/balance"
        response = self._get(url, data={})
        return response["balance"]

    def get_daily_stats(self, date: dt.date = None) -> Dict:
        """Get daily service usage stats."""
        url = f"{self.dadata_url}/stat/daily"
        date = date or dt.date.today()
        data = {"date": date.isoformat()}
        response = self._get(url, data)
        return response

    def get_versions(self) -> Dict:
        """Get product and dataset versions."""
        url = f"{self.dadata_url}/version"
        response = self._get(url, data={})
        return response

    def _get(self, url, data, timeout=TIMEOUT_SEC):
        response = self.session.get(url, params=data, timeout=timeout)
        response.raise_for_status()
        return response.json()

    def _post(self, url, data, timeout=TIMEOUT_SEC):
        response = self.session.post(url, data=json.dumps(data), timeout=timeout)
        response.raise_for_status()
        return response.json()
