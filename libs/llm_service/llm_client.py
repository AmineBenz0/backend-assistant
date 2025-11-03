"""
LLM Service client abstraction.

This module provides an async client that prefers Azure OpenAI by default
and can optionally fall back to OpenAI. It is separated from graph_builder_service
so other services can reuse it.
"""
import asyncio
import logging
import os
from typing import Dict, Any, Optional, List
import openai
from openai import AsyncOpenAI, AsyncAzureOpenAI

logger = logging.getLogger(__name__)


class SimpleLLMClient:
    """
    Simple LLM client that directly uses Azure OpenAI with optional OpenAI fallback.
    
    This client is designed to work with the pipeline_key as prompt_key pattern,
    where pipeline steps can be either Python classes or prompt-based LLM calls.
    """
    
    def __init__(
        self,
        azure_api_key: Optional[str] = None,
        azure_api_base: Optional[str] = None,
        azure_api_version: Optional[str] = None,
        default_model: str = "gpt-4o",
        fallback_to_openai: bool = False,
        openai_api_key: Optional[str] = None
    ):
        """
        Initialize the simple LLM client
        
        Args:
            azure_api_key: Azure OpenAI API key
            azure_api_base: Azure OpenAI API base URL
            azure_api_version: Azure OpenAI API version
            default_model: Default model to use
            fallback_to_openai: Whether to fallback to OpenAI if Azure fails
            openai_api_key: OpenAI API key for fallback
        """
        self.default_model = default_model
        self.fallback_to_openai = fallback_to_openai
        self._initialized = False
        
        # Get configuration from environment if not provided
        self.azure_config = {
            "api_key": azure_api_key or os.getenv("AZURE_OPENAI_API_KEY"),
            "api_base": azure_api_base or os.getenv("AZURE_OPENAI_ENDPOINT") or os.getenv("AZURE_OPENAI_BASE_URL"),
            "api_version": azure_api_version or os.getenv("AZURE_OPENAI_API_VERSION", "2025-03-01-preview")
        }
        self.azure_secondary_key = os.getenv("AZURE_OPENAI_API_KEY_SECONDARY")
        
        self.openai_config = {
            "api_key": openai_api_key or os.getenv("OPENAI_API_KEY")
        }
        
        # Initialize clients
        self.azure_client = None
        self.openai_client = None
    
    async def initialize(self) -> None:
        """Initialize the LLM clients"""
        if self._initialized:
            return
        
        try:
            # Initialize Azure OpenAI client if configured
            if self.azure_config["api_key"] and self.azure_config["api_base"]:
                # Use the proper Azure OpenAI client
                azure_endpoint = self.azure_config["api_base"]
                if not azure_endpoint.endswith('/'):
                    azure_endpoint += '/'
                
                self.azure_client = AsyncAzureOpenAI(
                    api_key=self.azure_config["api_key"],
                    azure_endpoint=azure_endpoint,
                    api_version=self.azure_config["api_version"]
                )
                logger.info(f"Azure OpenAI client initialized with endpoint: {azure_endpoint}")
            
            # Initialize OpenAI client if configured
            if self.openai_config["api_key"]:
                self.openai_client = AsyncOpenAI(
                    api_key=self.openai_config["api_key"]
                )
                logger.info("OpenAI client initialized")
            
            if not self.azure_client and not self.openai_client:
                raise ValueError("No LLM clients could be initialized")
            
            self._initialized = True
            logger.info("LLM client initialization completed")
            
        except Exception as e:
            logger.error(f"Failed to initialize LLM client: {str(e)}")
            raise
    
    async def call_llm(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: Optional[int] = 4000,
        **kwargs
    ) -> str:
        """
        Call LLM with the given prompt
        
        Args:
            prompt: The prompt to send
            model: Model to use (defaults to self.default_model)
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            **kwargs: Additional arguments passed to the API
            
        Returns:
            The generated text response
        """
        if not self._initialized:
            await self.initialize()
        
        model = model or self.default_model
        
        try:
            # Try Azure OpenAI first
            if self.azure_client:
                try:
                    response = await self.azure_client.chat.completions.create(
                        model=model,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=temperature,
                        max_tokens=max_tokens,
                        **kwargs
                    )
                    return response.choices[0].message.content.strip()
                except Exception as azure_error:
                    logger.warning(f"Azure OpenAI call failed: {azure_error}")
                    # Retry once using the secondary Azure key if available
                    if self.azure_secondary_key and self.azure_secondary_key != self.azure_config.get("api_key"):
                        try:
                            logger.info("Retrying Azure OpenAI with secondary API key")
                            # Recreate client with secondary key
                            endpoint = self.azure_config["api_base"]
                            if not endpoint.endswith('/'):
                                endpoint += '/'
                            self.azure_client = AsyncAzureOpenAI(
                                api_key=self.azure_secondary_key,
                                azure_endpoint=endpoint,
                                api_version=self.azure_config["api_version"]
                            )
                            response = await self.azure_client.chat.completions.create(
                                model=model,
                                messages=[{"role": "user", "content": prompt}],
                                temperature=temperature,
                                max_tokens=max_tokens,
                                **kwargs
                            )
                            return response.choices[0].message.content.strip()
                        except Exception as secondary_error:
                            logger.error(f"Secondary key retry failed: {secondary_error}")
                            # Restore to primary client for future attempts
                            endpoint = self.azure_config["api_base"]
                            if not endpoint.endswith('/'):
                                endpoint += '/'
                            self.azure_client = AsyncAzureOpenAI(
                                api_key=self.azure_config["api_key"],
                                azure_endpoint=endpoint,
                                api_version=self.azure_config["api_version"]
                            )
                            raise secondary_error
                    # No secondary key available, re-raise
                    raise azure_error
            
            # Fallback to OpenAI if Azure failed and fallback is enabled
            if self.openai_client and self.fallback_to_openai:
                response = await self.openai_client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                )
                return response.choices[0].message.content.strip()
            
            raise ValueError("No available LLM clients")
            
        except Exception as e:
            logger.error(f"LLM call failed: {str(e)}")
            raise
    
    def call_llm_sync(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: Optional[int] = 4000,
        json_object: bool = False,
        **kwargs
    ) -> str:
        """
        Synchronous LLM call for Celery compatibility.
        
        Args:
            prompt: The prompt to send
            model: Model to use (defaults to self.default_model)
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            json_object: Whether to request JSON object response format
            **kwargs: Additional arguments passed to the API
            
        Returns:
            The generated text response
        """
        import os
        from openai import AzureOpenAI
        
        model = model or self.default_model
        
        try:
            # Initialize synchronous Azure OpenAI client
            client = AzureOpenAI(
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2025-03-01-preview"),
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
            )
            
            # Call Azure OpenAI synchronously
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object" if json_object else "text"},
                **kwargs
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Synchronous LLM call failed: {str(e)}")
            raise

    async def close(self) -> None:
        """Close the LLM clients"""
        try:
            if self.azure_client:
                await self.azure_client.close()
            if self.openai_client:
                await self.openai_client.close()
            self._initialized = False
            logger.info("LLM clients closed")
        except Exception as e:
            logger.warning(f"Warning: Error closing LLM clients: {e}")
        
        
# Backward compatibility alias used elsewhere in the repo
class PreprocessingLLMClient(SimpleLLMClient):
    pass
