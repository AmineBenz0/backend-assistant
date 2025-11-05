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

class ProcessingConfig(BaseModel):
    """Configuration for document processing"""
    # General settings
    processing_type: ProcessingType = ProcessingType.EMBEDDING_ONLY
    
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
    
    # LLM client (will be injected at runtime)
    llm_client: Optional[Any] = None
    

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


class ProcessingResult(BaseModel):
    """Complete processing result"""
    job_id: str
    documents: List[DocumentMetadata]
    embedding_result: Optional[EmbeddingResult] = None
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
