"""
Chunking Service Module

This module provides document chunking capabilities for the GraphRAG pipeline.
"""

from .service import ChunkingGeneratorInterface
from .chunking_generators.recursive_text_splitter import RecursiveTextSplitterGenerator

# Optional import for semantic splitter
try:
    from .chunking_generators.semantic_splitter import SemanticSplitterGenerator
    SEMANTIC_SPLITTER_AVAILABLE = True
except ImportError:
    SEMANTIC_SPLITTER_AVAILABLE = False
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
    provider = config.get("provider", "recursive_text_splitter")
    chunking_config = ChunkingConfig(**config.get("config", {}))
    
    return ChunkingGeneratorInterface(default_provider=provider)

__all__ = [
    "ChunkingGeneratorInterface",
    "RecursiveTextSplitterGenerator",
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

# Conditionally add SemanticSplitterGenerator if available
if SEMANTIC_SPLITTER_AVAILABLE:
    __all__.append("SemanticSplitterGenerator")
