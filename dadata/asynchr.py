"""
Asynchronous Dadata API client.
"""

import datetime as dt
from typing import Dict, List, Optional
import httpx
from dadata import settings


class ClientBase:
    """Base class for API client"""

    def __init__(
        self,
        base_url: str,
        token: str,
        secret: Optional[str] = None,
        timeout: int = settings.TIMEOUT_SEC,
    ):
        headers = {
            "Content-type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Token {token}",
        }
        if secret:
            headers["X-Secret"] = secret
        self._client = httpx.AsyncClient(base_url=base_url, headers=headers, timeout=timeout)

    async def __aenter__(self) -> "ClientBase":
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()

    async def close(self):
        """Close network connections"""
        await self._client.aclose()

    async def _get(self, url, data):
        """GET request to Dadata API"""
        response = await self._client.get(url, params=data)
        response.raise_for_status()
        return response.json()

    async def _post(self, url, data):
        """POST request to Dadata API"""
        response = await self._client.post(url, json=data)
        response.raise_for_status()
        return response.json()


class CleanClient(ClientBase):
    """Dadata Cleaner API client"""

    BASE_URL = "https://cleaner.dadata.ru/api/v1/"

    def __init__(
        self,
        token: str,
        secret: Optional[str] = None,
        timeout: int = settings.TIMEOUT_SEC,
    ):
        super().__init__(base_url=self.BASE_URL, token=token, secret=secret, timeout=timeout)

    async def clean(self, name: str, source: str) -> Optional[Dict]:
        """Cleanse `source` as `name` data type."""
        url = f"clean/{name}"
        data = [source]
        response = await self._post(url, data)
        return response[0] if response else None

    async def clean_record(self, structure: List[str], record: List[str]) -> List[Dict]:
        """Cleanse `record` of specified `structure`."""
        url = "clean"
        data = {"structure": structure, "data": [record]}
        response = await self._post(url, data)
        return response["data"][0] if response else None


class SuggestClient(ClientBase):
    """Dadata Suggestions API client"""

    BASE_URL = "https://suggestions.dadata.ru/suggestions/api/4_1/rs/"

    def __init__(
        self,
        token: str,
        secret: Optional[str] = None,
        timeout: int = settings.TIMEOUT_SEC,
    ):
        super().__init__(base_url=self.BASE_URL, token=token, secret=secret, timeout=timeout)

    async def geolocate(
        self, name: str, lat: float, lon: float, radius_meters: int = 100, **kwargs
    ) -> List[Dict]:
        """Find places near given coordinates in given radius."""
        url = f"geolocate/{name}"
        data = {"lat": lat, "lon": lon, "radius_meters": radius_meters}
        data.update(kwargs)
        response = await self._post(url, data)
        return response["suggestions"]

    async def iplocate(self, query: str, **kwargs) -> Optional[Dict]:
        """Detect city by IPv4 or IPv6 address."""
        url = "iplocate/address"
        data = {"ip": query}
        data.update(kwargs)
        response = await self._get(url, data)
        return response["location"] if "location" in response else None

    async def suggest(
        self, name: str, query: str, count: int = settings.SUGGESTION_COUNT, **kwargs
    ) -> List[Dict]:
        """Suggest from `name` directory according to given `query`."""
        url = f"suggest/{name}"
        data = {"query": query, "count": count}
        data.update(kwargs)
        response = await self._post(url, data)
        return response["suggestions"]

    async def find_by_id(
        self, name: str, query: str, count: int = settings.SUGGESTION_COUNT, **kwargs
    ) -> List[Dict]:
        """Find record in `name` directory by its ID."""
        url = f"findById/{name}"
        data = {"query": query, "count": count}
        data.update(kwargs)
        response = await self._post(url, data)
        return response["suggestions"]

    async def find_affiliated(
        self, query: str, count: int = settings.SUGGESTION_COUNT, **kwargs
    ) -> List[Dict]:
        """Find affiliated parties by INN."""
        url = "findAffiliated/party"
        data = {"query": query, "count": count}
        data.update(kwargs)
        response = await self._post(url, data)
        return response["suggestions"]


