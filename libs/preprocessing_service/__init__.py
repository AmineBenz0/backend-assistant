"""
Preprocessing Service for Kotaemon

This service handles document processing and parsing using llama-index readers.
It follows the pattern of:
- Simple parser classes for each document format
- Registry pattern for managing parsers
- Direct integration with llama-index Document objects

Main Components:
- DocumentParserInterface: Base interface for document parsers
- DocumentParserRegistry: Registry for managing parser instances
- PDFParser: PDF document parser using llama-index
- TextParser: Text document parser using llama-index
"""

from .document_parsers import (
    DocumentParserRegistry,
    PDFParser,
    TextParser,
    get_parser,
    list_supported_formats,
    parser_registry
)
# Optional/test-only components removed from public exports
from .models import TextUnit
from .helpers import TextUnitProcessor
from .helpers.document_processor import DocumentProcessor, BaseDocument, FinalDocument
# from .graph_integration import GraphIntegrationAdapter, GraphProcessingPipeline

__all__ = [
    # Parser registry
    "DocumentParserRegistry",
    
    # Concrete implementations
    "PDFParser",
    "TextParser",
    
    # GraphRAG components (runtime)
    "TextUnit",
    "TextUnitProcessor",
    "DocumentProcessor",
    "BaseDocument",
    "FinalDocument",
    
    # Utility functions
    "get_parser",
    "list_supported_formats",
    
    # Global registry
    "parser_registry",
]
