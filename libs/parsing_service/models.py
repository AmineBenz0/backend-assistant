"""
Data models for the parsing service
"""
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from pathlib import Path


class DocumentFormat(str, Enum):
    """Supported document formats"""
    PDF = "pdf"
    DOCX = "docx"
    DOC = "doc"
    TXT = "txt"
    HTML = "html"
    HTM = "htm"
    XLSX = "xlsx"
    XLS = "xls"
    PPTX = "pptx"
    PPT = "ppt"
    MD = "md"
    EPUB = "epub"
    JPG = "jpg"
    JPEG = "jpeg"
    PNG = "png"
    GIF = "gif"
    BMP = "bmp"
    TIFF = "tiff"
    UNKNOWN = "unknown"


class ParsingMethod(str, Enum):
    """Types of parsing methods"""
    LLAMACLOUD = "llamacloud"
    PYPDF = "pypdf"
    DOCX2TXT = "docx2txt"
    BEAUTIFULSOUP = "beautifulsoup"
    CUSTOM = "custom"


class ParsingStatus(str, Enum):
    """Parsing job status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


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


class ParsingConfig(BaseModel):
    """Configuration for document parsing"""
    method: ParsingMethod = ParsingMethod.LLAMACLOUD
    output_format: str = "markdown"  # "markdown", "text", "html"
    language: str = "en"
    timeout: int = 300
    verbose: bool = True
    
    # LlamaCloud specific settings
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    result_type: str = "markdown"
    
    # PyPDF specific settings
    password: Optional[str] = None
    max_pages: Optional[int] = None
    
    # SSL verification settings
    verify_ssl: bool = True
    ssl_cert_path: Optional[str] = None
    
    # Additional provider-specific settings
    custom_settings: Dict[str, Any] = Field(default_factory=dict)


class ParsingResult(BaseModel):
    """Result of document parsing"""
    content: str
    metadata: DocumentMetadata
    parsing_method: ParsingMethod
    provider: str
    config_used: ParsingConfig
    processing_time: float
    parsing_metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def get_content_length(self) -> int:
        """Get the length of the parsed content"""
        return len(self.content)
    
    def get_word_count(self) -> int:
        """Get the word count of the parsed content"""
        return len(self.content.split())
    
    def get_line_count(self) -> int:
        """Get the line count of the parsed content"""
        return len(self.content.splitlines())
    
    def is_empty(self) -> bool:
        """Check if the parsed content is empty"""
        return not self.content.strip()


class ParsingRequest(BaseModel):
    """Request for document parsing"""
    file_path: str
    config: ParsingConfig
    custom_metadata: Dict[str, Any] = Field(default_factory=dict)


class ParsingResponse(BaseModel):
    """Response from parsing service"""
    result: ParsingResult
    success: bool = True
    error_message: Optional[str] = None
    processing_time: float


class ParsingProviderInfo(BaseModel):
    """Information about a parsing provider"""
    name: str
    supported_formats: List[DocumentFormat]
    supports_markdown: bool = True
    supports_text: bool = True
    supports_html: bool = False
    requires_api_key: bool = False
    max_file_size: Optional[int] = None
    class_name: str
    module: str
    description: Optional[str] = None


class ParsingHealthCheck(BaseModel):
    """Health check result for parsing service"""
    status: str  # "healthy", "unhealthy", "degraded"
    provider: str
    method: ParsingMethod
    test_parsing_successful: bool
    error_message: Optional[str] = None
    response_time: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class ParsingJob(BaseModel):
    """Parsing job definition"""
    job_id: str
    file_path: str
    config: ParsingConfig
    status: ParsingStatus = ParsingStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress: float = 0.0
    error_message: Optional[str] = None
    result: Optional[ParsingResult] = None


class ParsingProgress(BaseModel):
    """Progress update for parsing job"""
    job_id: str
    status: ParsingStatus
    progress: float  # 0.0 to 1.0
    current_step: str
    message: Optional[str] = None
    estimated_time_remaining: Optional[float] = None


class BatchParsingRequest(BaseModel):
    """Request for batch document parsing"""
    file_paths: List[str]
    config: ParsingConfig
    custom_metadata_list: Optional[List[Dict[str, Any]]] = None


class BatchParsingResult(BaseModel):
    """Result of batch document parsing"""
    results: List[ParsingResult]
    total_files: int
    successful_files: int
    failed_files: int
    total_processing_time: float
    errors: List[Dict[str, Any]] = Field(default_factory=list)
    
    def get_success_rate(self) -> float:
        """Get the success rate of batch parsing"""
        if self.total_files == 0:
            return 0.0
        return self.successful_files / self.total_files

