"""
Recursive chunking using Chonkie RecursiveChunker.

This generator uses Chonkie's RecursiveChunker for hierarchical text chunking,
recursively splitting text using different separators while respecting token limits.
"""
import logging
from typing import Dict, Any
from .chonkie_base import ChonkieChunkingGenerator
from chonkie import RecursiveRules

logger = logging.getLogger(__name__)

try:
    from chonkie import RecursiveChunker
    RECURSIVE_CHUNKER_AVAILABLE = True
except ImportError:
    RECURSIVE_CHUNKER_AVAILABLE = False
    logger.warning("Chonkie RecursiveChunker not available")


class RecursiveChunkerGenerator(ChonkieChunkingGenerator):
    """Recursive chunking using Chonkie RecursiveChunker"""
    
    @property
    def name(self) -> str:
        return "chonkie_recursive_chunker"
    
    def _get_chunker_params(self) -> Dict[str, Any]:
        """Get RecursiveChunker-specific parameters."""        
        # Define parameter mappings with defaults
        param_defaults = {
            'min_characters_per_chunk': 10
        }
        
        # Get parameters with fallback to defaults
        params = {}
        for param_name, default_value in param_defaults.items():
            value = getattr(self.config, param_name, default_value)
            params[param_name] = default_value if value is None else value
        
        return {
            "tokenizer_or_token_counter": self._get_tokenizer(),
            "chunk_size": self.config.chunk_size,
            "rules": RecursiveRules(),
            "min_characters_per_chunk": params['min_characters_per_chunk']
        }
    
    def _create_chunker(self, **kwargs):
        """Create RecursiveChunker with its specific parameters."""
        logger.info(f"🔍 DEBUG: Creating RecursiveChunker with parameters: {kwargs}")
        return RecursiveChunker(**kwargs)
