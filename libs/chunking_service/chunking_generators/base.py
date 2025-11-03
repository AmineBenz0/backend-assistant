"""
Abstract base classes for chunking generators
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import time

from ..models import DocumentChunk, ChunkingResult, ChunkingConfig, ChunkMetadata, ChunkType


class AbstractChunkingGenerator(ABC):
    """Abstract base class for chunking generators"""
    
    def __init__(self, config: ChunkingConfig):
        self.config = config
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of this chunking generator"""
        pass
    
    @property
    @abstractmethod
    def supports_semantic_chunking(self) -> bool:
        """Return whether this generator supports semantic chunking"""
        pass
    
    @property
    @abstractmethod
    def supports_custom_separators(self) -> bool:
        """Return whether this generator supports custom separators"""
        pass
    
    @abstractmethod
    async def chunk_text(
        self, 
        text: str,
        document_metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> List[DocumentChunk]:
        """
        Chunk text into document chunks
        
        Args:
            text: Text to chunk
            document_metadata: Optional metadata about the source document
            **kwargs: Additional generator-specific parameters
            
        Returns:
            List of document chunks
        """
        pass
    
    def chunk_text(
        self, 
        text: str,
        document_metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> List[DocumentChunk]:
        """
        Chunk text into document chunks (synchronous version)
        
        Args:
            text: Text to chunk
            document_metadata: Optional metadata about the source document
            **kwargs: Additional generator-specific parameters
            
        Returns:
            List of document chunks
        """
        # Default implementation: run async version in event loop
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're already in an async context, we need to use a different approach
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self.chunk_text(text, document_metadata, **kwargs))
                    return future.result()
            else:
                return loop.run_until_complete(self.chunk_text(text, document_metadata, **kwargs))
        except RuntimeError:
            # No event loop exists, create a new one
            return asyncio.run(self.chunk_text(text, document_metadata, **kwargs))
    
    def chunk_document_for_rag_sync(
        self, 
        text: str,
        document_metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> ChunkingResult:
        """
        Chunk a document for RAG (Retrieval-Augmented Generation) - Synchronous version
        
        Args:
            text: Document text to chunk
            document_metadata: Optional metadata about the source document
            **kwargs: Additional parameters
            
        Returns:
            Chunking result with chunks and metadata
        """
        start_time = time.time()
        
        # Generate chunks synchronously
        chunks = self.chunk_text(text, document_metadata, **kwargs)
        
        # Generate chunk IDs if not provided
        for i, chunk in enumerate(chunks):
            if chunk.chunk_id is None:
                chunk.chunk_id = f"chunk_{i}_{int(time.time())}"
        
        processing_time = time.time() - start_time
        
        # Create chunking metadata
        chunking_metadata = {
            "total_chunks": len(chunks),
            "provider": self.name,
            "method": self.config.method.value,
            "config_used": self.config.model_dump(),
            "processing_timestamp": time.time(),
            "average_chunk_size": self._calculate_average_chunk_size(chunks),
            "chunk_size_distribution": self._calculate_chunk_size_distribution(chunks)
        }
        
        return ChunkingResult(
            chunks=chunks,
            total_chunks=len(chunks),
            chunking_method=self.config.method,
            provider=self.name,
            config_used=self.config,
            processing_time=processing_time,
            document_metadata=document_metadata or {},
            chunking_metadata=chunking_metadata
        )
    
    def _calculate_average_chunk_size(self, chunks: List[DocumentChunk]) -> float:
        """Calculate average chunk size"""
        if not chunks:
            return 0.0
        return sum(chunk.get_chunk_length() for chunk in chunks) / len(chunks)
    
    def _calculate_chunk_size_distribution(self, chunks: List[DocumentChunk]) -> Dict[str, int]:
        """Calculate chunk size distribution"""
        if not chunks:
            return {}
        
        sizes = [chunk.get_chunk_length() for chunk in chunks]
        return {
            "min": min(sizes),
            "max": max(sizes),
            "mean": int(sum(sizes) / len(sizes)),
            "median": int(sorted(sizes)[len(sizes) // 2])
        }
    
    def _determine_chunk_type(self, chunk_text: str) -> ChunkType:
        """Determine the type of chunk based on its content"""
        chunk_text = chunk_text.strip()
        
        if not chunk_text:
            return ChunkType.UNKNOWN
        
        # Check for different content types
        if chunk_text.startswith('#') or chunk_text.startswith('##'):
            return ChunkType.HEADING
        elif chunk_text.startswith('-') or chunk_text.startswith('*'):
            return ChunkType.LIST_ITEM
        elif chunk_text.startswith('```') or chunk_text.endswith('```'):
            return ChunkType.CODE_BLOCK
        elif chunk_text.startswith('>'):
            return ChunkType.QUOTE
        elif chunk_text.startswith('|') and '|' in chunk_text[1:]:
            return ChunkType.TABLE
        elif any(chunk_text.startswith(prefix) for prefix in ['http://', 'https://', 'www.']):
            return ChunkType.URL
        elif len(chunk_text.split()) <= 3:
            return ChunkType.SHORT_PHRASE
        else:
            return ChunkType.PARAGRAPH
    
    def _create_chunk_metadata(
        self, 
        chunk_text: str, 
        chunk_index: int, 
        document_metadata: Optional[Dict[str, Any]] = None
    ) -> ChunkMetadata:
        """Create metadata for a chunk"""
        return ChunkMetadata(
            chunk_index=chunk_index,
            chunk_size=len(chunk_text),
            chunk_type=self._determine_chunk_type(chunk_text),
            chunking_method=self.config.method,
            provider=self.name,
            document_filename=document_metadata.get("filename") if document_metadata else None,
            document_size=document_metadata.get("size") if document_metadata else None,
            source_document_name=document_metadata.get("object_name") if document_metadata else None,
            custom_metadata=document_metadata or {}
        )
    
    async def health_check(self) -> Dict[str, Any]:
        """Check if the chunking service is healthy"""
        try:
            test_text = "This is a test document for chunking. It contains multiple sentences to test the chunking functionality."
            test_chunks = await self.chunk_text(test_text)
            
            return {
                "status": "healthy",
                "provider": self.name,
                "method": self.config.method.value,
                "test_chunking_successful": len(test_chunks) > 0,
                "test_chunks_generated": len(test_chunks),
                "supports_semantic_chunking": self.supports_semantic_chunking,
                "supports_custom_separators": self.supports_custom_separators
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "provider": self.name,
                "method": self.config.method.value,
                "test_chunking_successful": False,
                "error_message": str(e)
            }


class AbstractBatchChunkingGenerator(AbstractChunkingGenerator):
    """Abstract base class for chunking generators that support batch processing"""
    
    @abstractmethod
    async def chunk_texts_batch(
        self, 
        texts: List[str],
        document_metadata_list: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> List[List[DocumentChunk]]:
        """
        Chunk multiple texts in batch
        
        Args:
            texts: List of texts to chunk
            document_metadata_list: Optional list of metadata for each document
            **kwargs: Additional parameters
            
        Returns:
            List of chunk lists (one per input text)
        """
        pass
    
    async def chunk_texts(
        self, 
        texts: List[str],
        document_metadata_list: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> List[List[DocumentChunk]]:
        """Default implementation using batch processing"""
        return await self.chunk_texts_batch(texts, document_metadata_list, **kwargs)

