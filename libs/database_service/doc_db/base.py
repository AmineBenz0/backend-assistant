"""
Base provider class for document databases
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any


class BaseDocProvider(ABC):
    """Abstract base class for document database providers"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self._initialized = False
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the document database connection"""
        pass
    
    @abstractmethod
    async def save(self, index: str, doc_id: str, data: Dict[str, Any], client_id: Optional[str] = None) -> bool:
        """Save or update a document"""
        pass
    
    @abstractmethod
    async def load(self, index: str, doc_id: str, client_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Load a document by ID"""
        pass
    
    @abstractmethod
    async def search(self, index: str, query: Dict[str, Any], size: int = 10, client_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Perform a search query"""
        pass
    
    @abstractmethod
    async def delete(self, index: str, doc_id: str, client_id: Optional[str] = None) -> bool:
        """Delete a document"""
        pass
    
    @abstractmethod
    async def create_document_to_chunks_mapping(self, index_name: str, document_id: str, 
                                              storage_object_name: str, vector_chunk_ids: List[str], 
                                              metadata: Dict[str, Any], client_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a mapping document that links a storage object to its vector chunks"""
        pass
    
    @abstractmethod
    async def delete_document_mapping(self, index_name: str, document_id: str, client_id: Optional[str] = None) -> bool:
        """Delete a document mapping"""
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Close database connections"""
        pass
    
    def is_initialized(self) -> bool:
        """Check if provider is initialized"""
        return self._initialized
    
    def get_provider_type(self) -> str:
        """Get the provider type name"""
        return self.config.get("provider_type", "unknown")
