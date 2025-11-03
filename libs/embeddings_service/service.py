"""
Embeddings Service Interface

This module provides a high-level interface for embedding generation services.
"""
import os
import logging
from typing import List, Dict, Any, Optional, Union

from .embedding_generators.openai_embeddings import OpenAIEmbeddingGenerator, AzureOpenAIEmbeddingGenerator
from .embedding_generators.t2v_transformers_embeddings import T2VTransformersEmbeddingGenerator
from .embedding_generators.base import AbstractEmbeddingGenerator

logger = logging.getLogger(__name__)


class EmbeddingGeneratorInterface:
    """
    High-level interface for embedding generation services
    
    This class provides a unified interface for different embedding providers
    and handles provider selection, configuration, and fallbacks.
    """
    
    def __init__(self, default_provider: str = "azure_openai"):
        """
        Initialize the embedding service interface
        
        Args:
            default_provider: Default embedding provider to use
        """
        self.default_provider = default_provider
        self.generators = {}
        self._initialized = False
        
        logger.info(f"Initialized EmbeddingGeneratorInterface with default provider: {default_provider}")
    
    def _get_azure_openai_generator(self, **kwargs) -> AzureOpenAIEmbeddingGenerator:
        """Get Azure OpenAI embedding generator"""
        api_key = kwargs.get("api_key") or os.getenv("AZURE_OPENAI_API_KEY")
        azure_endpoint = kwargs.get("azure_endpoint") or os.getenv("AZURE_OPENAI_ENDPOINT") or os.getenv("AZURE_OPENAI_BASE_URL")
        api_version = kwargs.get("api_version") or os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
        deployment_name = kwargs.get("deployment_name") or os.getenv("AZURE_OPENAI_EMBEDDINGS") or os.getenv("AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT", "text-embedding-3-large")
        model_name = kwargs.get("model_name") or os.getenv("AZURE_OPENAI_EMBEDDINGS") or deployment_name
        
        if not api_key or not azure_endpoint:
            raise ValueError("Azure OpenAI API key and endpoint are required")
        
        return AzureOpenAIEmbeddingGenerator(
            api_key=api_key,
            azure_endpoint=azure_endpoint,
            api_version=api_version,
            deployment_name=deployment_name,
            model_name=model_name,
            batch_size=kwargs.get("batch_size", 100),
            max_retries=kwargs.get("max_retries", 3),
            timeout=kwargs.get("timeout", 60)
        )
    
    def _get_openai_generator(self, **kwargs) -> OpenAIEmbeddingGenerator:
        """Get OpenAI embedding generator"""
        api_key = kwargs.get("api_key") or os.getenv("OPENAI_API_KEY")
        model_name = kwargs.get("model_name", "text-embedding-3-small")
        
        if not api_key:
            raise ValueError("OpenAI API key is required")
        
        return OpenAIEmbeddingGenerator(
            api_key=api_key,
            model_name=model_name,
            batch_size=kwargs.get("batch_size", 100),
            max_retries=kwargs.get("max_retries", 3),
            timeout=kwargs.get("timeout", 60)
        )
    
    def _get_t2v_transformers_generator(self, **kwargs) -> T2VTransformersEmbeddingGenerator:
        """Get T2V Transformers embedding generator"""
        # Default endpoint uses the docker service name
        endpoint = kwargs.get("endpoint") or os.getenv("T2V_TRANSFORMERS_ENDPOINT", "http://t2v-transformers:8080")
        model_name = kwargs.get("model_name", "multi-qa-MiniLM-L6-cos-v1")
        
        return T2VTransformersEmbeddingGenerator(
            endpoint=endpoint,
            model_name=model_name,
            batch_size=kwargs.get("batch_size", 32),  # Smaller batch size for transformers
            max_retries=kwargs.get("max_retries", 3),
            timeout=kwargs.get("timeout", 60)
        )
    
    def get_generator(self, provider: str, **kwargs) -> AbstractEmbeddingGenerator:
        """
        Get an embedding generator for the specified provider
        
        Args:
            provider: Provider name ("azure_openai", "openai", "t2v_transformers")
            **kwargs: Provider-specific configuration
            
        Returns:
            Embedding generator instance
        """
        cache_key = f"{provider}_{hash(str(sorted(kwargs.items())))}"
        
        if cache_key in self.generators:
            return self.generators[cache_key]
        
        if provider == "azure_openai":
            generator = self._get_azure_openai_generator(**kwargs)
        elif provider == "openai":
            generator = self._get_openai_generator(**kwargs)
        elif provider == "t2v_transformers":
            generator = self._get_t2v_transformers_generator(**kwargs)
        elif provider == "mock":
            generator = self._get_mock_generator(**kwargs)
        else:
            raise ValueError(f"Unsupported embedding provider: {provider}")
        
        self.generators[cache_key] = generator
        logger.info(f"Created {provider} embedding generator")
        
        return generator
    
    async def generate_single_embedding(self, text: str, provider: Optional[str] = None, **kwargs) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Text to embed
            provider: Optional provider override
            **kwargs: Additional configuration
            
        Returns:
            Embedding vector
        """
        generator = self.get_generator(provider or self.default_provider, **kwargs)
        return await generator.generate_single_embedding(text)
    
    async def generate_batch_embeddings(
        self, 
        texts: List[str], 
        provider: Optional[str] = None,
        model_name: Optional[str] = None,
        batch_size: Optional[int] = None,
        **kwargs
    ) -> List[List[float]]:
        """
        Generate embeddings for a batch of texts
        
        Args:
            texts: List of texts to embed
            provider: Optional provider override
            model_name: Optional model name override
            batch_size: Optional batch size override
            **kwargs: Additional configuration
            
        Returns:
            List of embedding vectors
        """
        # Override kwargs with provided parameters
        if model_name:
            kwargs["model_name"] = model_name
        if batch_size:
            kwargs["batch_size"] = batch_size
            
        generator = self.get_generator(provider or self.default_provider, **kwargs)
        return await generator.generate_embeddings(texts, **kwargs)