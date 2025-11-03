"""
Data models for the embeddings service
"""
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from pathlib import Path


class ProcessingType(str, Enum):
    """Types of document processing"""
    EMBEDDING_ONLY = "embedding_only"
    GRAPH_ONLY = "graph_only" 
    HYBRID = "hybrid"  # both embedding and graph


class ProcessingStatus(str, Enum):
    """Processing job status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DocumentFormat(str, Enum):
    """Supported document formats"""
    PDF = "pdf"
    DOCX = "docx"
    DOC = "doc"
    TXT = "txt"
    HTML = "html"
    XLSX = "xlsx"
    XLS = "xls"
    CSV = "csv"
    MD = "md"
    MHTML = "mhtml"


class DocumentMetadata(BaseModel):
    """Document metadata structure"""
    file_name: str
    file_path: str
    file_size: int
    format: DocumentFormat
    created_at: datetime = Field(default_factory=datetime.now)
    modified_at: Optional[datetime] = None
    author: Optional[str] = None
    title: Optional[str] = None
    language: Optional[str] = None
    page_count: Optional[int] = None
    word_count: Optional[int] = None
    custom_metadata: Dict[str, Any] = Field(default_factory=dict)


class DocumentChunk(BaseModel):
    """Document chunk after splitting"""
    chunk_id: str
    text: str
    metadata: DocumentMetadata
    chunk_index: int
    start_char: int
    end_char: int
    embedding: Optional[List[float]] = None


class GraphEntity(BaseModel):
    """Graph entity extracted from document"""
    entity_id: str
    name: str
    type: str
    description: Optional[str] = None
    properties: Dict[str, Any] = Field(default_factory=dict)
    source_chunks: List[str] = Field(default_factory=list)


class GraphRelationship(BaseModel):
    """Graph relationship between entities"""
    relationship_id: str
    source_entity: str
    target_entity: str
    relationship_type: str
    description: Optional[str] = None
    weight: float = 1.0
    properties: Dict[str, Any] = Field(default_factory=dict)
    source_chunks: List[str] = Field(default_factory=list)


class GraphCommunity(BaseModel):
    """Graph community/cluster"""
    community_id: str
    entities: List[str]
    level: int
    title: Optional[str] = None
    summary: Optional[str] = None
    properties: Dict[str, Any] = Field(default_factory=dict)


class ProcessingConfig(BaseModel):
    """Configuration for document processing"""
    # General settings
    processing_type: ProcessingType = ProcessingType.HYBRID
    
    # Document parsing settings
    pdf_mode: str = "normal"  # "normal", "ocr", "multimodal", "mathpix"
    chunk_size: int = 1024
    chunk_overlap: int = 256
    
    # Embedding settings
    embedding_provider: str = "openai"
    embedding_model: str = "text-embedding-3-small"
    batch_size: int = 100
    
    # API credentials
    openai_api_key: Optional[str] = None
    azure_openai_api_key: Optional[str] = None
    azure_openai_endpoint: Optional[str] = None
    azure_openai_api_version: Optional[str] = None
    
    # LLM client for graph building (will be injected at runtime)
    llm_client: Optional[Any] = None
    
    # GraphRAG settings
    graph_provider: str = "standard"  # "standard", "nano", "light"
    entity_extraction_llm: str = "gpt-4o"
    relationship_extraction_llm: str = "gpt-4o"
    community_detection_algorithm: str = "leiden"
    max_entities_per_chunk: int = 10
    
    # Advanced settings
    enable_multimodal: bool = False
    enable_ocr: bool = False
    custom_extractors: Dict[str, str] = Field(default_factory=dict)


class ProcessingJob(BaseModel):
    """Processing job definition"""
    job_id: str
    files: List[str]  # File paths
    config: ProcessingConfig
    status: ProcessingStatus = ProcessingStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress: float = 0.0
    error_message: Optional[str] = None
    result_path: Optional[str] = None


class EmbeddingResult(BaseModel):
    """Result of embedding generation"""
    chunks: List[DocumentChunk]
    embedding_model: str
    total_chunks: int
    total_tokens: int
    processing_time: float


class GraphResult(BaseModel):
    """Result of graph building"""
    entities: List[GraphEntity]
    relationships: List[GraphRelationship]
    communities: List[GraphCommunity]
    graph_provider: str
    total_entities: int
    total_relationships: int
    processing_time: float
    graph_statistics: Dict[str, Any] = Field(default_factory=dict)


class ProcessingResult(BaseModel):
    """Complete processing result"""
    job_id: str
    documents: List[DocumentMetadata]
    embedding_result: Optional[EmbeddingResult] = None
    graph_result: Optional[GraphResult] = None
    processing_type: ProcessingType
    total_processing_time: float
    status: ProcessingStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    error_details: Optional[Dict[str, Any]] = None


class ProcessingProgress(BaseModel):
    """Progress update for processing job"""
    job_id: str
    status: ProcessingStatus
    progress: float  # 0.0 to 1.0
    current_step: str
    steps_completed: int
    total_steps: int
    estimated_time_remaining: Optional[float] = None
    message: Optional[str] = None


class EmbeddingRequest(BaseModel):
    """Request for embedding generation"""
    texts: List[str]
    model: str = "text-embedding-3-small"
    batch_size: int = 100
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EmbeddingData(BaseModel):
    """Individual embedding data"""
    embedding: List[float]
    index: int
    text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EmbeddingResponse(BaseModel):
    """Response from embedding generation"""
    embeddings: List[EmbeddingData]
    model: str
    total_tokens: int
    processing_time: float
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EntityEmbedding(BaseModel):
    """Embedding for a GraphRAG entity"""
    entity_id: str
    entity_name: str
    entity_type: str
    embedding: List[float]
    embedding_model: str
    text_used: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of the embedding vector"""
        return len(self.embedding)
    
    def similarity_to(self, other: 'EntityEmbedding') -> float:
        """Calculate cosine similarity to another entity embedding"""
        if len(self.embedding) != len(other.embedding):
            raise ValueError("Embedding dimensions must match")
        
        # Simple dot product for cosine similarity (assuming normalized vectors)
        import math
        
        dot_product = sum(a * b for a, b in zip(self.embedding, other.embedding))
        magnitude_a = math.sqrt(sum(a * a for a in self.embedding))
        magnitude_b = math.sqrt(sum(b * b for b in other.embedding))
        
        if magnitude_a == 0 or magnitude_b == 0:
            return 0.0
        
        return dot_product / (magnitude_a * magnitude_b)
