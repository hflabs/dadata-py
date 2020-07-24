"""
Synchronous Dadata API client.
"""

import datetime as dt
import json
from typing import Dict, List, Optional
import httpx
from dadata import settings


class ClientBase:
    """Base class for API client"""

    def __init__(self, base_url: str, token: str, secret: str = None):
        headers = {
            "Content-type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Token {token}",
        }
        if secret:
            headers["X-Secret"] = secret
        self._client = httpx.Client(base_url=base_url, headers=headers)

    def __enter__(self) -> "ClientBase":
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        """Close network connections"""
        self._client.close()

    def _get(self, url, data, timeout=settings.TIMEOUT_SEC):
        """GET request to Dadata API"""
        response = self._client.get(url, params=data, timeout=timeout)
        response.raise_for_status()
        return response.json()

    def _post(self, url, data, timeout=settings.TIMEOUT_SEC):
        """POST request to Dadata API"""
        response = self._client.post(url, data=json.dumps(data), timeout=timeout)
        response.raise_for_status()
        return response.json()


class CleanClient(ClientBase):
    """Dadata Cleaner API client"""

    BASE_URL = "https://cleaner.dadata.ru/api/v1/"

    def __init__(self, token: str, secret: str = None):
        super().__init__(base_url=self.BASE_URL, token=token, secret=secret)

    def clean(self, name: str, source: str) -> Optional[Dict]:
        """Cleanse `source` as `name` data type."""
        url = f"clean/{name}"
        data = [source]
        response = self._post(url, data)
        return response[0] if response else None

    def clean_record(self, structure: List[str], record: List[str]) -> List[Dict]:
        """Cleanse `record` of specified `structure`."""
        url = "clean"
        data = {"structure": structure, "data": [record]}
        response = self._post(url, data)
        return response["data"][0] if response else None


class SuggestClient(ClientBase):
    """Dadata Suggestions API client"""

    BASE_URL = "https://suggestions.dadata.ru/suggestions/api/4_1/rs/"

    def __init__(self, token: str):
        super().__init__(base_url=self.BASE_URL, token=token)

    def geolocate(
        self, name: str, lat: float, lon: float, radius_meters: int = 100, **kwargs
    ) -> List[Dict]:
        """Find places near given coordinates in given radius."""
        url = f"geolocate/{name}"
        data = {"lat": lat, "lon": lon, "radius_meters": radius_meters}
        data.update(kwargs)
        response = self._post(url, data)
        return response["suggestions"]

    def iplocate(self, query: str, **kwargs) -> Optional[Dict]:
        """Detect city by IPv4 or IPv6 address."""
        url = "iplocate/address"
        data = {"ip": query}
        data.update(kwargs)
        response = self._get(url, data)
        return response["location"] if "location" in response else None

    def suggest(
        self, name: str, query: str, count: int = settings.SUGGESTION_COUNT, **kwargs
    ) -> List[Dict]:
        """Suggest from `name` directory according to given `query`."""
        url = f"suggest/{name}"
        data = {"query": query, "count": count}
        data.update(kwargs)
        response = self._post(url, data)
        return response["suggestions"]

    def find_by_id(
        self, name: str, query: str, count: int = settings.SUGGESTION_COUNT, **kwargs
    ) -> List[Dict]:
        """Find record in `name` directory by its ID."""
        url = f"findById/{name}"
        data = {"query": query, "count": count}
        data.update(kwargs)
        response = self._post(url, data)
        return response["suggestions"]

    def find_affiliated(
        self, query: str, count: int = settings.SUGGESTION_COUNT, **kwargs
    ) -> List[Dict]:
        """Find affiliated parties by INN."""
        url = "findAffiliated/party"
        data = {"query": query, "count": count}
        data.update(kwargs)
        response = self._post(url, data)
        return response["suggestions"]


class ProfileClient(ClientBase):
    """Dadata Profile API client"""

    BASE_URL = "https://dadata.ru/api/v2/"

    def __init__(self, token: str, secret: str = None):
        super().__init__(base_url=self.BASE_URL, token=token, secret=secret)

    def get_balance(self) -> float:
        """Get account balance."""
        url = "profile/balance"
        response = self._get(url, data={})
        return response["balance"]

    def get_daily_stats(self, date: dt.date = None) -> Dict:
        """Get daily service usage stats."""
        url = "stat/daily"
        date = date or dt.date.today()
        data = {"date": date.isoformat()}
        response = self._get(url, data)
        return response

    def get_versions(self) -> Dict:
        """Get product and dataset versions."""
        url = "version"
        response = self._get(url, data={})
        return response


class DadataClient:
    """Synchronous Dadata API client"""

    def __init__(self, token: str, secret: str = None):
        self._cleaner = CleanClient(token=token, secret=secret)
        self._suggestions = SuggestClient(token=token)
        self._profile = ProfileClient(token=token, secret=secret)

    def clean(self, name: str, source: str) -> Optional[Dict]:
        """Cleanse `source` as `name` data type."""
        return self._cleaner.clean(name=name, source=source)

    def clean_record(self, structure: List[str], record: List[str]) -> List[Dict]:
        """Cleanse `record` of specified `structure`."""
        return self._cleaner.clean_record(structure=structure, record=record)

    def geolocate(
        self, name: str, lat: float, lon: float, radius_meters: int = 100, **kwargs
    ) -> List[Dict]:
        """Find places near given coordinates in given radius."""
        return self._suggestions.geolocate(
            name=name, lat=lat, lon=lon, radius_meters=radius_meters, **kwargs
        )

    def iplocate(self, query: str, **kwargs) -> Optional[Dict]:
        """Detect city by IPv4 or IPv6 address."""
        return self._suggestions.iplocate(query=query, **kwargs)

    def suggest(
        self, name: str, query: str, count: int = settings.SUGGESTION_COUNT, **kwargs
    ) -> List[Dict]:
        """Suggest from `name` directory according to given `query`."""
        return self._suggestions.suggest(name=name, query=query, count=count, **kwargs)

    def find_by_id(
        self, name: str, query: str, count: int = settings.SUGGESTION_COUNT, **kwargs
    ) -> List[Dict]:
        """Find record in `name` directory by its ID."""
        return self._suggestions.find_by_id(name=name, query=query, count=count, **kwargs)

    def find_affiliated(
        self, query: str, count: int = settings.SUGGESTION_COUNT, **kwargs
    ) -> List[Dict]:
        """Find affiliated parties by INN."""
        return self._suggestions.find_affiliated(query=query, count=count, **kwargs)

    def get_balance(self) -> float:
        """Get account balance."""
        return self._profile.get_balance()

    def get_daily_stats(self, date: dt.date = None) -> Dict:
        """Get daily service usage stats."""
        return self._profile.get_daily_stats(date=date)

    def get_versions(self) -> Dict:
        """Get product and dataset versions."""
        return self._profile.get_versions()

    def __enter__(self) -> "DadataClient":
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        """Close network connections"""
        self._cleaner.close()
        self._suggestions.close()
        self._profile.close()
