"""
Late chunking using Chonkie LateChunker.

This generator uses Chonkie's LateChunker for late interaction chunking,
which first chunks text using recursive splitting and then generates
token-level embeddings for each chunk using sentence-transformers.
"""
import logging
from typing import Dict, Any
from .chonkie_base import ChonkieChunkingGenerator

logger = logging.getLogger(__name__)

try:
    from chonkie import LateChunker
    LATE_CHUNKER_AVAILABLE = True
except ImportError:
    LATE_CHUNKER_AVAILABLE = False
    logger.warning("Chonkie LateChunker not available")


class LateChunkerGenerator(ChonkieChunkingGenerator):
    """Late chunking using Chonkie LateChunker"""
    
    @property
    def name(self) -> str:
        return "chonkie_late_chunker"
    
    def _get_chunker_params(self) -> Dict[str, Any]:
        """Get LateChunker-specific parameters."""
        from chonkie import RecursiveRules  # Import RecursiveRules
        
        embedding_model = self._build_embedding_model()
        
        params = {
            "embedding_model": embedding_model,
            "chunk_size": self.config.chunk_size,
            "rules": RecursiveRules(),  # Required parameter for LateChunker
        }
        
        # Add optional min_characters_per_chunk if specified
        if hasattr(self.config, 'min_characters_per_chunk') and self.config.min_characters_per_chunk is not None:
            params["min_characters_per_chunk"] = self.config.min_characters_per_chunk
        
        return params
    
    def _create_chunker(self, **kwargs):
        """Create LateChunker with its specific parameters."""
        logger.info(f"Creating LateChunker with parameters: {list(kwargs.keys())}")
        
        # LateChunker expects: embedding_model, chunk_size, and optionally min_characters_per_chunk
        # All other params are passed via **kwargs
        return LateChunker(**kwargs)
