"""
Text Unit Processor Helper for GraphRAG Final Text Units

This helper implements the create_final_text_units step from GraphRAG pipeline following kotaemon's approach:
- Create bidirectional mapping: text_unit_id → relationship_ids and entity_ids
- Preserve embeddings for text units and maintain semantic connections
- Maintain bidirectional references between text units and graph elements
"""
import logging
from typing import List, Dict, Optional, Any

from ..models import TextUnit

logger = logging.getLogger(__name__)


class TextUnitProcessor:
    """
    Helper class for processing GraphRAG text units following kotaemon's approach.
    
    This class handles the create_final_text_units step which creates bidirectional
    mappings between text units and graph elements (entities and relationships).
    """
    
    def __init__(self):
        """Initialize the text unit processor"""
        self.logger = logger
    
    async def create_base_text_units(self, documents: List[Any]) -> List[Dict[str, Any]]:
        """
        Create base text units from documents (Step 1 of GraphRAG pipeline).
        
        This implements the create_base_text_units step following kotaemon's approach:
        - Split input text into atomic text units
        - Tokenization and cleaning
        - Metadata assignment (doc_id, n_tokens, chunk_id)
        
        Args:
            documents: List of DocumentChunk objects to process
            
        Returns:
            List of base text unit dictionaries
        """
        self.logger.info(f"Creating base text units from {len(documents)} documents")
        
        text_units = []
        
        for doc_idx, document in enumerate(documents):
            # Extract text content
            if hasattr(document, 'text'):
                text_content = document.text
                doc_id = getattr(document, 'chunk_id', f"doc_{doc_idx}")
                metadata = getattr(document, 'metadata', None)
            else:
                # Handle dictionary format
                text_content = document.get('text', '')
                doc_id = document.get('chunk_id', f"doc_{doc_idx}")
                metadata = document.get('metadata', {})
            
            # Simple text splitting - split by sentences or paragraphs
            # This is a basic implementation, can be enhanced with more sophisticated splitting
            sentences = self._split_text_into_units(text_content)
            
            for unit_idx, sentence in enumerate(sentences):
                if not sentence.strip():
                    continue
                
                # Create text unit
                text_unit = {
                    "text_unit_id": f"{doc_id}_unit_{unit_idx}",
                    "text": sentence.strip(),
                    "doc_id": doc_id,
                    "chunk_id": f"{doc_id}_chunk_{unit_idx}",
                    "n_tokens": len(sentence.split()),  # Simple token count
                    "document_ids": [doc_id],
                    "entity_ids": [],
                    "relationship_ids": [],
                    "covariate_ids": [],
                    "text_embedding": None,
                    "attributes": {
                        "source_document": getattr(metadata, 'file_name', '') if metadata else '',
                        "unit_index": unit_idx,
                        "doc_index": doc_idx,
                        "processing_step": "create_base_text_units"
                    }
                }
                
                text_units.append(text_unit)
        
        self.logger.info(f"Successfully created {len(text_units)} base text units")
        return text_units
    
    def _split_text_into_units(self, text: str, max_length: int = 500) -> List[str]:
        """
        Split text into smaller units (sentences or chunks).
        
        Args:
            text: Input text to split
            max_length: Maximum length per unit
            
        Returns:
            List of text units
        """
        # Simple sentence splitting
        import re
        
        # Split by sentence endings
        sentences = re.split(r'[.!?]+', text)
        
        units = []
        current_unit = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # If adding this sentence would exceed max_length, start a new unit
            if current_unit and len(current_unit + " " + sentence) > max_length:
                if current_unit:
                    units.append(current_unit)
                current_unit = sentence
            else:
                if current_unit:
                    current_unit += " " + sentence
                else:
                    current_unit = sentence
        
        # Add the last unit
        if current_unit:
            units.append(current_unit)
        
        # If no sentences found, split by length
        if not units and text.strip():
            words = text.split()
            current_unit = ""
            
            for word in words:
                if current_unit and len(current_unit + " " + word) > max_length:
                    units.append(current_unit)
                    current_unit = word
                else:
                    if current_unit:
                        current_unit += " " + word
                    else:
                        current_unit = word
            
            if current_unit:
                units.append(current_unit)
        
        return units
    
    def create_final_text_units(
        self,
        base_text_units: List[TextUnit],
        entity_ids: Optional[List[str]] = None,
        relationship_ids: Optional[List[str]] = None,
        entity_text_mapping: Optional[Dict[str, List[str]]] = None,
        relationship_text_mapping: Optional[Dict[str, List[str]]] = None
    ) -> List[TextUnit]:
        """
        Create final text units with entity and relationship mappings.
        
        This implements the create_final_text_units step from GraphRAG pipeline following
        kotaemon's approach:
        - Create bidirectional mapping: text_unit_id → relationship_ids and entity_ids
        - Preserve embeddings for text units and maintain semantic connections
        - Maintain bidirectional references between text units and graph elements
        
        Args:
            base_text_units: List of base text units from create_base_text_units step
            entity_ids: Optional list of all entity IDs in the graph
            relationship_ids: Optional list of all relationship IDs in the graph
            entity_text_mapping: Optional mapping of entity_id -> list of text_unit_ids
            relationship_text_mapping: Optional mapping of relationship_id -> list of text_unit_ids
            
        Returns:
            List of final text units with bidirectional mappings
        """
        self.logger.info(f"Creating final text units from {len(base_text_units)} base text units")
        
        # Initialize mappings if not provided
        entity_ids = entity_ids or []
        relationship_ids = relationship_ids or []
        entity_text_mapping = entity_text_mapping or {}
        relationship_text_mapping = relationship_text_mapping or {}
        
        # Create reverse mappings: text_unit_id -> entity_ids and relationship_ids
        text_unit_entities = self._create_text_unit_entity_mapping(
            base_text_units, entity_text_mapping
        )
        text_unit_relationships = self._create_text_unit_relationship_mapping(
            base_text_units, relationship_text_mapping
        )
        
        final_text_units = []
        
        for text_unit in base_text_units:
            # Handle both dictionary and object formats
            if isinstance(text_unit, dict):
                text_unit_id = text_unit.get('text_unit_id')
                text = text_unit.get('text', '')
                doc_id = text_unit.get('doc_id', '')
                chunk_id = text_unit.get('chunk_id', '')
                n_tokens = text_unit.get('n_tokens', 0)
                document_ids = text_unit.get('document_ids', [])
                covariate_ids = text_unit.get('covariate_ids', [])
                text_embedding = text_unit.get('text_embedding', None)
                attributes = text_unit.get('attributes', {})
            else:
                text_unit_id = getattr(text_unit, 'text_unit_id', None)
                text = getattr(text_unit, 'text', '')
                doc_id = getattr(text_unit, 'doc_id', '')
                chunk_id = getattr(text_unit, 'chunk_id', '')
                n_tokens = getattr(text_unit, 'n_tokens', 0)
                document_ids = getattr(text_unit, 'document_ids', [])
                covariate_ids = getattr(text_unit, 'covariate_ids', [])
                text_embedding = getattr(text_unit, 'text_embedding', None)
                attributes = getattr(text_unit, 'attributes', {})
            
            # Get mapped entities and relationships for this text unit
            unit_entity_ids = text_unit_entities.get(text_unit_id, [])
            unit_relationship_ids = text_unit_relationships.get(text_unit_id, [])
            
            # Create final text unit with bidirectional mappings
            final_unit = TextUnit(
                text_unit_id=text_unit_id,
                text=text,
                doc_id=doc_id,
                chunk_id=chunk_id,
                n_tokens=n_tokens,
                document_ids=document_ids,
                entity_ids=unit_entity_ids,
                relationship_ids=unit_relationship_ids,
                covariate_ids=covariate_ids,
                text_embedding=text_embedding,
                attributes={
                    **attributes,
                    "final_processing": True,
                    "entity_count": len(unit_entity_ids),
                    "relationship_count": len(unit_relationship_ids)
                }
            )
            
            final_text_units.append(final_unit)
        
        self.logger.info(f"Successfully created {len(final_text_units)} final text units")
        self.logger.info(f"Total entity mappings: {sum(len(unit.entity_ids) for unit in final_text_units)}")
        self.logger.info(f"Total relationship mappings: {sum(len(unit.relationship_ids) for unit in final_text_units)}")
        
        return final_text_units
    
    def _create_text_unit_entity_mapping(
        self,
        text_units: List[TextUnit],
        entity_text_mapping: Dict[str, List[str]]
    ) -> Dict[str, List[str]]:
        """
        Create reverse mapping from text_unit_id to entity_ids.
        
        Args:
            text_units: List of text units
            entity_text_mapping: Mapping of entity_id -> list of text_unit_ids
            
        Returns:
            Dictionary mapping text_unit_id -> list of entity_ids
        """
        text_unit_entities = {}
        
        # Initialize empty lists for all text units
        for text_unit in text_units:
            text_unit_id = text_unit.get("text_unit_id", text_unit.get("id", "unknown"))
            text_unit_entities[text_unit_id] = []
        
        # Create reverse mapping from entity_text_mapping
        for entity_id, text_unit_ids in entity_text_mapping.items():
            for text_unit_id in text_unit_ids:
                if text_unit_id in text_unit_entities:
                    text_unit_entities[text_unit_id].append(entity_id)
        
        # If no explicit mapping provided, try to infer from text content
        if not entity_text_mapping:
            self.logger.warning("No entity-text mapping provided, text units will have empty entity lists")
        
        return text_unit_entities
    
    def _create_text_unit_relationship_mapping(
        self,
        text_units: List[TextUnit],
        relationship_text_mapping: Dict[str, List[str]]
    ) -> Dict[str, List[str]]:
        """
        Create reverse mapping from text_unit_id to relationship_ids.
        
        Args:
            text_units: List of text units
            relationship_text_mapping: Mapping of relationship_id -> list of text_unit_ids
            
        Returns:
            Dictionary mapping text_unit_id -> list of relationship_ids
        """
        text_unit_relationships = {}
        
        # Initialize empty lists for all text units
        for text_unit in text_units:
            # Handle both dictionary and object formats
            if isinstance(text_unit, dict):
                text_unit_id = text_unit.get('text_unit_id')
            else:
                text_unit_id = getattr(text_unit, 'text_unit_id', None)
            
            if text_unit_id:
                text_unit_relationships[text_unit_id] = []
        
        # Create reverse mapping from relationship_text_mapping
        for relationship_id, text_unit_ids in relationship_text_mapping.items():
            for text_unit_id in text_unit_ids:
                if text_unit_id in text_unit_relationships:
                    text_unit_relationships[text_unit_id].append(relationship_id)
        
        # If no explicit mapping provided, try to infer from text content
        if not relationship_text_mapping:
            self.logger.warning("No relationship-text mapping provided, text units will have empty relationship lists")
        
        return text_unit_relationships
    
    # tests/optional methods removed: link_text_units_to_graph_elements, save_text_units_to_storage, validate_text_unit_mappings