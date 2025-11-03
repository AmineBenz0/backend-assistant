"""
Embeddings Service Module

This module provides embedding generation capabilities for the GraphRAG pipeline.
"""

from .service import EmbeddingGeneratorInterface
from .embedding_generators.entity_embeddings import EntityEmbeddingGenerator

__all__ = [
    "EmbeddingGeneratorInterface",
    "EntityEmbeddingGenerator",
]