class ProfileClient(ClientBase):
    """Dadata Profile API client"""

    BASE_URL = "https://dadata.ru/api/v2/"

    def __init__(
        self,
        token: str,
        secret: Optional[str] = None,
        timeout: int = settings.TIMEOUT_SEC,
    ):
        super().__init__(base_url=self.BASE_URL, token=token, secret=secret, timeout=timeout)

    async def get_balance(self) -> float:
        """Get account balance."""
        url = "profile/balance"
        response = await self._get(url, data={})
        return response["balance"]

    async def get_daily_stats(self, date: Optional[dt.date] = None) -> Dict:
        """Get daily service usage stats."""
        url = "stat/daily"
        data = {"date": date.isoformat()} if date else {}
        response = await self._get(url, data)
        return response

    async def get_versions(self) -> Dict:
        """Get product and dataset versions."""
        url = "version"
        response = await self._get(url, data={})
        return response


class DadataClient:
    """Asynchronous Dadata API client"""

    def __init__(
        self,
        token: str,
        secret: Optional[str] = None,
        timeout: int = settings.TIMEOUT_SEC,
    ):
        self._cleaner = CleanClient(token=token, secret=secret, timeout=timeout)
        self._suggestions = SuggestClient(token=token, secret=secret, timeout=timeout)
        self._profile = ProfileClient(token=token, secret=secret, timeout=timeout)

    async def clean(self, name: str, source: str) -> Optional[Dict]:
        """Cleanse `source` as `name` data type."""
        return await self._cleaner.clean(name=name, source=source)

    async def clean_record(self, structure: List[str], record: List[str]) -> List[Dict]:
        """Cleanse `record` of specified `structure`."""
        return await self._cleaner.clean_record(structure=structure, record=record)

    async def geolocate(
        self, name: str, lat: float, lon: float, radius_meters: int = 100, **kwargs
    ) -> List[Dict]:
        """Find places near given coordinates in given radius."""
        return await self._suggestions.geolocate(
            name=name, lat=lat, lon=lon, radius_meters=radius_meters, **kwargs
        )

    async def iplocate(self, query: str, **kwargs) -> Optional[Dict]:
        """Detect city by IPv4 or IPv6 address."""
        return await self._suggestions.iplocate(query=query, **kwargs)

    async def suggest(
        self, name: str, query: str, count: int = settings.SUGGESTION_COUNT, **kwargs
    ) -> List[Dict]:
        """Suggest from `name` directory according to given `query`."""
        return await self._suggestions.suggest(name=name, query=query, count=count, **kwargs)

    async def find_by_id(
        self, name: str, query: str, count: int = settings.SUGGESTION_COUNT, **kwargs
    ) -> List[Dict]:
        """Find record in `name` directory by its ID."""
        return await self._suggestions.find_by_id(name=name, query=query, count=count, **kwargs)

    async def find_affiliated(
        self, query: str, count: int = settings.SUGGESTION_COUNT, **kwargs
    ) -> List[Dict]:
        """Find affiliated parties by INN."""
        return await self._suggestions.find_affiliated(query=query, count=count, **kwargs)

    async def get_balance(self) -> float:
        """Get account balance."""
        return await self._profile.get_balance()

    async def get_daily_stats(self, date: Optional[dt.date] = None) -> Dict:
        """Get daily service usage stats."""
        return await self._profile.get_daily_stats(date=date)

    async def get_versions(self) -> Dict:
        """Get product and dataset versions."""
        return await self._profile.get_versions()

    async def __aenter__(self) -> "DadataClient":
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()

    async def close(self):
        """Close network connections"""
        await self._cleaner.close()
        await self._suggestions.close()
        await self._profile.close()
