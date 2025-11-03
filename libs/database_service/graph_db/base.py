"""
Base provider class for graph databases
"""
from abc import ABC, abstractmethod
from typing import List
from ..models import GraphIndexConfig, GraphNode, GraphRelationship


class BaseGraphProvider(ABC):
    """Abstract base class for graph database providers"""
    
    def __init__(self, config: GraphIndexConfig):
        self.config = config
        self._initialized = False
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the graph database connection"""
        pass
    
    @abstractmethod
    async def create_index(self) -> bool:
        """Create a new graph database and indexes"""
        pass
    
    @abstractmethod
    async def add_nodes(self, nodes: List[GraphNode]) -> List[str]:
        """Add nodes to the graph"""
        pass
    
    @abstractmethod
    async def add_relationships(self, relationships: List[GraphRelationship]) -> List[str]:
        """Add relationships to the graph"""
        pass
    
    def is_initialized(self) -> bool:
        """Check if provider is initialized"""
        return self._initialized
    
    def get_provider_type(self) -> str:
        """Get the provider type name"""
        return self.config.graph_db_type
