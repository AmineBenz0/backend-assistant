"""
Abstract base classes for document parsers
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, BinaryIO
from pathlib import Path

from ..models import DocumentMetadata, DocumentChunk, DocumentFormat


class AbstractDocumentParser(ABC):
    """Abstract base class for document parsers"""
    
    @property
    @abstractmethod
    def supported_formats(self) -> List[DocumentFormat]:
        """Return list of supported document formats"""
        pass
    
    @abstractmethod
    async def parse_document(
        self, 
        file_path: Path, 
        metadata: Optional[DocumentMetadata] = None,
        **kwargs
    ) -> List[DocumentChunk]:
        """
        Parse a document and return chunks
        
        Args:
            file_path: Path to the document file
            metadata: Optional document metadata
            **kwargs: Additional parser-specific options
            
        Returns:
            List of document chunks
        """
        pass
    
    @abstractmethod
    async def parse_document_from_bytes(
        self,
        file_bytes: bytes,
        filename: str,
        metadata: Optional[DocumentMetadata] = None,
        **kwargs
    ) -> List[DocumentChunk]:
        """
        Parse a document from bytes
        
        Args:
            file_bytes: Document bytes
            filename: Original filename
            metadata: Optional document metadata
            **kwargs: Additional parser-specific options
            
        Returns:
            List of document chunks
        """
        pass
    
    @abstractmethod
    def extract_metadata(self, file_path: Path) -> DocumentMetadata:
        """
        Extract metadata from document
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Document metadata
        """
        pass
    
    def can_parse(self, file_format: DocumentFormat) -> bool:
        """Check if this parser can handle the given format"""
        return file_format in self.supported_formats
    
    def validate_file(self, file_path: Path) -> bool:
        """Validate if file can be parsed"""
        if not file_path.exists():
            return False
        
        # Get file extension
        extension = file_path.suffix.lower().lstrip('.')
        try:
            format_enum = DocumentFormat(extension)
            return self.can_parse(format_enum)
        except ValueError:
            return False


class AbstractTextSplitter(ABC):
    """Abstract base class for text splitters"""
    
    def __init__(self, chunk_size: int = 1024, chunk_overlap: int = 256):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    @abstractmethod
    def split_text(self, text: str, metadata: DocumentMetadata) -> List[DocumentChunk]:
        """
        Split text into chunks
        
        Args:
            text: Text to split
            metadata: Document metadata
            
        Returns:
            List of document chunks
        """
        pass
    
    @abstractmethod
    def split_documents(self, documents: List[DocumentChunk]) -> List[DocumentChunk]:
        """
        Split multiple documents into chunks
        
        Args:
            documents: List of documents to split
            
        Returns:
            List of document chunks
        """
        pass


class AbstractMultimodalParser(AbstractDocumentParser):
    """Abstract base class for multimodal document parsers"""
    
    @abstractmethod
    async def parse_with_images(
        self,
        file_path: Path,
        extract_images: bool = True,
        extract_tables: bool = True,
        **kwargs
    ) -> List[DocumentChunk]:
        """
        Parse document with image and table extraction
        
        Args:
            file_path: Path to the document file
            extract_images: Whether to extract images
            extract_tables: Whether to extract tables
            **kwargs: Additional options
            
        Returns:
            List of document chunks with multimodal content
        """
        pass
