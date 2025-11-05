"""
Sentence-based chunking using Chonkie SentenceChunker.

This generator uses Chonkie's SentenceChunker for sentence-aware text chunking,
splitting text at sentence boundaries while respecting token limits.
"""
import logging
from typing import Dict, Any
from .chonkie_base import ChonkieChunkingGenerator

logger = logging.getLogger(__name__)

try:
    from chonkie import SentenceChunker
    SENTENCE_CHUNKER_AVAILABLE = True
except ImportError:
    SENTENCE_CHUNKER_AVAILABLE = False
    logger.warning("Chonkie SentenceChunker not available")


class SentenceChunkerGenerator(ChonkieChunkingGenerator):
    """Sentence-based chunking using Chonkie SentenceChunker"""
    
    @property
    def name(self) -> str:
        return "chonkie_sentence_chunker"
    
    def _get_chunker_params(self) -> Dict[str, Any]:
        """Get SentenceChunker-specific parameters."""
        return {
            "tokenizer_or_token_counter": self._get_tokenizer(), 
            "chunk_size": self.config.chunk_size,
            "chunk_overlap": self.config.chunk_overlap,
            # Add SentenceChunker-specific parameters with defaults
            "min_sentences_per_chunk": self.config.min_sentences_per_chunk if self.config.min_sentences_per_chunk is not None else 1,
            "min_characters_per_sentence": self.config.min_characters_per_sentence if self.config.min_characters_per_sentence is not None else 12
        }
    
    def _create_chunker(self, **kwargs):
        """Create SentenceChunker with its specific parameters."""
        logger.info(f"🔍 DEBUG: Creating SentenceChunker with parameters: {kwargs}")
        return SentenceChunker(**kwargs)
