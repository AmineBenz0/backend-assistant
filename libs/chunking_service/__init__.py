"""
Chunking Service Module

This module provides document chunking capabilities for the VectorRAG pipeline.
"""

from .service import ChunkingGeneratorInterface
from .chunking_generators.token_chunker import TokenChunkerGenerator
from .chunking_generators.sentence_chunker import SentenceChunkerGenerator
from .chunking_generators.recursive_chunker import RecursiveChunkerGenerator
from .chunking_generators.chonkie_base import CHONKIE_AVAILABLE
from .models import (
    ChunkingConfig,
    ChunkingMethod,
    ChunkingResult,
    DocumentChunk,
    ChunkMetadata,
    ChunkType,
    ChunkingRequest,
    ChunkingResponse
)


def create_chunking_from_config(config: dict) -> ChunkingGeneratorInterface:
    """
    Create a chunking adapter from configuration dictionary.
    
    Args:
        config: Configuration dictionary with 'provider' and 'config' keys
        
    Returns:
        ChunkingGeneratorInterface instance
    """
    provider = config.get("provider", "token_chunker")
    chunking_config = ChunkingConfig(**config.get("config", {}))
    
    return ChunkingGeneratorInterface(default_provider=provider)

__all__ = [
    "ChunkingGeneratorInterface",
    "TokenChunkerGenerator",
    "SentenceChunkerGenerator",
    "RecursiveChunkerGenerator",
    "CHONKIE_AVAILABLE",
    "ChunkingConfig",
    "ChunkingMethod",
    "ChunkingResult",
    "DocumentChunk",
    "ChunkMetadata",
    "ChunkType",
    "ChunkingRequest",
    "ChunkingResponse",
    "create_chunking_from_config",
]
