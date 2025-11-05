"""
Token-based chunking using Chonkie TokenChunker.

This generator uses Chonkie's TokenChunker for token-aware text chunking,
ensuring chunks respect token boundaries and match the embedding model's tokenizer.
"""
import logging
from typing import Dict, Any
from .chonkie_base import ChonkieChunkingGenerator

logger = logging.getLogger(__name__)

try:
    from chonkie import TokenChunker
    TOKEN_CHUNKER_AVAILABLE = True
except ImportError:
    TOKEN_CHUNKER_AVAILABLE = False
    logger.warning("Chonkie TokenChunker not available")


class TokenChunkerGenerator(ChonkieChunkingGenerator):
    """Token-based chunking using Chonkie TokenChunker"""
    
    @property
    def name(self) -> str:
        return "chonkie_token_chunker"
    
    def _get_chunker_params(self) -> Dict[str, Any]:
        """Get TokenChunker-specific parameters."""
        tokenizer = self._get_tokenizer()
        if tokenizer is None:
            logger.error("🔍 DEBUG: Tokenizer is None! This will cause the TokenChunker to fail!")
            raise ValueError("Tokenizer is None - cannot create TokenChunker")
        
        return {
            "tokenizer": tokenizer,  # TokenChunker uses 'tokenizer' parameter
            "chunk_size": self.config.chunk_size,
            "chunk_overlap": self.config.chunk_overlap  # TokenChunker uses 'chunk_overlap' parameter
        }
    
    def _create_chunker(self, **kwargs):
        """Create TokenChunker with its specific parameters."""
        logger.info(f"🔍 DEBUG: Creating TokenChunker with parameters: {kwargs}")
        return TokenChunker(**kwargs)
