"""
Data cleansing and enrichment via Dadata API.
"""

from dadata.sync import DadataClient as Dadata  # noqa
from dadata.asynchr import DadataClient as DadataAsync  # noqa

__version__ = "21.10.0"
__all__ = []  # type: ignore
