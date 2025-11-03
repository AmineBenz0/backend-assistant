"""
Base provider class for vector databases
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
from ..models import VectorIndexConfig, VectorDocument


class BaseVectorProvider(ABC):
    """Abstract base class for vector database providers"""
    
    def __init__(self, config: VectorIndexConfig):
        self.config = config
        self._initialized = False
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the vector database connection"""
        pass
    
    @abstractmethod
    async def create_index(self) -> bool:
        """Create a new vector index"""
        pass
    
    @abstractmethod
    async def delete_index(self) -> bool:
        """Delete the vector index"""
        pass
    
    @abstractmethod
    async def add_documents(self, documents: List[VectorDocument]) -> List[str]:
        """Add documents to the index"""
        pass
    
    @abstractmethod
    async def update_documents(self, documents: List[VectorDocument]) -> bool:
        """Update existing documents"""
        pass
    
    @abstractmethod
    async def delete_documents(self, document_ids: List[str]) -> bool:
        """Delete documents from the index"""
        pass
    
    @abstractmethod
    async def get_document(self, document_id: str) -> Optional[VectorDocument]:
        """Retrieve a specific document"""
        pass
    
    @abstractmethod
    async def get_index_stats(self) -> Dict[str, Any]:
        """Get index statistics"""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Check provider health"""
        pass
    
    @abstractmethod
    async def store_chunks(self, chunks: List[Dict[str, Any]], client_id: str, project_id: str) -> Dict[str, Any]:
        """Store document chunks with embeddings, scoped to client_id and project_id"""
        pass
    
    @abstractmethod
    async def similarity_search(self, query: str, client_id: str, project_id: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Perform similarity search scoped to client_id and project_id"""
        pass
    
    @abstractmethod
    async def delete_chunks(self, client_id: str, project_id: str, object_name: str) -> Dict[str, Any]:
        """Delete chunks associated with a document in a client's project"""
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
        return self.config.vector_db_type

