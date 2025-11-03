"""
Data models for the chunking service
"""
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field


class ChunkingMethod(str, Enum):
    """Types of chunking methods"""
    RECURSIVE = "recursive"
    SEMANTIC = "semantic"
    FIXED_SIZE = "fixed_size"
    SENTENCE = "sentence"
    PARAGRAPH = "paragraph"


class ChunkType(str, Enum):
    """Types of content chunks"""
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    LIST_ITEM = "list_item"
    CODE_BLOCK = "code_block"
    QUOTE = "quote"
    TABLE = "table"
    URL = "url"
    SHORT_PHRASE = "short_phrase"
    UNKNOWN = "unknown"


class ChunkingConfig(BaseModel):
    """Configuration for document chunking"""
    chunk_size: int = 1000
    chunk_overlap: int = 200
    method: ChunkingMethod = ChunkingMethod.RECURSIVE
    separators: Optional[List[str]] = None
    keep_separator: bool = False
    add_start_index: bool = False
    strip_whitespace: bool = True
    is_separator_regex: bool = False
    
    # Semantic chunking specific
    breakpoint_threshold_type: str = "percentile"
    breakpoint_threshold_amount: int = 95
    embedding_model: Optional[str] = None
    
    # Additional provider-specific settings
    custom_settings: Dict[str, Any] = Field(default_factory=dict)


class ChunkMetadata(BaseModel):
    """Metadata for a document chunk"""
    chunk_index: int
    chunk_size: int
    chunk_type: ChunkType = ChunkType.UNKNOWN
    chunking_method: ChunkingMethod
    created_at: datetime = Field(default_factory=datetime.now)
    provider: str
    start_char: Optional[int] = None
    end_char: Optional[int] = None
    
    # Document metadata
    document_filename: Optional[str] = None
    document_size: Optional[int] = None
    source_document_name: Optional[str] = None
    
    # Additional metadata
    custom_metadata: Dict[str, Any] = Field(default_factory=dict)


class DocumentChunk(BaseModel):
    """A chunk of a document"""
    chunk_id: Optional[str] = None
    text: str
    metadata: ChunkMetadata
    
    def get_chunk_length(self) -> int:
        """Get the length of the chunk text"""
        return len(self.text)
    
    def get_word_count(self) -> int:
        """Get the word count of the chunk"""
        return len(self.text.split())
    
    def is_empty(self) -> bool:
        """Check if the chunk is empty or whitespace only"""
        return not self.text.strip()


class ChunkingResult(BaseModel):
    """Result of document chunking"""
    chunks: List[DocumentChunk]
    total_chunks: int
    chunking_method: ChunkingMethod
    provider: str
    config_used: ChunkingConfig
    processing_time: float
    document_metadata: Dict[str, Any] = Field(default_factory=dict)
    chunking_metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def get_average_chunk_size(self) -> float:
        """Get the average chunk size"""
        if not self.chunks:
            return 0.0
        return sum(chunk.get_chunk_length() for chunk in self.chunks) / len(self.chunks)
    
    def get_chunk_size_distribution(self) -> Dict[str, int]:
        """Get distribution of chunk sizes"""
        if not self.chunks:
            return {}
        
        sizes = [chunk.get_chunk_length() for chunk in self.chunks]
        return {
            "min": min(sizes),
            "max": max(sizes),
            "mean": int(sum(sizes) / len(sizes)),
            "median": int(sorted(sizes)[len(sizes) // 2])
        }
    
    def get_chunk_type_distribution(self) -> Dict[str, int]:
        """Get distribution of chunk types"""
        if not self.chunks:
            return {}
        
        type_counts = {}
        for chunk in self.chunks:
            chunk_type = chunk.metadata.chunk_type.value
            type_counts[chunk_type] = type_counts.get(chunk_type, 0) + 1
        
        return type_counts


class ChunkingRequest(BaseModel):
    """Request for document chunking"""
    text: str
    config: ChunkingConfig
    document_metadata: Dict[str, Any] = Field(default_factory=dict)
    generate_chunk_ids: bool = True


class ChunkingResponse(BaseModel):
    """Response from chunking service"""
    result: ChunkingResult
    success: bool = True
    error_message: Optional[str] = None
    processing_time: float


class ChunkingProviderInfo(BaseModel):
    """Information about a chunking provider"""
    name: str
    supports_semantic_chunking: bool = False
    supports_custom_separators: bool = True
    supports_metadata_extraction: bool = True
    max_chunk_size: Optional[int] = None
    min_chunk_size: Optional[int] = None
    class_name: str
    module: str
    description: Optional[str] = None


class ChunkingHealthCheck(BaseModel):
    """Health check result for chunking service"""
    status: str  # "healthy", "unhealthy", "degraded"
    provider: str
    method: ChunkingMethod
    test_chunking_successful: bool
    error_message: Optional[str] = None
    response_time: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.now)

