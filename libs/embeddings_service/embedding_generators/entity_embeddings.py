"""
Entity-specific embedding generator for GraphRAG processing

This module handles embedding generation specifically for entities extracted from GraphRAG,
providing specialized handling for entity names, descriptions, and properties.
"""
import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple
import os
from datetime import datetime

from .base import AbstractEmbeddingGenerator
from ..models import EntityEmbedding
from .openai_embeddings import OpenAIEmbeddingGenerator, AzureOpenAIEmbeddingGenerator

logger = logging.getLogger(__name__)


class EntityEmbeddingGenerator(AbstractEmbeddingGenerator):
    """
    Specialized embedding generator for GraphRAG entities
    
    This generator creates embeddings specifically optimized for entity data,
    combining entity names, descriptions, and contextual information.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "text-embedding-3-large",
        batch_size: int = 100,
        max_retries: int = 3,
        timeout: float = 30.0,
        # Azure OpenAI support
        azure_api_key: Optional[str] = None,
        azure_endpoint: Optional[str] = None,
        azure_api_version: Optional[str] = None,
        azure_deployment: Optional[str] = None,
        provider: Optional[str] = None,
    ):
        super().__init__(model, batch_size)
        
        # Resolve provider and credentials from args or environment
        resolved_provider = provider
        if not resolved_provider:
            if (azure_api_key or os.getenv("AZURE_OPENAI_API_KEY")) and (azure_endpoint or os.getenv("AZURE_OPENAI_ENDPOINT") or os.getenv("AZURE_OPENAI_BASE_URL")):
                resolved_provider = "azure_openai"
            else:
                resolved_provider = "openai"
        
        if resolved_provider == "azure_openai":
            a_key = azure_api_key or os.getenv("AZURE_OPENAI_API_KEY")
            a_endpoint = azure_endpoint or os.getenv("AZURE_OPENAI_ENDPOINT") or os.getenv("AZURE_OPENAI_BASE_URL")
            a_version = azure_api_version or os.getenv("AZURE_OPENAI_API_VERSION", "2025-03-01-preview")
            a_deployment = azure_deployment or os.getenv("AZURE_OPENAI_EMBEDDINGS") or os.getenv("AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT", model)
            
            if not a_key or not a_endpoint:
                raise ValueError("Azure OpenAI credentials not provided for EntityEmbeddingGenerator")
            
            self.openai_generator = AzureOpenAIEmbeddingGenerator(
                api_key=a_key,
                azure_endpoint=a_endpoint,
                api_version=a_version,
                deployment_name=a_deployment,
                model_name=model,
                batch_size=batch_size,
                max_retries=max_retries,
                timeout=timeout,
            )
            logger.info(f"Initialized EntityEmbeddingGenerator with Azure OpenAI deployment: {a_deployment}")
        else:
            oai_key = api_key or os.getenv("OPENAI_API_KEY")
            if not oai_key:
                raise ValueError("OPENAI_API_KEY not provided for EntityEmbeddingGenerator")
            # Use OpenAI embedding generator as the underlying implementation
            self.openai_generator = OpenAIEmbeddingGenerator(
                api_key=oai_key,
                model_name=model,
                batch_size=batch_size,
                max_retries=max_retries,
                timeout=timeout
            )
            logger.info(f"Initialized EntityEmbeddingGenerator with OpenAI model: {model}")
    
    @property
    def embedding_dimension(self) -> int:
        """Return the dimension of embeddings produced by this generator"""
        return self.openai_generator.embedding_dimension
    
    @property
    def max_tokens(self) -> int:
        """Return the maximum number of tokens this model can handle"""
        return self.openai_generator.max_tokens
    
    async def generate_single_embedding(
        self,
        text: str,
        **kwargs
    ) -> List[float]:
        """Generate a single embedding by delegating to the underlying provider"""
        return await self.openai_generator.generate_single_embedding(text, **kwargs)
    
    async def generate_embeddings(
        self, 
        texts: List[str],
        **kwargs
    ) -> List[List[float]]:
        """Generate embeddings for a list of texts (delegates to OpenAI)"""
        return await self.openai_generator.generate_embeddings(texts, **kwargs)
    
    async def generate_entity_embeddings(
        self,
        entities: List[Dict[str, Any]],
        include_descriptions: bool = True,
        include_properties: bool = False,
        context_window: int = 512
    ) -> List[EntityEmbedding]:
        """
        Generate embeddings specifically for GraphRAG entities
        
        Args:
            entities: List of entity dictionaries with name, type, description, etc.
            include_descriptions: Whether to include entity descriptions in embedding text
            include_properties: Whether to include entity properties in embedding text
            context_window: Maximum context length for embedding text
            
        Returns:
            List of EntityEmbedding objects with embeddings and metadata
        """
        logger.info(f"🔍 Generating embeddings for {len(entities)} entities")
        
        if not entities:
            return []
        
        try:
            # Prepare entity texts for embedding
            entity_texts = []
            entity_metadata = []
            
            for entity in entities:
                entity_text, metadata = self._prepare_entity_text(
                    entity, 
                    include_descriptions=include_descriptions,
                    include_properties=include_properties,
                    context_window=context_window
                )
                entity_texts.append(entity_text)
                entity_metadata.append(metadata)
            
            # Generate embeddings using the underlying OpenAI generator
            embeddings = await self.openai_generator.generate_embeddings(entity_texts)
            
            # Create EntityEmbedding objects
            entity_embeddings = []
            for i, embedding in enumerate(embeddings):
                entity_embedding = EntityEmbedding(
                    entity_id=entity_metadata[i]["entity_id"],
                    entity_name=entity_metadata[i]["entity_name"],
                    entity_type=entity_metadata[i]["entity_type"],
                    embedding=embedding,
                    embedding_model=self.model_name,
                    text_used=entity_texts[i],
                    metadata=entity_metadata[i],
                    created_at=datetime.now()
                )
                entity_embeddings.append(entity_embedding)
            
            logger.info(f"✅ Generated embeddings for {len(entity_embeddings)} entities")
            return entity_embeddings
            
        except Exception as e:
            logger.error(f"❌ Failed to generate entity embeddings: {str(e)}")
            raise
    
    def _prepare_entity_text(
        self,
        entity: Dict[str, Any],
        include_descriptions: bool = True,
        include_properties: bool = False,
        context_window: int = 512
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Prepare entity text for embedding generation
        
        Args:
            entity: Entity dictionary
            include_descriptions: Whether to include descriptions
            include_properties: Whether to include properties
            context_window: Maximum text length
            
        Returns:
            Tuple of (prepared_text, metadata)
        """
        # Extract entity information
        entity_id = entity.get("entity_id", entity.get("id", "unknown"))
        entity_name = entity.get("name", entity.get("title", "Unknown Entity"))
        entity_type = entity.get("type", "ENTITY")
        entity_description = entity.get("description", "")
        entity_properties = entity.get("properties", {})
        
        # Build entity text for embedding
        text_parts = []
        
        # Always include entity name and type
        text_parts.append(f"Entity: {entity_name}")
        text_parts.append(f"Type: {entity_type}")
        
        # Include description if available and requested
        if include_descriptions and entity_description:
            text_parts.append(f"Description: {entity_description}")
        
        # Include relevant properties if requested
        if include_properties and entity_properties:
            property_texts = []
            for key, value in entity_properties.items():
                if key in ["degree", "community", "level", "rank"]:  # Important GraphRAG properties
                    property_texts.append(f"{key}: {value}")
            
            if property_texts:
                text_parts.append(f"Properties: {', '.join(property_texts)}")
        
        # Combine text parts
        full_text = " | ".join(text_parts)
        
        # Truncate if necessary
        if len(full_text) > context_window:
            full_text = full_text[:context_window-3] + "..."
        
        # Prepare metadata
        metadata = {
            "entity_id": entity_id,
            "entity_name": entity_name,
            "entity_type": entity_type,
            "has_description": bool(entity_description),
            "has_properties": bool(entity_properties),
            "text_length": len(full_text),
            "original_entity": entity
        }
        
        return full_text, metadata
    
    async def batch_generate_entity_embeddings(
        self,
        entities: List[Dict[str, Any]],
        batch_size: Optional[int] = None,
        **kwargs
    ) -> List[EntityEmbedding]:
        """
        Generate entity embeddings in batches for better performance
        
        Args:
            entities: List of entities to process
            batch_size: Optional batch size override
            **kwargs: Additional arguments for generate_entity_embeddings
            
        Returns:
            List of all EntityEmbedding objects
        """
        batch_size = batch_size or self.batch_size
        
        if len(entities) <= batch_size:
            return await self.generate_entity_embeddings(entities, **kwargs)
        
        logger.info(f"🔄 Processing {len(entities)} entities in batches of {batch_size}")
        
        all_embeddings = []
        
        for i in range(0, len(entities), batch_size):
            batch = entities[i:i + batch_size]
            logger.info(f"📊 Processing batch {i//batch_size + 1}/{(len(entities) + batch_size - 1)//batch_size}")
            
            try:
                batch_embeddings = await self.generate_entity_embeddings(batch, **kwargs)
                all_embeddings.extend(batch_embeddings)
                
                # Small delay between batches to avoid rate limiting
                if i + batch_size < len(entities):
                    await asyncio.sleep(0.1)
                    
            except Exception as e:
                logger.error(f"❌ Failed to process batch {i//batch_size + 1}: {str(e)}")
                # Continue with next batch
                continue
        
        logger.info(f"✅ Completed batch processing: {len(all_embeddings)} entity embeddings generated")
        return all_embeddings
