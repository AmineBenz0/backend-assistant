"""
T2V Transformers embedding generator implementation
"""
import asyncio
import aiohttp
import json
from typing import List, Dict, Any, Optional
import logging

from .base import AbstractBatchEmbeddingGenerator

logger = logging.getLogger(__name__)


class T2VTransformersEmbeddingGenerator(AbstractBatchEmbeddingGenerator):
    """T2V Transformers embedding generator for sentence-transformers models"""
    
    # Model configuration for multi-qa-MiniLM-L6-cos-v1
    MODEL_CONFIG = {
        "dimension": 384,
        "max_tokens": 512,
        "model_name": "multi-qa-MiniLM-L6-cos-v1"
    }
    
    def __init__(
        self, 
        endpoint: str = "http://t2v-transformers:8080",
        model_name: str = "multi-qa-MiniLM-L6-cos-v1",
        batch_size: int = 32,  # Smaller batch size for transformers
        max_retries: int = 3,
        timeout: int = 60
    ):
        super().__init__(model_name, batch_size)
        self.endpoint = endpoint.rstrip('/')
        self.max_retries = max_retries
        self.timeout = timeout
        
        # Use the predefined config
        self.config = self.MODEL_CONFIG.copy()
        self.config["model_name"] = model_name
    
    @property
    def embedding_dimension(self) -> int:
        return self.config["dimension"]
    
    @property
    def max_tokens(self) -> int:
        return self.config["max_tokens"]
    
    async def generate_single_embedding(
        self, 
        text: str,
        **kwargs
    ) -> List[float]:
        """Generate embedding for a single text"""
        # Truncate text if necessary
        text = self.truncate_text(text)
        
        for attempt in range(self.max_retries):
            try:
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                    payload = {"text": text}
                    
                    async with session.post(
                        f"{self.endpoint}/vectors",
                        json=payload,
                        headers={"Content-Type": "application/json"}
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            # Extract the embedding from the response
                            if isinstance(result, dict) and "vector" in result:
                                embedding = result["vector"]
                                if isinstance(embedding, list) and len(embedding) == self.embedding_dimension:
                                    return embedding
                                else:
                                    raise ValueError(f"Invalid embedding format or dimension. Expected {self.embedding_dimension}, got {len(embedding) if isinstance(embedding, list) else type(embedding)}")
                            else:
                                raise ValueError("No vector in response")
                        else:
                            error_text = await response.text()
                            raise RuntimeError(f"T2V Transformers API error {response.status}: {error_text}")
            
            except Exception as e:
                logger.warning(f"T2V Transformers embedding attempt {attempt + 1} failed: {str(e)}")
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        raise RuntimeError("All embedding attempts failed")

    async def generate_embeddings(
        self, 
        texts: List[str],
        **kwargs
    ) -> List[List[float]]:
        """Override to handle batch_size parameter correctly"""
        # Extract batch_size from kwargs to avoid parameter conflict
        batch_size = kwargs.pop('batch_size', self.batch_size)
        return await self.generate_embeddings_batch(texts, batch_size, **kwargs)
    
    async def generate_embeddings_batch(
        self,
        texts: List[str],
        batch_size: Optional[int] = None,
        **kwargs
    ) -> List[List[float]]:
        """Batch embedding generation with retry and truncation."""
        bs = batch_size or self.batch_size
        results: List[List[float]] = []

        # Process in sub-batches to respect service limits
        for i in range(0, len(texts), bs):
            batch_texts = [self.truncate_text(t) for t in texts[i:i+bs]]
            
            for attempt in range(self.max_retries):
                try:
                    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                        # Process each text individually since the API expects single text input
                        batch_embeddings = []
                        for text in batch_texts:
                            payload = {"text": text}
                            
                            async with session.post(
                                f"{self.endpoint}/vectors",
                                json=payload,
                                headers={"Content-Type": "application/json"}
                            ) as response:
                                if response.status == 200:
                                    result = await response.json()
                                    
                                    if isinstance(result, dict) and "vector" in result:
                                        embedding = result["vector"]
                                        if isinstance(embedding, list) and len(embedding) == self.embedding_dimension:
                                            batch_embeddings.append(embedding)
                                        else:
                                            raise ValueError(f"Invalid embedding format or dimension. Expected {self.embedding_dimension}, got {len(embedding) if isinstance(embedding, list) else type(embedding)}")
                                    else:
                                        raise ValueError("No vector in response")
                                else:
                                    error_text = await response.text()
                                    raise RuntimeError(f"T2V Transformers API error {response.status}: {error_text}")
                        
                        # Validate we got all embeddings
                        if len(batch_embeddings) != len(batch_texts):
                            raise ValueError(f"Expected {len(batch_texts)} embeddings, got {len(batch_embeddings)}")
                        
                        results.extend(batch_embeddings)
                        break
                
                except Exception as e:
                    logger.warning(f"T2V Transformers batch embedding attempt {attempt + 1} failed: {str(e)}")
                    if attempt == self.max_retries - 1:
                        raise
                    await asyncio.sleep(2 ** attempt)

        return results
    
    async def health_check(self) -> Dict[str, Any]:
        """Check if the T2V Transformers service is healthy"""
        try:
            # Try a simple embedding generation
            test_embedding = await self.generate_single_embedding("test")
            return {
                "status": "healthy",
                "model_name": self.model_name,
                "endpoint": self.endpoint,
                "embedding_dimension": len(test_embedding),
                "max_tokens": self.max_tokens
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "model_name": self.model_name,
                "endpoint": self.endpoint
            }
