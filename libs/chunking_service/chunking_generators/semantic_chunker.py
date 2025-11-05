"""
Semantic chunking using Chonkie SemanticChunker.

This generator uses Chonkie's SemanticChunker for semantic similarity-based
chunking, which splits text based on semantic similarity thresholds using
sentence-transformers embeddings.
"""
import logging
from typing import Dict, Any
from .chonkie_base import ChonkieChunkingGenerator

logger = logging.getLogger(__name__)

try:
    from chonkie import SemanticChunker
    SEMANTIC_CHUNKER_AVAILABLE = True
except ImportError:
    SEMANTIC_CHUNKER_AVAILABLE = False
    logger.warning("Chonkie SemanticChunker not available")


class SemanticChunkerGenerator(ChonkieChunkingGenerator):
    """Semantic chunking using Chonkie SemanticChunker"""
    
    @property
    def name(self) -> str:
        return "chonkie_semantic_chunker"
    
    def _get_chunker_params(self) -> Dict[str, Any]:
        """Get SemanticChunker-specific parameters."""
        embedding_model = self._build_embedding_model()
        
        # Define parameter mappings with defaults
        param_defaults = {
            'semantic_threshold': 0.8,
            'similarity_window': 3,
            'min_sentences_per_chunk': 1,
            'skip_window': 0,
            'min_chunk_size': 2,
            'min_characters_per_sentence': 12,
            'filter_window': 5,
            'filter_polyorder': 3,
            'filter_tolerance': 0.2
        }
        
        # Get parameters with fallback to defaults
        params = {}
        for param_name, default_value in param_defaults.items():
            value = getattr(self.config, param_name, default_value)
            params[param_name] = default_value if value is None else value
        
        return {
            "embedding_model": embedding_model,
            "threshold": params['semantic_threshold'],
            "chunk_size": self.config.chunk_size,
            "similarity_window": params['similarity_window'],
            "min_sentences_per_chunk": params['min_sentences_per_chunk'],
        }
    
    def _create_chunker(self, **kwargs):
        """Create SemanticChunker with its specific parameters."""
        logger.info(f"Creating SemanticChunker with parameters: {list(kwargs.keys())}")
        return SemanticChunker(**kwargs)
