"""
Data models for the Database Indexing Service
"""
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from uuid import UUID, uuid4


class VectorIndexConfig(BaseModel):
    """Configuration for vector database indices"""
    index_id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: Optional[str] = None
    
    # Vector database settings
    vector_db_type: str = "chroma"  # chroma, pinecone, weaviate, qdrant, faiss
    vector_dimension: int = 3072  # OpenAI text-embedding-3-large dimension (default for kotaemon)
    distance_metric: str = "cosine"  # cosine, euclidean, dot_product
    
    # Weaviate specific settings
    weaviate_url: Optional[str] = None
    weaviate_api_key: Optional[str] = None
    
    # ChromaDB specific settings
    chroma_host: Optional[str] = None
    chroma_port: Optional[int] = None
    
    # Index settings
    max_elements: Optional[int] = None
    ef_construction: Optional[int] = None  # For HNSW indices
    m: Optional[int] = None  # For HNSW indices
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    tags: List[str] = Field(default_factory=list)
    custom_config: Dict[str, Any] = Field(default_factory=dict)


class GraphIndexConfig(BaseModel):
    """Configuration for graph database indices"""
    index_id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: Optional[str] = None
    
    # Graph database settings
    graph_db_type: str = "neo4j"  # neo4j, arangodb, orientdb
    database_name: str = "neo4j"
    
    # Neo4j specific settings
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"
    
    # Graph settings
    enable_constraints: bool = True
    enable_indexes: bool = True
    max_relationships_per_node: Optional[int] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    tags: List[str] = Field(default_factory=list)
    custom_config: Dict[str, Any] = Field(default_factory=dict)


class VectorDocument(BaseModel):
    """Document for vector database storage"""
    document_id: str = Field(default_factory=lambda: str(uuid4()))
    index_id: str
    content: str
    embedding: List[float]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Document info
    source: Optional[str] = None
    chunk_index: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Vector info
    vector_id: Optional[str] = None
    similarity_score: Optional[float] = None


class GraphNode(BaseModel):
    """Node for graph database storage"""
    node_id: str = Field(default_factory=lambda: str(uuid4()))
    index_id: str
    labels: List[str] = Field(default_factory=list)
    properties: Dict[str, Any] = Field(default_factory=dict)
    
    # Node info
    name: str
    node_type: str
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Graph info
    in_degree: int = 0
    out_degree: int = 0


class GraphRelationship(BaseModel):
    """Relationship for graph database storage"""
    relationship_id: str = Field(default_factory=lambda: str(uuid4()))
    index_id: str
    source_node_id: str
    target_node_id: str
    relationship_type: str
    properties: Dict[str, Any] = Field(default_factory=dict)
    
    # Relationship info
    weight: float = 1.0
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Graph info
    bidirectional: bool = False
