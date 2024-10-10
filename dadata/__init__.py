"""
Data cleansing and enrichment via Dadata API.
"""

from dadata.sync import DadataClient as Dadata
from dadata.asynchr import DadataClient as DadataAsync

__version__ = "24.10.0"
__all__ = ["Dadata", "DadataAsync"]
