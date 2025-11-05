"""
Base class for all Chonkie-based chunking generators.

This module provides the base class that all Chonkie chunking generators inherit from,
including common functionality for tokenizer integration and chunk processing.
"""
from abc import abstractmethod
from typing import List, Dict, Any, Optional
import logging

from .base import AbstractChunkingGenerator
from .tokenizer_utils import get_tokenizer_for_embedding_model
from ..models import DocumentChunk, ChunkingConfig

logger = logging.getLogger(__name__)

try:
    import chonkie
    CHONKIE_AVAILABLE = True
except ImportError:
    CHONKIE_AVAILABLE = False
    logger.warning("Chonkie not available")


class ChonkieChunkingGenerator(AbstractChunkingGenerator):
    """Base class for all Chonkie-based chunking generators"""
    
    def __init__(self, config: ChunkingConfig):
        super().__init__(config)
        if not CHONKIE_AVAILABLE:
            raise ImportError("Chonkie is required but not available")
        self._chunker = None
        self._tokenizer = None
    
    def _get_chunker_params(self) -> Dict[str, Any]:
        """Get chunker-specific parameters. Override in subclasses for strategy-specific parameters."""
        return {
            "tokenizer_or_token_counter": self._get_tokenizer(),
            "chunk_size": self.config.chunk_size
        }
    
    @abstractmethod
    def _create_chunker(self, **kwargs):
        """Create the specific chunker with provided parameters. Override in subclasses."""
        pass
    
    def _get_chunker(self):
        """Get or create the chunker instance using strategy-specific parameters."""
        logger.info(f"🔍 DEBUG: _get_chunker called, current _chunker: {self._chunker}")
        
        if self._chunker is None:
            logger.info("🔍 DEBUG: Creating new chunker instance")
            params = self._get_chunker_params()
            logger.info(f"🔍 DEBUG: Chunker parameters: {params}")
            
            try:
                self._chunker = self._create_chunker(**params)
                logger.info(f"🔍 DEBUG: Chunker created successfully: {type(self._chunker)}")
            except Exception as e:
                logger.error(f"🔍 DEBUG: Failed to create chunker: {e}")
                import traceback
                logger.error(f"🔍 DEBUG: Chunker creation traceback: {traceback.format_exc()}")
                raise
        else:
            logger.info(f"🔍 DEBUG: Using cached chunker: {type(self._chunker)}")
            
        return self._chunker
    
    def _get_tokenizer(self):
        """Get tokenizer matching the embedding model"""
        logger.info(f"🔍 DEBUG: _get_tokenizer called, current _tokenizer: {self._tokenizer}")
        
        if self._tokenizer is None:
            provider = self.config.embeddings_provider or "azure_openai"
            model = self.config.embeddings_model or "text-embedding-3-large"
            
            logger.info(f"🔍 DEBUG: Getting tokenizer for provider='{provider}', model='{model}'")
            logger.info(f"🔍 DEBUG: config.embeddings_provider: {self.config.embeddings_provider}")
            logger.info(f"🔍 DEBUG: config.embeddings_model: {self.config.embeddings_model}")
            
            self._tokenizer = get_tokenizer_for_embedding_model(provider, model)
            logger.info(f"🔍 DEBUG: get_tokenizer_for_embedding_model returned: {type(self._tokenizer)} - {self._tokenizer}")
            
            if self._tokenizer is None:
                logger.error("🔍 DEBUG: get_tokenizer_for_embedding_model returned None!")
            else:
                logger.info(f"🔍 DEBUG: Tokenizer retrieved successfully: {type(self._tokenizer)}")
        else:
            logger.info(f"🔍 DEBUG: Using cached tokenizer: {type(self._tokenizer)}")
            
        return self._tokenizer
    
    def _build_embedding_model(self):
        """Build embedding model instance from provider and model config."""
        provider = self.config.embeddings_provider or "azure_openai"
        model = self.config.embeddings_model or "text-embedding-3-large"
        
        # Import AutoEmbeddings from Chonkie
        try:
            from chonkie.embeddings import AutoEmbeddings
        except ImportError:
            raise ImportError("Chonkie embeddings not available. Please install chonkie[all]")
        
        # For Azure OpenAI, we need to pass the proper parameters
        if provider == "azure_openai":
            # Get Azure OpenAI credentials from environment
            import os
            azure_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
            azure_api_key = os.getenv('AZURE_OPENAI_API_KEY')
            
            if not azure_endpoint or not azure_api_key:
                raise ValueError("Azure OpenAI credentials not found. Please set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY")
            
            # Try to create Azure OpenAI embeddings instance
            try:
                from chonkie.embeddings.azure_openai import AzureOpenAIEmbeddings
                return AzureOpenAIEmbeddings(
                    azure_endpoint=azure_endpoint,
                    model=model,
                    azure_api_key=azure_api_key
                )
            except ImportError:
                # Fallback: use AutoEmbeddings with Azure OpenAI model
                logger.warning("Azure OpenAI embeddings not available, falling back to AutoEmbeddings")
                return AutoEmbeddings.get_embeddings(f"azure://{model}")
        else:
            # For other providers, use AutoEmbeddings
            return AutoEmbeddings.get_embeddings(model)
    
    def chunk_text(self, text: str, document_metadata: Optional[Dict[str, Any]] = None, **kwargs) -> List[DocumentChunk]:
        """Chunk text using Chonkie chunker"""
        try:
            chunker = self._get_chunker()
            chonkie_chunks = chunker.chunk(text)
            
            chunks = []
            for i, chonkie_chunk in enumerate(chonkie_chunks):
                # Chonkie chunks have a .text attribute
                chunk_text = chonkie_chunk.text
                chunk_metadata = self._create_chunk_metadata(
                    chunk_text=chunk_text,
                    chunk_index=i,
                    document_metadata=document_metadata
                )
                
                chunk = DocumentChunk(
                    text=chunk_text,
                    metadata=chunk_metadata
                )
                chunks.append(chunk)
            
            logger.info(f"Text chunked using {self.name}: {len(chunks)} chunks created")
            return chunks
            
        except Exception as e:
            logger.error(f"Failed to chunk text with {self.name}: {e}", exc_info=True)
            raise RuntimeError(f"Failed to chunk text with {self.name}: {e}") from e
    
    @property
    def supports_semantic_chunking(self) -> bool:
        return False
    
    @property
    def supports_custom_separators(self) -> bool:
        return False
    
    def close(self) -> None:
        """Close and cleanup resources"""
        self._chunker = None
        self._tokenizer = None
