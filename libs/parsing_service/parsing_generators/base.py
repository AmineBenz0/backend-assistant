"""
Abstract base classes for parsing generators
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import time
import os
from datetime import datetime
from pathlib import Path

from ..models import (
    ParsingResult, 
    ParsingConfig, 
    DocumentMetadata, 
    DocumentFormat, 
    ParsingMethod,
    ParsingStatus
)


class AbstractParsingGenerator(ABC):
    """Abstract base class for parsing generators"""
    
    def __init__(self, config: ParsingConfig):
        self.config = config
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of this parsing generator"""
        pass
    
    @property
    @abstractmethod
    def supported_formats(self) -> List[DocumentFormat]:
        """Return list of supported document formats"""
        pass
    
    @property
    @abstractmethod
    def requires_api_key(self) -> bool:
        """Return whether this generator requires an API key"""
        pass
    
    @abstractmethod
    async def parse_document(
        self, 
        file_path: str,
        custom_metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> ParsingResult:
        """
        Parse a document file
        
        Args:
            file_path: Path to the document file
            custom_metadata: Optional custom metadata
            **kwargs: Additional generator-specific parameters
            
        Returns:
            Parsing result with content and metadata
        """
        pass
    
    async def parse_document_to_markdown(
        self, 
        file_path: str,
        custom_metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> ParsingResult:
        """
        Parse a document to markdown format
        
        Args:
            file_path: Path to the document file
            custom_metadata: Optional custom metadata
            **kwargs: Additional parameters
            
        Returns:
            Parsing result with markdown content
        """
        # Default implementation - can be overridden by generators
        result = await self.parse_document(file_path, custom_metadata, **kwargs)
        
        # If the result is not already in markdown, convert it
        if not result.parsing_metadata.get('output_format') == 'markdown':
            result.content = self._convert_to_markdown(result.content, file_path)
            result.parsing_metadata['output_format'] = 'markdown'
        
        return result
    
    def _convert_to_markdown(self, content: str, file_path: str) -> str:
        """Convert content to markdown format"""
        file_name = Path(file_path).name
        
        # Add document header if not present
        if not content.startswith('#'):
            content = f"# {file_name}\n\n{content}"
        
        return content
    
    def _create_document_metadata(
        self, 
        file_path: str, 
        custom_metadata: Optional[Dict[str, Any]] = None
    ) -> DocumentMetadata:
        """Create document metadata from file path"""
        path = Path(file_path)
        
        # Get file stats
        stat = path.stat() if path.exists() else None
        
        # Determine document format
        file_format = self._determine_document_format(file_path)
        
        # Get word count if content is available
        word_count = None
        if custom_metadata and 'content' in custom_metadata:
            word_count = len(custom_metadata['content'].split())
        
        return DocumentMetadata(
            file_name=path.name,
            file_path=str(path.absolute()),
            file_size=stat.st_size if stat else 0,
            format=file_format,
            modified_at=datetime.fromtimestamp(stat.st_mtime) if stat else None,
            word_count=word_count,
            custom_metadata=custom_metadata or {}
        )
    
    def _determine_document_format(self, file_path: str) -> DocumentFormat:
        """Determine document format from file extension"""
        extension = Path(file_path).suffix.lower().lstrip('.')
        
        format_mapping = {
            'pdf': DocumentFormat.PDF,
            'docx': DocumentFormat.DOCX,
            'doc': DocumentFormat.DOC,
            'txt': DocumentFormat.TXT,
            'html': DocumentFormat.HTML,
            'htm': DocumentFormat.HTM,
            'xlsx': DocumentFormat.XLSX,
            'xls': DocumentFormat.XLS,
            'pptx': DocumentFormat.PPTX,
            'ppt': DocumentFormat.PPT,
            'md': DocumentFormat.MD,
            'epub': DocumentFormat.EPUB,
            'jpg': DocumentFormat.JPG,
            'jpeg': DocumentFormat.JPEG,
            'png': DocumentFormat.PNG,
            'gif': DocumentFormat.GIF,
            'bmp': DocumentFormat.BMP,
            'tiff': DocumentFormat.TIFF,
        }
        
        return format_mapping.get(extension, DocumentFormat.UNKNOWN)
    
    def _validate_file(self, file_path: str) -> None:
        """Validate that the file exists and is readable"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Document not found: {file_path}")
        
        if not os.path.isfile(file_path):
            raise ValueError(f"Path is not a file: {file_path}")
        
        if not os.access(file_path, os.R_OK):
            raise PermissionError(f"File is not readable: {file_path}")
    
    def _validate_format_support(self, file_path: str) -> None:
        """Validate that the file format is supported"""
        file_format = self._determine_document_format(file_path)
        
        if file_format not in self.supported_formats:
            supported_extensions = [fmt.value for fmt in self.supported_formats]
            raise ValueError(
                f"Unsupported file format: {file_format.value}. "
                f"Supported formats: {supported_extensions}"
            )
    
    async def health_check(self) -> Dict[str, Any]:
        """Check if the parsing service is healthy"""
        try:
            # Create a simple test file for health check
            test_content = "This is a test document for parsing health check."
            test_file = "test_parsing_health_check.txt"
            
            # Write test file
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(test_content)
            
            try:
                # Test parsing
                result = await self.parse_document(test_file)
                
                return {
                    "status": "healthy",
                    "provider": self.name,
                    "method": self.config.method.value,
                    "test_parsing_successful": result is not None and result.content.strip() != "",
                    "supported_formats": [fmt.value for fmt in self.supported_formats],
                    "requires_api_key": self.requires_api_key
                }
            finally:
                # Clean up test file
                if os.path.exists(test_file):
                    os.remove(test_file)
                    
        except Exception as e:
            return {
                "status": "unhealthy",
                "provider": self.name,
                "method": self.config.method.value,
                "test_parsing_successful": False,
                "error_message": str(e)
            }


class AbstractBatchParsingGenerator(AbstractParsingGenerator):
    """Abstract base class for parsing generators that support batch processing"""
    
    @abstractmethod
    async def parse_documents_batch(
        self, 
        file_paths: List[str],
        custom_metadata_list: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> List[ParsingResult]:
        """
        Parse multiple documents in batch
        
        Args:
            file_paths: List of file paths to parse
            custom_metadata_list: Optional list of metadata for each document
            **kwargs: Additional parameters
            
        Returns:
            List of parsing results
        """
        pass
    
    async def parse_documents(
        self, 
        file_paths: List[str],
        custom_metadata_list: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> List[ParsingResult]:
        """Default implementation using batch processing"""
        return await self.parse_documents_batch(file_paths, custom_metadata_list, **kwargs)
