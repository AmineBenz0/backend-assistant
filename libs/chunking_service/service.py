"""
Chunking Service Interface

This module provides a high-level interface for chunking services.
"""
import os
import logging
from typing import List, Dict, Any, Optional, Union

from .chunking_generators.token_chunker import TokenChunkerGenerator
from .chunking_generators.sentence_chunker import SentenceChunkerGenerator
from .chunking_generators.recursive_chunker import RecursiveChunkerGenerator
from .chunking_generators.late_chunker import LateChunkerGenerator
from .chunking_generators.semantic_chunker import SemanticChunkerGenerator
from .chunking_generators.chonkie_base import CHONKIE_AVAILABLE
from .chunking_generators.base import AbstractChunkingGenerator
from .models import ChunkingConfig, ChunkingMethod, ChunkingResult, ChunkingRequest, ChunkingResponse

logger = logging.getLogger(__name__)


class ChunkingGeneratorInterface:
    """
    High-level interface for chunking services
    
    This class provides a unified interface for different chunking providers
    and handles provider selection, configuration, and fallbacks.
    """
    
    def __init__(self, default_provider: str = "token_chunker"):
        """
        Initialize the chunking service interface
        
        Args:
            default_provider: Default chunking provider to use
        """
        self.default_provider = default_provider
        self.generators = {}
        self._initialized = False
        
        logger.info(f"Initialized ChunkingGeneratorInterface with default provider: {default_provider}")
    
    def _get_token_chunker_generator(self, config: ChunkingConfig) -> TokenChunkerGenerator:
        """Get token chunker generator"""
        return TokenChunkerGenerator(config)
    
    def _get_sentence_chunker_generator(self, config: ChunkingConfig) -> SentenceChunkerGenerator:
        """Get sentence chunker generator"""
        return SentenceChunkerGenerator(config)
    
    def _get_recursive_chunker_generator(self, config: ChunkingConfig) -> RecursiveChunkerGenerator:
        """Get recursive chunker generator"""
        return RecursiveChunkerGenerator(config)
    
    def _get_late_chunker_generator(self, config: ChunkingConfig) -> LateChunkerGenerator:
        """Get late chunker generator"""
        return LateChunkerGenerator(config)
    
    def _get_semantic_chunker_generator(self, config: ChunkingConfig) -> SemanticChunkerGenerator:
        """Get semantic chunker generator"""
        return SemanticChunkerGenerator(config)
    
    def get_generator(self, provider: str, config: ChunkingConfig) -> AbstractChunkingGenerator:
        """
        Get a chunking generator for the specified provider
        
        Args:
            provider: Provider name ("token_chunker", "sentence_chunker", "recursive_chunker")
            config: Chunking configuration
            
        Returns:
            Chunking generator instance
        """
        logger.info(f"🔍 DEBUG: ChunkingGeneratorInterface.get_generator called with provider='{provider}'")
        logger.info(f"🔍 DEBUG: config: {config}")
        logger.info(f"🔍 DEBUG: config.embeddings_provider: {config.embeddings_provider}")
        logger.info(f"🔍 DEBUG: config.embeddings_model: {config.embeddings_model}")
        
        cache_key = f"{provider}_{hash(str(sorted(config.model_dump().items())))}"
        logger.info(f"🔍 DEBUG: cache_key: {cache_key}")
        
        if cache_key in self.generators:
            logger.info(f"🔍 DEBUG: Using cached generator for {provider}")
            return self.generators[cache_key]
        
        if not CHONKIE_AVAILABLE:
            logger.error("🔍 DEBUG: Chonkie is not available!")
            raise ValueError("Chonkie is required but not available. Please install chonkie[all].")
        
        logger.info(f"🔍 DEBUG: Creating new {provider} generator")
        
        if provider == "token_chunker":
            generator = self._get_token_chunker_generator(config)
        elif provider == "sentence_chunker":
            generator = self._get_sentence_chunker_generator(config)
        elif provider == "recursive_chunker":
            generator = self._get_recursive_chunker_generator(config)
        elif provider == "late_chunker":
            generator = self._get_late_chunker_generator(config)
        elif provider == "semantic_chunker":
            generator = self._get_semantic_chunker_generator(config)
        else:
            logger.error(f"🔍 DEBUG: Unsupported provider: {provider}")
            raise ValueError(f"Unsupported chunking provider: {provider}")
        
        self.generators[cache_key] = generator
        logger.info(f"🔍 DEBUG: Created {provider} chunking generator: {type(generator)}")
        
        return generator
    
    async def chunk_text(
        self, 
        text: str, 
        config: Optional[ChunkingConfig] = None,
        provider: Optional[str] = None,
        document_metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> ChunkingResult:
        """
        Chunk text using the specified or default provider
        
        Args:
            text: Text to chunk
            config: Chunking configuration (uses default if not provided)
            provider: Optional provider override
            document_metadata: Optional metadata about the source document
            **kwargs: Additional configuration
            
        Returns:
            Chunking result with chunks and metadata
        """
        if config is None:
            config = ChunkingConfig()
        
        generator = self.get_generator(provider or self.default_provider, config)
        return await generator.chunk_document_for_rag(text, document_metadata, **kwargs)
    
    def chunk_document_for_rag_sync(
        self, 
        text: str,
        config: ChunkingConfig,
        provider: Optional[str] = None,
        document_metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> ChunkingResult:
        """
        Chunk a document for RAG with config object (synchronous version)
        
        Args:
            text: Document text to chunk
            config: Chunking configuration object
            provider: Optional provider override
            document_metadata: Optional metadata about the source document
            **kwargs: Additional configuration
            
        Returns:
            Chunking result with chunks and metadata
        """
        generator = self.get_generator(provider or self.default_provider, config)
        return generator.chunk_document_for_rag_sync(text, document_metadata, **kwargs)
    
    async def chunk_texts_batch(
        self, 
        texts: List[str],
        config: Optional[ChunkingConfig] = None,
        provider: Optional[str] = None,
        document_metadata_list: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> List[ChunkingResult]:
        """
        Chunk multiple texts in batch
        
        Args:
            texts: List of texts to chunk
            config: Chunking configuration (uses default if not provided)
            provider: Optional provider override
            document_metadata_list: Optional list of metadata for each document
            **kwargs: Additional configuration
            
        Returns:
            List of chunking results
        """
        if config is None:
            config = ChunkingConfig()
        
        generator = self.get_generator(provider or self.default_provider, config)
        
        results = []
        for i, text in enumerate(texts):
            doc_metadata = document_metadata_list[i] if document_metadata_list and i < len(document_metadata_list) else None
            result = await generator.chunk_document_for_rag(text, doc_metadata, **kwargs)
            results.append(result)
        
        return results
    
    async def health_check(self, provider: Optional[str] = None) -> Dict[str, Any]:
        """
        Check if the chunking service is healthy
        
        Args:
            provider: Optional provider to check (checks default if not provided)
            
        Returns:
            Health check result
        """
        try:
            config = ChunkingConfig()
            generator = self.get_generator(provider or self.default_provider, config)
            return await generator.health_check()
        except Exception as e:
            return {
                "status": "unhealthy",
                "provider": provider or self.default_provider,
                "error": str(e)
            }
    
    def get_available_providers(self) -> List[str]:
        """Get list of available chunking providers"""
        if not CHONKIE_AVAILABLE:
            return []
        
        return [
            "token_chunker",
            "sentence_chunker", 
            "recursive_chunker"
        ]
    
    def get_provider_info(self, provider: str) -> Dict[str, Any]:
        """
        Get information about a specific provider
        
        Args:
            provider: Provider name
            
        Returns:
            Dictionary with provider information
        """
        try:
            config = ChunkingConfig()
            generator = self.get_generator(provider, config)
            
            return {
                "name": generator.name,
                "supports_semantic_chunking": generator.supports_semantic_chunking,
                "supports_custom_separators": generator.supports_custom_separators,
                "class_name": generator.__class__.__name__,
                "module": generator.__class__.__module__
            }
        except Exception as e:
            return {
                "name": provider,
                "error": str(e)
            }
    
    def close(self) -> None:
        """Close all generators and cleanup resources"""
        for generator in self.generators.values():
            if hasattr(generator, 'close'):
                generator.close()
        self.generators.clear()
        logger.info("Closed all chunking generators")

