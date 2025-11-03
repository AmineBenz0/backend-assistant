"""
Chunking Service Interface

This module provides a high-level interface for chunking services.
"""
import os
import logging
from typing import List, Dict, Any, Optional, Union

from .chunking_generators.recursive_text_splitter import RecursiveTextSplitterGenerator

# Optional import for semantic splitter
try:
    from .chunking_generators.semantic_splitter import SemanticSplitterGenerator
    SEMANTIC_SPLITTER_AVAILABLE = True
except ImportError:
    SEMANTIC_SPLITTER_AVAILABLE = False
    logger.warning("Semantic splitter not available")
from .chunking_generators.base import AbstractChunkingGenerator
from .models import ChunkingConfig, ChunkingMethod, ChunkingResult, ChunkingRequest, ChunkingResponse

logger = logging.getLogger(__name__)


class ChunkingGeneratorInterface:
    """
    High-level interface for chunking services
    
    This class provides a unified interface for different chunking providers
    and handles provider selection, configuration, and fallbacks.
    """
    
    def __init__(self, default_provider: str = "recursive_text_splitter"):
        """
        Initialize the chunking service interface
        
        Args:
            default_provider: Default chunking provider to use
        """
        self.default_provider = default_provider
        self.generators = {}
        self._initialized = False
        
        logger.info(f"Initialized ChunkingGeneratorInterface with default provider: {default_provider}")
    
    def _get_recursive_text_splitter_generator(self, config: ChunkingConfig) -> RecursiveTextSplitterGenerator:
        """Get recursive text splitter generator"""
        return RecursiveTextSplitterGenerator(config)
    
    def _get_semantic_splitter_generator(self, config: ChunkingConfig) -> SemanticSplitterGenerator:
        """Get semantic splitter generator"""
        return SemanticSplitterGenerator(config)
    
    def get_generator(self, provider: str, config: ChunkingConfig) -> AbstractChunkingGenerator:
        """
        Get a chunking generator for the specified provider
        
        Args:
            provider: Provider name ("recursive_text_splitter", "semantic_splitter")
            config: Chunking configuration
            
        Returns:
            Chunking generator instance
        """
        cache_key = f"{provider}_{hash(str(sorted(config.model_dump().items())))}"
        
        if cache_key in self.generators:
            return self.generators[cache_key]
        
        if provider == "recursive_text_splitter":
            generator = self._get_recursive_text_splitter_generator(config)
        elif provider == "semantic_splitter":
            if not SEMANTIC_SPLITTER_AVAILABLE:
                raise ValueError("Semantic splitter is not available. Please install langchain_experimental.")
            generator = self._get_semantic_splitter_generator(config)
        else:
            raise ValueError(f"Unsupported chunking provider: {provider}")
        
        self.generators[cache_key] = generator
        logger.info(f"Created {provider} chunking generator")
        
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
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        method: ChunkingMethod = ChunkingMethod.RECURSIVE,
        provider: Optional[str] = None,
        document_metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> ChunkingResult:
        """
        Chunk a document for RAG with simplified parameters (synchronous version)
        
        Args:
            text: Document text to chunk
            chunk_size: Size of each chunk
            chunk_overlap: Overlap between chunks
            method: Chunking method to use
            provider: Optional provider override
            document_metadata: Optional metadata about the source document
            **kwargs: Additional configuration
            
        Returns:
            Chunking result with chunks and metadata
        """
        config = ChunkingConfig(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            method=method,
            **kwargs
        )
        
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
        providers = ["recursive_text_splitter"]
        if SEMANTIC_SPLITTER_AVAILABLE:
            providers.append("semantic_splitter")
        return providers
    
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

