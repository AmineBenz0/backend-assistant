"""
Semantic text splitter generator implementation.

This generator uses semantic understanding to create more meaningful chunks
by grouping related content together based on semantic similarity.
"""

import time
import logging
from typing import Dict, List, Any, Optional

from .base import AbstractChunkingGenerator
from ..models import DocumentChunk, ChunkingConfig, ChunkingMethod

logger = logging.getLogger(__name__)

# Optional imports for semantic chunking
try:
    from langchain_experimental.text_splitter import SemanticChunker
    from langchain_openai.embeddings import OpenAIEmbeddings
    SEMANTIC_CHUNKING_AVAILABLE = True
except ImportError:
    SEMANTIC_CHUNKING_AVAILABLE = False
    logger.warning("langchain_experimental not available, semantic chunking will not work")


class SemanticSplitterGenerator(AbstractChunkingGenerator):
    """
    Semantic text splitter implementation using LangChain's experimental SemanticChunker.
    
    This generator creates chunks based on semantic similarity rather than just text boundaries,
    resulting in more meaningful and contextually coherent chunks for RAG applications.
    """

    def __init__(self, config: ChunkingConfig):
        super().__init__(config)
        self._splitter = None
        self._embeddings = None
        
        if not SEMANTIC_CHUNKING_AVAILABLE:
            raise ImportError("langchain_experimental is required for semantic chunking but not available")

    @property
    def name(self) -> str:
        return "semantic_splitter"

    @property
    def supports_semantic_chunking(self) -> bool:
        return SEMANTIC_CHUNKING_AVAILABLE

    @property
    def supports_custom_separators(self) -> bool:
        return False

    def _get_embeddings(self) -> "OpenAIEmbeddings":
        """Get or create the embeddings instance"""
        if self._embeddings is None:
            try:
                self._embeddings = OpenAIEmbeddings(
                    model=self.config.embedding_model or "text-embedding-3-small"
                )
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI embeddings: {e}")
                logger.warning("Falling back to default embeddings")
                self._embeddings = OpenAIEmbeddings()
        return self._embeddings

    def _get_splitter(self) -> "SemanticChunker":
        """Get or create the semantic chunker instance"""
        if self._splitter is None:
            embeddings = self._get_embeddings()
            self._splitter = SemanticChunker(
                embeddings=embeddings,
                breakpoint_threshold_type=self.config.breakpoint_threshold_type,
                breakpoint_threshold_amount=self.config.breakpoint_threshold_amount,
                **self.config.custom_settings
            )
        return self._splitter

    async def chunk_text(
        self, 
        text: str,
        document_metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> List[DocumentChunk]:
        """Chunk text using semantic text splitting."""
        try:
            splitter = self._get_splitter()
            
            # Use the splitter to create semantic chunks
            text_chunks = splitter.split_text(text)

            # Create structured chunk objects with rich metadata
            chunks = []
            for i, chunk_text in enumerate(text_chunks):
                chunk_metadata = self._create_chunk_metadata(
                    chunk_text=chunk_text,
                    chunk_index=i,
                    document_metadata=document_metadata
                )
                
                # Add semantic-specific metadata
                chunk_metadata.chunking_method = ChunkingMethod.SEMANTIC
                chunk_metadata.source_document_name = document_metadata.get('object_name') if document_metadata else None
                
                chunk = DocumentChunk(
                    text=chunk_text,
                    metadata=chunk_metadata
                )
                chunks.append(chunk)
            
            logger.info(f"Text chunked semantically: {len(chunks)} chunks created using {self.name}")
            return chunks
            
        except Exception as e:
            logger.error(f"Failed to chunk text semantically: {e}", exc_info=True)
            raise RuntimeError(f"Failed to chunk text semantically: {e}") from e

    def close(self) -> None:
        """Close connections and cleanup resources."""
        self._splitter = None
        self._embeddings = None

