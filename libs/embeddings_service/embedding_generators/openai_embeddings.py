"""
OpenAI embedding generator implementation
"""
import asyncio
from typing import List, Dict, Any, Optional
import logging

from .base import AbstractBatchEmbeddingGenerator

logger = logging.getLogger(__name__)


class OpenAIEmbeddingGenerator(AbstractBatchEmbeddingGenerator):
    """OpenAI embedding generator"""
    
    # Model configurations
    MODEL_CONFIGS = {
        "text-embedding-3-small": {
            "dimension": 1536,
            "max_tokens": 8191,
            "cost_per_1k": 0.00002
        },
        "text-embedding-3-large": {
            "dimension": 3072,
            "max_tokens": 8191,
            "cost_per_1k": 0.00013
        },
        "text-embedding-ada-002": {
            "dimension": 1536,
            "max_tokens": 8191,
            "cost_per_1k": 0.0001
        }
    }
    
    def __init__(
        self, 
        api_key: str,
        model_name: str = "text-embedding-3-small",
        batch_size: int = 100,
        max_retries: int = 3,
        timeout: int = 60
    ):
        super().__init__(model_name, batch_size)
        self.api_key = api_key
        self.max_retries = max_retries
        self.timeout = timeout
        
        if model_name not in self.MODEL_CONFIGS:
            raise ValueError(f"Unsupported OpenAI model: {model_name}")
        
        self.config = self.MODEL_CONFIGS[model_name]
    
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
        try:
            import openai
        except ImportError:
            raise ImportError("openai package is required. Install with: pip install openai")
        
        client = openai.AsyncOpenAI(api_key=self.api_key)
        
        # Truncate text if necessary
        text = self.truncate_text(text)
        
        for attempt in range(self.max_retries):
            try:
                response = await client.embeddings.create(
                    model=self.model_name,
                    input=text,
                    timeout=self.timeout
                )
                return response.data[0].embedding
            
            except Exception as e:
                logger.warning(f"OpenAI embedding attempt {attempt + 1} failed: {str(e)}")
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        raise RuntimeError("All embedding attempts failed")

    async def generate_embeddings_batch(
        self,
        texts: List[str],
        batch_size: Optional[int] = None,
        **kwargs
    ) -> List[List[float]]:
        """Batch embedding generation with retry and truncation."""
        try:
            import openai
        except ImportError:
            raise ImportError("openai package is required. Install with: pip install openai")

        client = openai.AsyncOpenAI(api_key=self.api_key)
        bs = batch_size or self.batch_size
        results: List[List[float]] = []

        # Process in sub-batches to respect provider limits
        for i in range(0, len(texts), bs):
            batch_texts = [self.truncate_text(t) for t in texts[i:i+bs]]
            for attempt in range(self.max_retries):
                try:
                    response = await client.embeddings.create(
                        model=self.model_name,
                        input=batch_texts,
                        timeout=self.timeout
                    )
                    results.extend([d.embedding for d in response.data])
                    break
                except Exception as e:
                    logger.warning(f"OpenAI batch embedding attempt {attempt + 1} failed: {str(e)}")
                    if attempt == self.max_retries - 1:
                        raise
                    await asyncio.sleep(2 ** attempt)

        return results


class AzureOpenAIEmbeddingGenerator(AbstractBatchEmbeddingGenerator):
    """Azure OpenAI embedding generator"""
    
    def __init__(
        self, 
        api_key: str,
        azure_endpoint: str,
        api_version: str = "2024-02-01",
        deployment_name: str = "text-embedding-ada-002",
        model_name: str = "text-embedding-ada-002",
        batch_size: int = 100,
        max_retries: int = 3,
        timeout: int = 60
    ):
        super().__init__(model_name, batch_size)
        self.api_key = api_key
        self.azure_endpoint = azure_endpoint
        self.api_version = api_version
        self.deployment_name = deployment_name
        self.max_retries = max_retries
        self.timeout = timeout
        
        # Use OpenAI model configs
        if model_name in OpenAIEmbeddingGenerator.MODEL_CONFIGS:
            self.config = OpenAIEmbeddingGenerator.MODEL_CONFIGS[model_name]
        else:
            # Default config for custom models
            self.config = {
                "dimension": 1536,
                "max_tokens": 8191,
                "cost_per_1k": 0.0001
            }
    
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
        try:
            import openai
        except ImportError:
            raise ImportError("openai package is required. Install with: pip install openai")
        
        client = openai.AsyncAzureOpenAI(
            api_key=self.api_key,
            azure_endpoint=self.azure_endpoint,
            api_version=self.api_version
        )
        
        # Truncate text if necessary
        text = self.truncate_text(text)
        
        for attempt in range(self.max_retries):
            try:
                response = await client.embeddings.create(
                    model=self.deployment_name,
                    input=text,
                    timeout=self.timeout
                )
                return response.data[0].embedding
            
            except Exception as e:
                logger.warning(f"Azure OpenAI embedding attempt {attempt + 1} failed: {str(e)}")
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)
        
        raise RuntimeError("All embedding attempts failed")

    async def generate_embeddings_batch(
        self,
        texts: List[str],
        batch_size: Optional[int] = None,
        **kwargs
    ) -> List[List[float]]:
        """Batch embedding generation against Azure OpenAI deployments."""
        try:
            import openai
        except ImportError:
            raise ImportError("openai package is required. Install with: pip install openai")

        client = openai.AsyncAzureOpenAI(
            api_key=self.api_key,
            azure_endpoint=self.azure_endpoint,
            api_version=self.api_version
        )

        bs = batch_size or self.batch_size
        results: List[List[float]] = []

        for i in range(0, len(texts), bs):
            batch_texts = [self.truncate_text(t) for t in texts[i:i+bs]]
            for attempt in range(self.max_retries):
                try:
                    response = await client.embeddings.create(
                        model=self.deployment_name,
                        input=batch_texts,
                        timeout=self.timeout
                    )
                    results.extend([d.embedding for d in response.data])
                    break
                except Exception as e:
                    logger.warning(f"Azure OpenAI batch embedding attempt {attempt + 1} failed: {str(e)}")
                    if attempt == self.max_retries - 1:
                        raise
                    await asyncio.sleep(2 ** attempt)

        return results

