"""
Tokenizer utility functions for Chonkie chunking generators.

This module provides helper functions to get tokenizers that match embedding models
using Chonkie's embedding classes with get_tokenizer_or_token_counter().
"""
import os
import logging
from typing import Optional, Any

logger = logging.getLogger(__name__)


def get_tokenizer_for_embedding_model(provider: str, model: str, **kwargs) -> Optional[Any]:
    """
    Get tokenizer that matches the embedding model.
    Uses Chonkie's embedding classes with get_tokenizer_or_token_counter().
    
    Args:
        provider: Embedding provider ("azure_openai", "openai", etc.)
        model: Model name (e.g., "text-embedding-3-large")
        **kwargs: Additional provider-specific parameters
        
    Returns:
        Tokenizer instance or None if not available
    """
    logger.info(f"🔍 DEBUG: get_tokenizer_for_embedding_model called with provider='{provider}', model='{model}'")
    logger.info(f"🔍 DEBUG: kwargs={kwargs}")
    
    try:
        if provider == "azure_openai":
            logger.info("🔍 DEBUG: Processing azure_openai provider")
            
            # Check environment variables
            azure_endpoint = kwargs.get("azure_endpoint") or os.getenv("AZURE_OPENAI_ENDPOINT")
            azure_api_key = kwargs.get("azure_api_key") or os.getenv("AZURE_OPENAI_API_KEY")
            deployment = kwargs.get("deployment") or os.getenv("AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT")
            
            logger.info(f"🔍 DEBUG: azure_endpoint={azure_endpoint}")
            logger.info(f"🔍 DEBUG: azure_api_key={'Set' if azure_api_key else 'Not set'}")
            logger.info(f"🔍 DEBUG: deployment={deployment}")
            logger.info(f"🔍 DEBUG: model={model}")
            
            if not azure_endpoint:
                logger.error("🔍 DEBUG: azure_endpoint is None or empty")
                return None
            
            if not azure_api_key:
                logger.error("🔍 DEBUG: azure_api_key is None or empty")
                return None
            
            logger.info("🔍 DEBUG: Importing AzureOpenAIEmbeddings")
            from chonkie.embeddings.azure_openai import AzureOpenAIEmbeddings
            
            logger.info("🔍 DEBUG: Creating AzureOpenAIEmbeddings instance")
            embeddings = AzureOpenAIEmbeddings(
                azure_endpoint=azure_endpoint,
                azure_api_key=azure_api_key,
                model=model,
                deployment=deployment
            )
            logger.info(f"🔍 DEBUG: AzureOpenAIEmbeddings created successfully: {type(embeddings)}")
            
            logger.info("🔍 DEBUG: Calling get_tokenizer_or_token_counter()")
            tokenizer = embeddings.get_tokenizer_or_token_counter()
            logger.info(f"🔍 DEBUG: get_tokenizer_or_token_counter() returned: {type(tokenizer)} - {tokenizer}")
            
            if tokenizer is None:
                logger.error("🔍 DEBUG: get_tokenizer_or_token_counter() returned None!")
                # Try alternative methods
                logger.info("🔍 DEBUG: Trying alternative tokenizer retrieval methods")
                try:
                    if hasattr(embeddings, '_tokenizer'):
                        alt_tokenizer = embeddings._tokenizer
                        logger.info(f"🔍 DEBUG: _tokenizer attribute: {type(alt_tokenizer)} - {alt_tokenizer}")
                        if alt_tokenizer is not None:
                            logger.info("🔍 DEBUG: Using _tokenizer attribute as fallback")
                            return alt_tokenizer
                except Exception as e:
                    logger.error(f"🔍 DEBUG: Failed to access _tokenizer attribute: {e}")
                
                logger.error("🔍 DEBUG: All tokenizer retrieval methods failed")
                return None
            
            logger.info(f"🔍 DEBUG: Successfully retrieved tokenizer: {type(tokenizer)}")
            return tokenizer
            
        elif provider == "openai":
            logger.info("🔍 DEBUG: Processing openai provider")
            from chonkie.embeddings.openai import OpenAIEmbeddings
            embeddings = OpenAIEmbeddings(
                api_key=kwargs.get("api_key") or os.getenv("OPENAI_API_KEY"),
                model=model
            )
            logger.info("🔍 DEBUG: Calling get_tokenizer_or_token_counter() for OpenAI")
            tokenizer = embeddings.get_tokenizer_or_token_counter()
            logger.info(f"🔍 DEBUG: OpenAI tokenizer result: {type(tokenizer)} - {tokenizer}")
            return tokenizer
        else:
            logger.warning(f"🔍 DEBUG: Unknown provider {provider}, using default tokenizer")
            return None
    except Exception as e:
        logger.error(f"🔍 DEBUG: Exception in get_tokenizer_for_embedding_model: {e}")
        import traceback
        logger.error(f"🔍 DEBUG: Traceback: {traceback.format_exc()}")
        return None


def get_default_tokenizer() -> Optional[Any]:
    """
    Get default tokenizer using Azure OpenAI configuration.
    
    Returns:
        Default tokenizer instance or None if not available
    """
    return get_tokenizer_for_embedding_model(
        provider="azure_openai",
        model="text-embedding-3-large"
    )
