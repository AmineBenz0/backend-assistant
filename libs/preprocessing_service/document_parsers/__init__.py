"""
Document Parser Interface and Registry

This module provides a unified interface for parsing different document formats
and managing parser instances.
"""

import logging
from typing import Dict, List, Type, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)

# Import llama-index readers
try:
    # Try different import paths for llama-index
    try:
        # Try the most recent import paths
        from llama_index.core.readers import SimpleDirectoryReader
        from llama_index.core.readers.file import PDFReader
        from llama_index.core.schema import Document as LIDocument
        LLAMA_INDEX_AVAILABLE = True
        logger.info("llama-index imported successfully using core paths")
    except ImportError:
        try:
            # Fallback to older import paths
            from llama_index.readers import SimpleDirectoryReader
            from llama_index.readers.file import PDFReader
            from llama_index.schema import Document as LIDocument
            LLAMA_INDEX_AVAILABLE = True
            logger.info("llama-index imported successfully using legacy paths")
        except ImportError:
            # Try the most basic import
            import llama_index
            LLAMA_INDEX_AVAILABLE = True
            logger.info("llama-index imported successfully using basic import")
            # We'll need to handle the imports differently
            SimpleDirectoryReader = None
            PDFReader = None
            LIDocument = None
except ImportError as e:
    LLAMA_INDEX_AVAILABLE = False
    LIDocument = None
    logger.error(f"Failed to import llama-index: {e}")
    logger.error("llama-index is required for document parsing")


class PDFParser:
    """PDF document parser using llama-index"""
    
    def __init__(self):
        if not LLAMA_INDEX_AVAILABLE:
            raise ImportError("llama-index is required for PDF parsing")
        self.reader = PDFReader()
    
    def parse_document(self, file_path: Path) -> List[LIDocument]:
        """Parse PDF document"""
        try:
            documents = self.reader.load_data(file=file_path)
            logger.info(f"PDF parsed successfully: {len(documents)} pages")
            return documents
        except Exception as e:
            logger.error(f"Error parsing PDF {file_path}: {e}")
            raise


class TextParser:
    """Text document parser using llama-index"""
    
    def __init__(self):
        if not LLAMA_INDEX_AVAILABLE:
            raise ImportError("llama-index is required for text parsing")
        self.reader = SimpleDirectoryReader()
    
    def parse_document(self, file_path: Path) -> List[LIDocument]:
        """Parse text document"""
        try:
            documents = self.reader.load_data(files=[file_path])
            logger.info(f"Text parsed successfully: {len(documents)} documents")
            return documents
        except Exception as e:
            logger.error(f"Error parsing text {file_path}: {e}")
            raise


class FallbackPDFParser:
    """Fallback PDF parser using PyPDF2 when llama-index is not available"""
    
    def parse_document(self, file_path: Path) -> List[Any]:
        """Parse PDF document using PyPDF2 fallback method"""
        try:
            logger.warning("Using PyPDF2 fallback parser - llama-index not available")
            
            # Try to use PyPDF2 for real PDF parsing
            try:
                import PyPDF2
                
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    
                    # Extract text from all pages
                    text_content = ""
                    for page_num, page in enumerate(pdf_reader.pages):
                        page_text = page.extract_text()
                        if page_text:
                            text_content += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
                    
                    if not text_content.strip():
                        text_content = f"PDF content from {file_path.name} (text extraction failed)"
                    
                    logger.info(f"Extracted {len(text_content)} characters from PDF using PyPDF2")
                    
            except ImportError:
                logger.warning("PyPDF2 not available, using basic file info")
                text_content = f"PDF content from {file_path.name} (PyPDF2 not available)"
            except Exception as e:
                logger.warning(f"PyPDF2 parsing failed: {e}, using basic file info")
                text_content = f"PDF content from {file_path.name} (parsing failed: {e})"
            
            # Get file stats for metadata
            file_stat = file_path.stat()
            
            # Create a document with real or fallback content
            mock_doc = type('MockDocument', (), {
                'text': text_content,
                'metadata': {
                    'file_name': file_path.name,
                    'file_path': str(file_path),
                    'file_size': file_stat.st_size,
                    'format': 'pdf',  # Use lowercase enum value
                    'source': str(file_path),
                    'type': 'pdf'
                }
            })()
            return [mock_doc]
            
        except Exception as e:
            logger.error(f"Error in fallback PDF parsing {file_path}: {e}")
            raise


class FallbackTextParser:
    """Fallback text parser for when llama-index is not available"""
    
    def parse_document(self, file_path: Path) -> List[Any]:
        """Parse text document using fallback method"""
        try:
            logger.warning("Using fallback text parser - llama-index not available")
            
            # Read the file directly
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Get file stats for metadata
            file_stat = file_path.stat()
            
            # Create a simple mock document with proper metadata structure
            mock_doc = type('MockDocument', (), {
                'text': content,
                'metadata': {
                    'file_name': file_path.name,
                    'file_path': str(file_path),
                    'file_size': file_stat.st_size,
                    'format': 'txt',  # Use lowercase enum value
                    'source': str(file_path),
                    'type': 'txt'
                }
            })()
            return [mock_doc]
        except Exception as e:
            logger.error(f"Error in fallback text parsing {file_path}: {e}")
            raise


class DocumentParserRegistry:
    """Registry for document parsers"""
    
    def __init__(self):
        self._parsers: Dict[str, Type[Any]] = {}
        self._parser_instances: Dict[str, Any] = {}
        
        logger.info(f"Initializing DocumentParserRegistry, LLAMA_INDEX_AVAILABLE: {LLAMA_INDEX_AVAILABLE}")
        
        # Register default parsers (inline; no dynamic registration method)
        if LLAMA_INDEX_AVAILABLE and PDFReader and SimpleDirectoryReader:
            self._parsers["pdf"] = PDFParser
            self._parsers["txt"] = TextParser
            logger.info(f"Registered llama-index parsers: {list(self._parsers.keys())}")
        else:
            logger.warning("llama-index not available, registering fallback parsers")
            self._parsers["pdf"] = FallbackPDFParser
            self._parsers["txt"] = FallbackTextParser
            logger.info(f"Registered fallback parsers: {list(self._parsers.keys())}")
    
    # tests/optional method removed: register_parser
    
    def get_parser(self, format_name: str) -> Any:
        """Get parser instance for format"""
        logger.info(f"Getting parser for format: {format_name}")
        logger.info(f"Available parsers: {list(self._parsers.keys())}")
        
        if format_name not in self._parsers:
            raise ValueError(f"Unsupported format: {format_name}. Available formats: {list(self._parsers.keys())}")
        
        # Create instance if not cached
        if format_name not in self._parser_instances:
            self._parser_instances[format_name] = self._parsers[format_name]()
        
        return self._parser_instances[format_name]
    
    def list_supported_formats(self) -> List[str]:
        """List supported formats"""
        return list(self._parsers.keys())
    
    def has_parser(self, format_name: str) -> bool:
        """Check if format is supported"""
        return format_name in self._parsers


# Global registry instance
parser_registry = DocumentParserRegistry()


def get_parser(format_name: str) -> Any:
    """Get parser for format"""
    return parser_registry.get_parser(format_name)


def list_supported_formats() -> List[str]:
    """List supported formats"""
    return parser_registry.list_supported_formats()
