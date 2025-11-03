"""
Abstract base classes for embedding generators
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
import asyncio

from ..models import DocumentChunk, EmbeddingResult


class AbstractEmbeddingGenerator(ABC):
    """Abstract base class for embedding generators"""
    
    def __init__(self, model_name: str, batch_size: int = 100):
        self.model_name = model_name
        self.batch_size = batch_size
    
    @property
    @abstractmethod
    def embedding_dimension(self) -> int:
        """Return the dimension of embeddings produced by this generator"""
        pass
    
    @property
    @abstractmethod
    def max_tokens(self) -> int:
        """Return the maximum number of tokens this model can handle"""
        pass
    
    @abstractmethod
    async def generate_embeddings(
        self, 
        texts: List[str],
        **kwargs
    ) -> List[List[float]]:
        """
        Generate embeddings for a list of texts
        
        Args:
            texts: List of texts to embed
            **kwargs: Additional model-specific parameters
            
        Returns:
            List of embedding vectors
        """
        pass
    
    @abstractmethod
    async def generate_single_embedding(
        self, 
        text: str,
        **kwargs
    ) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Text to embed
            **kwargs: Additional model-specific parameters
            
        Returns:
            Embedding vector
        """
        pass
    
    async def generate_chunk_embeddings(
        self, 
        chunks: List[DocumentChunk],
        **kwargs
    ) -> EmbeddingResult:
        """
        Generate embeddings for document chunks
        
        Args:
            chunks: List of document chunks
            **kwargs: Additional parameters
            
        Returns:
            Embedding result with updated chunks
        """
        import time
        start_time = time.time()
        
        # Extract texts from chunks
        texts = [chunk.text for chunk in chunks]
        
        # Generate embeddings in batches
        all_embeddings = []
        total_tokens = 0
        
        for i in range(0, len(texts), self.batch_size):
            batch_texts = texts[i:i + self.batch_size]
            batch_embeddings = await self.generate_embeddings(batch_texts, **kwargs)
            all_embeddings.extend(batch_embeddings)
            
            # Estimate tokens (rough approximation)
            batch_tokens = sum(len(text.split()) for text in batch_texts)
            total_tokens += batch_tokens
        
        # Update chunks with embeddings
        updated_chunks = []
        for chunk, embedding in zip(chunks, all_embeddings):
            updated_chunk = chunk.model_copy()
            updated_chunk.embedding = embedding
            updated_chunks.append(updated_chunk)
        
        processing_time = time.time() - start_time
        
        return EmbeddingResult(
            chunks=updated_chunks,
            embedding_model=self.model_name,
            total_chunks=len(chunks),
            total_tokens=total_tokens,
            processing_time=processing_time
        )
    
    def validate_text_length(self, text: str) -> bool:
        """Validate if text is within token limits"""
        # Simple word-based estimation (actual implementation should use tokenizer)
        estimated_tokens = len(text.split())
        return estimated_tokens <= self.max_tokens
    
    def truncate_text(self, text: str) -> str:
        """Truncate text to fit within token limits"""
        if self.validate_text_length(text):
            return text
        
        # Simple word-based truncation (actual implementation should use tokenizer)
        words = text.split()
        truncated_words = words[:self.max_tokens]
        return " ".join(truncated_words)
    
    async def health_check(self) -> Dict[str, Any]:
        """Check if the embedding service is healthy"""
        try:
            test_embedding = await self.generate_single_embedding("test")
            return {
                "status": "healthy",
                "model_name": self.model_name,
                "embedding_dimension": len(test_embedding),
                "max_tokens": self.max_tokens
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "model_name": self.model_name
            }


class AbstractBatchEmbeddingGenerator(AbstractEmbeddingGenerator):
    """Abstract base class for embedding generators that support batch processing"""
    
    @abstractmethod
    async def generate_embeddings_batch(
        self, 
        texts: List[str],
        batch_size: Optional[int] = None,
        **kwargs
    ) -> List[List[float]]:
        """
        Generate embeddings with optimized batch processing
        
        Args:
            texts: List of texts to embed
            batch_size: Override default batch size
            **kwargs: Additional parameters
            
        Returns:
            List of embedding vectors
        """
        pass
    
    async def generate_embeddings(
        self, 
        texts: List[str],
        **kwargs
    ) -> List[List[float]]:
        """Default implementation using batch processing"""
        return await self.generate_embeddings_batch(texts, self.batch_size, **kwargs)
