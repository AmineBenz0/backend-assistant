"""
Data models for the preprocessing service
"""
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


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


class TextUnit(BaseModel):
    """GraphRAG text unit - atomic text unit with metadata"""
    text_unit_id: str
    text: str
    doc_id: str
    chunk_id: str
    n_tokens: int
    document_ids: List[str] = Field(default_factory=list)
    entity_ids: List[str] = Field(default_factory=list)
    relationship_ids: List[str] = Field(default_factory=list)
    covariate_ids: List[str] = Field(default_factory=list)
    text_embedding: Optional[List[float]] = None
    attributes: Dict[str, Any] = Field(default_factory=dict)


__all__ = [
    "DocumentFormat",
    "DocumentMetadata",
    "DocumentChunk",
    "TextUnit",
]
