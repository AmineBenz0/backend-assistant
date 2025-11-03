"""
Parsing Service Interface

This module provides a high-level interface for parsing services.
"""
import os
import time
import logging
from typing import List, Dict, Any, Optional, Union

from .parsing_generators.llamacloud_parser import LlamaCloudParsingGenerator
from .parsing_generators.base import AbstractParsingGenerator
from .models import (
    ParsingConfig, 
    ParsingMethod, 
    ParsingResult, 
    ParsingRequest, 
    ParsingResponse,
    DocumentFormat,
    BatchParsingRequest,
    BatchParsingResult
)

logger = logging.getLogger(__name__)


class ParsingGeneratorInterface:
    """
    High-level interface for parsing services
    
    This class provides a unified interface for different parsing providers
    and handles provider selection, configuration, and fallbacks.
    """
    
    def __init__(self, default_provider: str = "llamacloud_parser"):
        """
        Initialize the parsing service interface
        
        Args:
            default_provider: Default parsing provider to use
        """
        self.default_provider = default_provider
        self.generators = {}
        self._initialized = False
        
        logger.info(f"Initialized ParsingGeneratorInterface with default provider: {default_provider}")
    
    def _get_llamacloud_generator(self, config: ParsingConfig) -> LlamaCloudParsingGenerator:
        """Get LlamaCloud parsing generator"""
        return LlamaCloudParsingGenerator(config)
    
    def get_generator(self, provider: str, config: ParsingConfig) -> AbstractParsingGenerator:
        """
        Get a parsing generator for the specified provider
        
        Args:
            provider: Provider name ("llamacloud", "llamaparser")
            config: Parsing configuration
            
        Returns:
            Parsing generator instance
        """
        cache_key = f"{provider}_{hash(str(sorted(config.dict().items())))}"
        
        if cache_key in self.generators:
            return self.generators[cache_key]
        
        if provider == "llamacloud_parser":
            generator = self._get_llamacloud_generator(config)
        else:
            raise ValueError(f"Unsupported parsing provider: {provider}. Supported providers: llamacloud_parser")
        
        self.generators[cache_key] = generator
        logger.info(f"Created {provider} parsing generator")
        
        return generator
    
    async def parse_document(
        self, 
        file_path: str, 
        config: Optional[ParsingConfig] = None,
        provider: Optional[str] = None,
        custom_metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> ParsingResult:
        """
        Parse a document using the specified or default provider
        
        Args:
            file_path: Path to the document file
            config: Parsing configuration (uses default if not provided)
            provider: Optional provider override
            custom_metadata: Optional custom metadata
            **kwargs: Additional configuration
            
        Returns:
            Parsing result with content and metadata
        """
        if config is None:
            config = ParsingConfig()
        
        generator = self.get_generator(provider or self.default_provider, config)
        return await generator.parse_document(file_path, custom_metadata, **kwargs)
    
    async def parse_document_to_markdown(
        self, 
        file_path: str,
        method: ParsingMethod = ParsingMethod.LLAMACLOUD,
        provider: Optional[str] = None,
        custom_metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> ParsingResult:
        """
        Parse a document to markdown format with simplified parameters
        
        Args:
            file_path: Path to the document file
            method: Parsing method to use
            provider: Optional provider override
            custom_metadata: Optional custom metadata
            **kwargs: Additional configuration
            
        Returns:
            Parsing result with markdown content
        """
        config = ParsingConfig(
            method=method,
            output_format="markdown",
            **kwargs
        )
        
        generator = self.get_generator(provider or self.default_provider, config)
        return await generator.parse_document_to_markdown(file_path, custom_metadata)
    
    async def parse_documents_batch(
        self, 
        file_paths: List[str],
        config: Optional[ParsingConfig] = None,
        provider: Optional[str] = None,
        custom_metadata_list: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> BatchParsingResult:
        """
        Parse multiple documents in batch
        
        Args:
            file_paths: List of file paths to parse
            config: Parsing configuration (uses default if not provided)
            provider: Optional provider override
            custom_metadata_list: Optional list of metadata for each document
            **kwargs: Additional configuration
            
        Returns:
            Batch parsing result
        """
        if config is None:
            config = ParsingConfig()
        
        generator = self.get_generator(provider or self.default_provider, config)
        
        results = []
        errors = []
        successful_files = 0
        failed_files = 0
        start_time = time.time()
        
        for i, file_path in enumerate(file_paths):
            try:
                doc_metadata = custom_metadata_list[i] if custom_metadata_list and i < len(custom_metadata_list) else None
                result = await generator.parse_document(file_path, doc_metadata, **kwargs)
                results.append(result)
                successful_files += 1
            except Exception as e:
                failed_files += 1
                error_info = {
                    "file_path": file_path,
                    "error": str(e),
                    "index": i
                }
                errors.append(error_info)
                logger.error(f"Failed to parse {file_path}: {e}")
        
        total_processing_time = time.time() - start_time
        
        return BatchParsingResult(
            results=results,
            total_files=len(file_paths),
            successful_files=successful_files,
            failed_files=failed_files,
            total_processing_time=total_processing_time,
            errors=errors
        )
    
    async def health_check(self, provider: Optional[str] = None) -> Dict[str, Any]:
        """
        Check if the parsing service is healthy
        
        Args:
            provider: Optional provider to check (checks default if not provided)
            
        Returns:
            Health check result
        """
        try:
            config = ParsingConfig()
            generator = self.get_generator(provider or self.default_provider, config)
            return await generator.health_check()
        except Exception as e:
            return {
                "status": "unhealthy",
                "provider": provider or self.default_provider,
                "error": str(e)
            }
    
    def get_available_providers(self) -> List[str]:
        """Get list of available parsing providers"""
        return ["llamacloud_parser"]
    
    def get_provider_info(self, provider: str) -> Dict[str, Any]:
        """
        Get information about a specific provider
        
        Args:
            provider: Provider name
            
        Returns:
            Dictionary with provider information
        """
        try:
            config = ParsingConfig()
            generator = self.get_generator(provider, config)
            
            return {
                "name": generator.name,
                "supported_formats": [fmt.value for fmt in generator.supported_formats],
                "requires_api_key": generator.requires_api_key,
                "class_name": generator.__class__.__name__,
                "module": generator.__class__.__module__
            }
        except Exception as e:
            return {
                "name": provider,
                "error": str(e)
            }
    
    def get_supported_formats(self, provider: Optional[str] = None) -> List[DocumentFormat]:
        """
        Get supported formats for a provider
        
        Args:
            provider: Provider name (uses default if not provided)
            
        Returns:
            List of supported document formats
        """
        try:
            config = ParsingConfig()
            generator = self.get_generator(provider or self.default_provider, config)
            return generator.supported_formats
        except Exception as e:
            logger.error(f"Failed to get supported formats: {e}")
            return []
    
    def close(self) -> None:
        """Close all generators and cleanup resources"""
        for generator in self.generators.values():
            if hasattr(generator, 'close'):
                generator.close()
        self.generators.clear()
        logger.info("Closed all parsing generators")


def create_parsing_from_config(config: Dict[str, Any]) -> ParsingGeneratorInterface:
    """
    Create a parsing service interface from configuration
    
    Args:
        config: Configuration dictionary with provider and settings
        
    Returns:
        ParsingGeneratorInterface instance
    """
    provider = config.get("provider", "llamacloud_parser")
    parsing_interface = ParsingGeneratorInterface(default_provider=provider)
    
    # Set up any provider-specific configuration if needed
    if provider == "llamacloud_parser":
        # LlamaCloud configuration is handled by the generator itself
        pass
    else:
        logger.warning(f"Unknown provider '{provider}', using default 'llamacloud_parser'")
        parsing_interface.default_provider = "llamacloud_parser"
    
    return parsing_interface


def create_sync_parsing_adapter(api_key: str, base_url: str = None, verify_ssl: bool = False) -> LlamaCloudParsingGenerator:
    """
    Create a synchronous parsing adapter for Celery workers
    
    Args:
        api_key: LlamaCloud API key
        base_url: LlamaCloud base URL (optional)
        verify_ssl: Whether to verify SSL certificates
        
    Returns:
        LlamaCloudParsingGenerator instance
    """
    from .models import ParsingConfig, ParsingMethod
    
    config = ParsingConfig(
        method=ParsingMethod.LLAMACLOUD,
        api_key=api_key,
        base_url=base_url or "https://api.cloud.llamaindex.ai",
        verify_ssl=verify_ssl,
        result_type="markdown"
    )
    
    return LlamaCloudParsingGenerator(config)
