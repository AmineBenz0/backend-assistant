"""
Recursive text splitter generator implementation.

This generator uses LangChain's RecursiveCharacterTextSplitter for robust text chunking.
"""

import time
import logging
from typing import Dict, List, Any, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .base import AbstractChunkingGenerator
from ..models import DocumentChunk, ChunkingConfig, ChunkingMethod

logger = logging.getLogger(__name__)


class RecursiveTextSplitterGenerator(AbstractChunkingGenerator):
    """
    LangChain-powered recursive text splitter implementation.
    
    This generator acts as a wrapper around LangChain's battle-tested
    RecursiveCharacterTextSplitter, ensuring robustness and maintainability.
    """

    def __init__(self, config: ChunkingConfig):
        super().__init__(config)
        self._splitter = None

    @property
    def name(self) -> str:
        return "recursive_text_splitter"

    @property
    def supports_semantic_chunking(self) -> bool:
        return False

    @property
    def supports_custom_separators(self) -> bool:
        return True

    def _get_splitter(self) -> RecursiveCharacterTextSplitter:
        """Get or create the text splitter instance"""
        if self._splitter is None:
            self._splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.config.chunk_size,
                chunk_overlap=self.config.chunk_overlap,
                separators=self.config.separators,
                keep_separator=self.config.keep_separator,
                add_start_index=self.config.add_start_index,
                strip_whitespace=self.config.strip_whitespace,
                is_separator_regex=self.config.is_separator_regex,
                **self.config.custom_settings
            )
        return self._splitter

    def chunk_text(
        self, 
        text: str,
        document_metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> List[DocumentChunk]:
        """Chunk text using LangChain's recursive text splitter."""
        try:
            splitter = self._get_splitter()
            
            # Use the splitter to create chunks (as strings)
            text_chunks = splitter.split_text(text)

            # Create structured chunk objects with rich metadata
            chunks = []
            for i, chunk_text in enumerate(text_chunks):
                chunk_metadata = self._create_chunk_metadata(
                    chunk_text=chunk_text,
                    chunk_index=i,
                    document_metadata=document_metadata
                )
                
                # Add source document and any other relevant info
                chunk_metadata.source_document_name = document_metadata.get('object_name') if document_metadata else None
                
                chunk = DocumentChunk(
                    text=chunk_text,
                    metadata=chunk_metadata
                )
                chunks.append(chunk)
            
            logger.info(f"Text chunked: {len(chunks)} chunks created using {self.name}")
            return chunks
            
        except Exception as e:
            logger.error(f"Failed to chunk text: {e}", exc_info=True)
            raise RuntimeError(f"Failed to chunk text: {e}") from e
            
    def close(self) -> None:
        """Close connections and cleanup resources."""
        self._splitter = None

