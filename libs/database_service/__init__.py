"""
Database Service for Kotaemon

This service handles database operations including graph databases (Neo4j),
vector databases (ChromaDB, Weaviate, etc.), document databases (Elasticsearch),
and object storage (MinIO).
"""

from .storage import MinIOStorageManager
from .graph_db.providers import Neo4jProvider
from .vector_db import WeaviateVectorProvider, ChromaVectorProvider
from .doc_db import ElasticsearchDocProvider
from .models import (
    GraphIndexConfig, VectorIndexConfig, GraphNode, GraphRelationship
)
from .service import DatabaseService

__all__ = [
    # Storage management
    "MinIOStorageManager",
    
    # Graph database
    "Neo4jProvider",
    
    # Vector database
    "WeaviateVectorProvider",
    "ChromaVectorProvider",
    
    # Document database
    "ElasticsearchDocProvider",
    
    
    # Data models
    "GraphIndexConfig",
    "VectorIndexConfig",
    "GraphNode",
    "GraphRelationship",
    
    # Service classes
    "DatabaseService",
]