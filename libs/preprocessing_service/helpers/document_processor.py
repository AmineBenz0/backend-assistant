"""
Document Processor Helper for GraphRAG Document Processing Steps

This helper implements the create_base_documents and create_final_documents steps from GraphRAG pipeline 
following kotaemon's approach:
- Collect base document metadata following kotaemon's metadata collection (create_base_documents)
- Map text files to document IDs with initial metadata matching kotaemon's mapping strategy
- Create enriched document objects with title assignment and relationships following kotaemon's enrichment process (create_final_documents)
- Establish relationships between documents, communities, and text units matching kotaemon's relationship structure
- Store all document metadata and relationships in MinIO bucket
"""
import logging
from typing import List, Dict, Optional, Any, Set
from pathlib import Path
import json
import uuid
from datetime import datetime

from ..models import DocumentMetadata, DocumentFormat, TextUnit

logger = logging.getLogger(__name__)


class BaseDocument:
    """
    Base document representation for GraphRAG processing following kotaemon's approach.
    
    This represents the create_base_documents step output with initial metadata collection.
    """
    
    def __init__(
        self,
        document_id: str,
        title: str,
        raw_content: str,
        text_units: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.document_id = document_id
        self.title = title
        self.raw_content = raw_content
        self.text_units = text_units  # List of text_unit_ids
        self.metadata = metadata or {}
        self.created_at = datetime.now()
    
    # tests/optional method removed: to_dict


class FinalDocument:
    """
    Final document representation with enriched metadata and relationships following kotaemon's approach.
    
    This represents the create_final_documents step output with complete relationships.
    """
    
    def __init__(
        self,
        document_id: str,
        title: str,
        raw_content: str,
        text_units: List[str],
        entities: List[str],
        relationships: List[str],
        communities: List[str],
        metadata: Optional[Dict[str, Any]] = None,
        attributes: Optional[Dict[str, Any]] = None
    ):
        self.document_id = document_id
        self.title = title
        self.raw_content = raw_content
        self.text_units = text_units  # List of text_unit_ids
        self.entities = entities  # List of entity_ids mentioned in this document
        self.relationships = relationships  # List of relationship_ids in this document
        self.communities = communities  # List of community_ids this document belongs to
        self.metadata = metadata or {}
        self.attributes = attributes or {}
        self.created_at = datetime.now()
    
    # tests/optional method removed: to_dict


class DocumentProcessor:
    """
    Helper class for processing GraphRAG documents following kotaemon's approach.
    
    This class handles both create_base_documents and create_final_documents steps
    which collect document metadata and establish relationships with graph elements.
    """
    
    def __init__(self):
        """Initialize the document processor"""
        self.logger = logger
    
    def create_base_documents(
        self,
        text_files: List[Any],  # Can be Dict or DocumentChunk objects
        text_units: Optional[List[TextUnit]] = None
    ) -> List[BaseDocument]:
        """
        Create base document objects with initial metadata following kotaemon's approach.
        
        This implements the create_base_documents step from GraphRAG pipeline:
        - Collect base document metadata following kotaemon's metadata collection
        - Map text files to document IDs with initial metadata matching kotaemon's mapping strategy
        
        Args:
            text_files: List of text file dictionaries or DocumentChunk objects
            text_units: Optional list of text units to map to documents
            
        Returns:
            List of base documents with initial metadata
        """
        self.logger.info(f"Creating base documents from {len(text_files)} text files")
        
        base_documents = []
        text_unit_mapping = self._create_text_unit_document_mapping(text_units or [])
        
        for file_info in text_files:
            try:
                # Handle both dictionary and DocumentChunk object formats
                if isinstance(file_info, dict):
                    file_path = file_info.get('file_path', '')
                    content = file_info.get('content', '')
                    metadata = file_info.get('metadata', {})
                else:
                    # Handle DocumentChunk object
                    content = getattr(file_info, 'text', '')
                    metadata_obj = getattr(file_info, 'metadata', {})
                    
                    # Handle metadata object conversion
                    if hasattr(metadata_obj, '__dict__'):
                        # Convert metadata object to dict
                        metadata = metadata_obj.__dict__
                        file_path = metadata.get('file_path', '')
                    elif isinstance(metadata_obj, dict):
                        metadata = metadata_obj
                        file_path = metadata.get('file_path', '')
                    else:
                        # Fallback for other metadata formats
                        file_path = getattr(metadata_obj, 'file_path', '') if hasattr(metadata_obj, 'file_path') else ''
                        metadata = {}
                
                # Generate document ID
                document_id = str(uuid.uuid4())
                
                # Extract title from file path or metadata
                title = self._extract_document_title(file_path, metadata)
                
                # Get text units for this document
                doc_text_units = text_unit_mapping.get(file_path, [])
                
                # Create base document metadata following kotaemon's approach
                base_metadata = {
                    "file_path": file_path,
                    "file_name": Path(file_path).name if file_path else "unknown",
                    "file_size": len(content.encode('utf-8')),
                    "content_length": len(content),
                    "text_unit_count": len(doc_text_units),
                    "processing_step": "create_base_documents",
                    **metadata  # Include original metadata
                }
                
                # Create base document
                base_document = BaseDocument(
                    document_id=document_id,
                    title=title,
                    raw_content=content,
                    text_units=doc_text_units,
                    metadata=base_metadata
                )
                
                base_documents.append(base_document)
                
                self.logger.debug(f"Created base document {document_id} from {file_path}")
                
            except Exception as e:
                self.logger.error(f"Failed to create base document from {file_info}: {str(e)}")
                continue
        
        self.logger.info(f"Successfully created {len(base_documents)} base documents")
        return base_documents
    
    def create_final_documents(
        self,
        base_documents: List[BaseDocument],
        entities: Optional[List[Dict[str, Any]]] = None,
        relationships: Optional[List[Dict[str, Any]]] = None,
        communities: Optional[List[Dict[str, Any]]] = None,
        text_units: Optional[List[TextUnit]] = None
    ) -> List[FinalDocument]:
        """
        Create enriched document objects with title assignment and relationships following kotaemon's approach.
        
        This implements the create_final_documents step from GraphRAG pipeline:
        - Create enriched document objects with title assignment and relationships
        - Establish relationships between documents, communities, and text units
        
        Args:
            base_documents: List of base documents from create_base_documents step
            entities: Optional list of entity dictionaries
            relationships: Optional list of relationship dictionaries
            communities: Optional list of community dictionaries
            text_units: Optional list of text units for mapping
            
        Returns:
            List of final documents with complete metadata and relationships
        """
        self.logger.info(f"Creating final documents from {len(base_documents)} base documents")
        
        # Initialize data structures
        entities = entities or []
        relationships = relationships or []
        communities = communities or []
        text_units = text_units or []
        
        # Create mappings for efficient lookup
        entity_document_mapping = self._create_entity_document_mapping(entities, text_units, base_documents)
        relationship_document_mapping = self._create_relationship_document_mapping(relationships, text_units, base_documents)
        community_document_mapping = self._create_community_document_mapping(communities, text_units, base_documents)
        
        final_documents = []
        
        for base_doc in base_documents:
            try:
                # Get related entities, relationships, and communities
                doc_entities = entity_document_mapping.get(base_doc.document_id, [])
                doc_relationships = relationship_document_mapping.get(base_doc.document_id, [])
                doc_communities = community_document_mapping.get(base_doc.document_id, [])
                
                # Enhance title with entity information if available
                enhanced_title = self._enhance_document_title(
                    base_doc.title, 
                    doc_entities, 
                    entities
                )
                
                # Create enriched metadata following kotaemon's enrichment process
                enriched_metadata = {
                    **base_doc.metadata,
                    "entity_count": len(doc_entities),
                    "relationship_count": len(doc_relationships),
                    "community_count": len(doc_communities),
                    "processing_step": "create_final_documents",
                    "enrichment_timestamp": datetime.now().isoformat()
                }
                
                # Create document attributes for additional information
                attributes = {
                    "semantic_density": self._calculate_semantic_density(
                        len(doc_entities), 
                        len(doc_relationships), 
                        len(base_doc.raw_content)
                    ),
                    "community_membership": doc_communities,
                    "primary_entities": doc_entities[:5],  # Top 5 entities
                    "key_relationships": doc_relationships[:10]  # Top 10 relationships
                }
                
                # Create final document
                final_document = FinalDocument(
                    document_id=base_doc.document_id,
                    title=enhanced_title,
                    raw_content=base_doc.raw_content,
                    text_units=base_doc.text_units,
                    entities=doc_entities,
                    relationships=doc_relationships,
                    communities=doc_communities,
                    metadata=enriched_metadata,
                    attributes=attributes
                )
                
                final_documents.append(final_document)
                
                self.logger.debug(f"Created final document {base_doc.document_id} with {len(doc_entities)} entities, {len(doc_relationships)} relationships")
                
            except Exception as e:
                self.logger.error(f"Failed to create final document from {base_doc.document_id}: {str(e)}")
                continue
        
        self.logger.info(f"Successfully created {len(final_documents)} final documents")
        self.logger.info(f"Total entity mappings: {sum(len(doc.entities) for doc in final_documents)}")
        self.logger.info(f"Total relationship mappings: {sum(len(doc.relationships) for doc in final_documents)}")
        self.logger.info(f"Total community mappings: {sum(len(doc.communities) for doc in final_documents)}")
        
        return final_documents
    
    def _create_text_unit_document_mapping(
        self, 
        text_units: List[TextUnit]
    ) -> Dict[str, List[str]]:
        """
        Create mapping from document file path to text unit IDs.
        
        Args:
            text_units: List of text units
            
        Returns:
            Dictionary mapping file_path -> list of text_unit_ids
        """
        mapping = {}
        
        for text_unit in text_units:
            # Use doc_id or derive from metadata
            doc_path = text_unit.doc_id
            
            if doc_path not in mapping:
                mapping[doc_path] = []
            mapping[doc_path].append(text_unit.text_unit_id)
        
        return mapping
    
    def _extract_document_title(
        self, 
        file_path: str, 
        metadata: Dict[str, Any]
    ) -> str:
        """
        Extract document title from file path or metadata following kotaemon's approach.
        
        Args:
            file_path: Path to the document file
            metadata: Document metadata
            
        Returns:
            Extracted or generated document title
        """
        # Try to get title from metadata first
        if 'title' in metadata and metadata['title']:
            return metadata['title']
        
        # Extract from file name
        if file_path:
            file_name = Path(file_path).stem
            # Clean up the file name to make it a readable title
            title = file_name.replace('_', ' ').replace('-', ' ')
            title = ' '.join(word.capitalize() for word in title.split())
            return title
        
        # Fallback to generic title
        return "Untitled Document"
    
    def _create_entity_document_mapping(
        self,
        entities: List[Dict[str, Any]],
        text_units: List[TextUnit],
        base_documents: List[BaseDocument]
    ) -> Dict[str, List[str]]:
        """
        Create mapping from document_id to entity_ids mentioned in that document.
        
        Args:
            entities: List of entity dictionaries
            text_units: List of text units
            base_documents: List of base documents
            
        Returns:
            Dictionary mapping document_id -> list of entity_ids
        """
        mapping = {}
        
        # Initialize empty lists for all documents
        for doc in base_documents:
            mapping[doc.document_id] = []
        
        # Create text_unit_id to document_id mapping
        text_unit_to_doc = {}
        for doc in base_documents:
            for text_unit_id in doc.text_units:
                text_unit_to_doc[text_unit_id] = doc.document_id
        
        # Map entities to documents through text units
        for entity in entities:
            entity_id = entity.get('entity_id', entity.get('id', ''))
            if not entity_id:
                continue
            
            # Find text units that mention this entity
            for text_unit in text_units:
                if entity_id in text_unit.entity_ids:
                    doc_id = text_unit_to_doc.get(text_unit.text_unit_id)
                    if doc_id and entity_id not in mapping[doc_id]:
                        mapping[doc_id].append(entity_id)
        
        return mapping
    
    def _create_relationship_document_mapping(
        self,
        relationships: List[Dict[str, Any]],
        text_units: List[TextUnit],
        base_documents: List[BaseDocument]
    ) -> Dict[str, List[str]]:
        """
        Create mapping from document_id to relationship_ids mentioned in that document.
        
        Args:
            relationships: List of relationship dictionaries
            text_units: List of text units
            base_documents: List of base documents
            
        Returns:
            Dictionary mapping document_id -> list of relationship_ids
        """
        mapping = {}
        
        # Initialize empty lists for all documents
        for doc in base_documents:
            mapping[doc.document_id] = []
        
        # Create text_unit_id to document_id mapping
        text_unit_to_doc = {}
        for doc in base_documents:
            for text_unit_id in doc.text_units:
                text_unit_to_doc[text_unit_id] = doc.document_id
        
        # Map relationships to documents through text units
        for relationship in relationships:
            relationship_id = relationship.get('relationship_id', relationship.get('id', ''))
            if not relationship_id:
                continue
            
            # Find text units that mention this relationship
            for text_unit in text_units:
                if relationship_id in text_unit.relationship_ids:
                    doc_id = text_unit_to_doc.get(text_unit.text_unit_id)
                    if doc_id and relationship_id not in mapping[doc_id]:
                        mapping[doc_id].append(relationship_id)
        
        return mapping
    
    def _create_community_document_mapping(
        self,
        communities: List[Dict[str, Any]],
        text_units: List[TextUnit],
        base_documents: List[BaseDocument]
    ) -> Dict[str, List[str]]:
        """
        Create mapping from document_id to community_ids that document belongs to.
        
        Args:
            communities: List of community dictionaries
            text_units: List of text units
            base_documents: List of base documents
            
        Returns:
            Dictionary mapping document_id -> list of community_ids
        """
        mapping = {}
        
        # Initialize empty lists for all documents
        for doc in base_documents:
            mapping[doc.document_id] = []
        
        # Create text_unit_id to document_id mapping
        text_unit_to_doc = {}
        for doc in base_documents:
            for text_unit_id in doc.text_units:
                text_unit_to_doc[text_unit_id] = doc.document_id
        
        # Map communities to documents through text units
        for community in communities:
            community_id = community.get('community_id', community.get('id', ''))
            text_unit_ids = community.get('text_units', [])
            
            if not community_id:
                continue
            
            # Find documents that contain text units from this community
            for text_unit_id in text_unit_ids:
                doc_id = text_unit_to_doc.get(text_unit_id)
                if doc_id and community_id not in mapping[doc_id]:
                    mapping[doc_id].append(community_id)
        
        return mapping
    
    def _enhance_document_title(
        self,
        original_title: str,
        entity_ids: List[str],
        entities: List[Dict[str, Any]]
    ) -> str:
        """
        Enhance document title with entity information following kotaemon's approach.
        
        Args:
            original_title: Original document title
            entity_ids: List of entity IDs in the document
            entities: List of entity dictionaries
            
        Returns:
            Enhanced document title
        """
        if not entity_ids or not entities:
            return original_title
        
        # Create entity lookup
        entity_lookup = {
            entity.get('entity_id', entity.get('id', '')): entity
            for entity in entities
        }
        
        # Find key entities (e.g., PERSON, ORGANIZATION)
        key_entities = []
        for entity_id in entity_ids[:3]:  # Top 3 entities
            entity = entity_lookup.get(entity_id)
            if entity:
                entity_name = entity.get('name', '')
                entity_type = entity.get('type', '').upper()
                
                if entity_type in ['PERSON', 'ORGANIZATION', 'LOCATION'] and entity_name:
                    key_entities.append(entity_name)
        
        # Enhance title if key entities found
        if key_entities:
            entities_str = ', '.join(key_entities)
            return f"{original_title} ({entities_str})"
        
        return original_title
    
    def _calculate_semantic_density(
        self,
        entity_count: int,
        relationship_count: int,
        content_length: int
    ) -> float:
        """
        Calculate semantic density of the document based on entities and relationships.
        
        Args:
            entity_count: Number of entities in document
            relationship_count: Number of relationships in document
            content_length: Length of document content
            
        Returns:
            Semantic density score (0.0 to 1.0)
        """
        if content_length == 0:
            return 0.0
        
        # Calculate density based on entities and relationships per 1000 characters
        total_semantic_elements = entity_count + relationship_count
        density = (total_semantic_elements * 1000) / content_length
        
        # Normalize to 0-1 range (assuming max density of 50 elements per 1000 chars)
        normalized_density = min(density / 50.0, 1.0)
        
        return round(normalized_density, 3)
