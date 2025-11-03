"""
Document Database Providers

This module contains providers for document databases like Elasticsearch.
"""

from .elasticsearch_provider import ElasticsearchDocProvider

__all__ = [
    "ElasticsearchDocProvider"
]
