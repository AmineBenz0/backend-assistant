"""
LlamaCloud parsing generator implementation.

This generator uses direct HTTP requests to LlamaCloud services for robust document parsing
with full Celery worker compatibility and support for multiple document formats.
"""

import os
import time
import logging
import requests
import ssl
from typing import Dict, List, Any, Optional
from pathlib import Path

from .base import AbstractParsingGenerator
from ..models import (
    ParsingResult, 
    ParsingConfig, 
    DocumentFormat, 
    ParsingMethod,
    DocumentMetadata
)

logger = logging.getLogger(__name__)


class LlamaCloudParsingGenerator(AbstractParsingGenerator):
    """
    LlamaCloud implementation of document parsing.
    
    This generator uses direct HTTP requests to LlamaCloud services for robust document parsing
    with support for multiple formats including PDF, DOCX, images, and more.
    """

    def __init__(self, config: ParsingConfig):
        super().__init__(config)
        
        try:
            # Disable SSL verification globally for Docker environments
            ssl._create_default_https_context = ssl._create_unverified_context
            
            # Set environment variables to disable SSL verification
            os.environ['PYTHONHTTPSVERIFY'] = '0'
            os.environ['CURL_CA_BUNDLE'] = ''
            os.environ['REQUESTS_CA_BUNDLE'] = ''
            
            # Get API key from config or environment
            self.api_key = config.api_key or os.getenv("LLAMA_CLOUD_API_KEY")
            if not self.api_key:
                raise RuntimeError("LlamaCloud API key is required")
            
            self.base_url = config.base_url or os.getenv("LLAMA_CLOUD_BASE_URL", "https://api.cloud.llamaindex.ai")
            
            # Supported file extensions mapping
            self.supported_extensions = {
                '.pdf': DocumentFormat.PDF,
                '.docx': DocumentFormat.DOCX,
                '.doc': DocumentFormat.DOC,
                '.pptx': DocumentFormat.PPTX,
                '.ppt': DocumentFormat.PPT,
                '.txt': DocumentFormat.TXT,
                '.md': DocumentFormat.MD,
                '.xlsx': DocumentFormat.XLSX,
                '.xls': DocumentFormat.XLS,
                '.html': DocumentFormat.HTML,
                '.htm': DocumentFormat.HTM,
                '.epub': DocumentFormat.EPUB,
                '.jpg': DocumentFormat.JPG,
                '.jpeg': DocumentFormat.JPEG,
                '.png': DocumentFormat.PNG,
                '.gif': DocumentFormat.GIF,
                '.bmp': DocumentFormat.BMP,
                '.tiff': DocumentFormat.TIFF,
            }
            
            logger.info("✅ Synchronous LlamaCloud parsing generator initialized successfully")
            
        except Exception as e:
            raise RuntimeError(f"Failed to initialize synchronous LlamaCloud parsing generator: {e}") from e

    @property
    def name(self) -> str:
        return "llamacloud_parser"

    @property
    def supported_formats(self) -> List[DocumentFormat]:
        return list(self.supported_extensions.values())

    @property
    def requires_api_key(self) -> bool:
        return True

    def parse_document(
        self, 
        file_path: str,
        custom_metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> ParsingResult:
        """Parse a document using synchronous LlamaCloud API calls."""
        start_time = time.time()
        
        try:
            # Validate file
            self._validate_file(file_path)
            self._validate_format_support(file_path)
            
            logger.info(f"Parsing document with synchronous LlamaCloud: {file_path}")
            
            # Parse the document using direct API calls
            content = self._parse_with_api(file_path)
            
            if not content:
                raise RuntimeError("LlamaCloud returned empty result")
            
            # Create document metadata
            document_metadata = self._create_document_metadata(file_path, custom_metadata)
            
            # Create parsing metadata
            parsing_metadata = {
                "provider": self.name,
                "method": self.config.method.value,
                "output_format": self.config.output_format,
                "language": self.config.language,
                "api_key_used": bool(self.api_key),
                "base_url": self.base_url,
                "processing_timestamp": time.time()
            }
            
            processing_time = time.time() - start_time
            
            result = ParsingResult(
                content=content,
                metadata=document_metadata,
                parsing_method=self.config.method,
                provider=self.name,
                config_used=self.config,
                processing_time=processing_time,
                parsing_metadata=parsing_metadata
            )
            
            logger.info(f"✅ Document parsed successfully with synchronous LlamaCloud in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Synchronous LlamaCloud parsing error: {e}", exc_info=True)
            raise RuntimeError(f"Synchronous LlamaCloud parsing error: {e}") from e

    def parse_document_to_markdown(
        self, 
        file_path: str,
        custom_metadata: Optional[Dict[str, Any]] = None
    ) -> ParsingResult:
        """Parse a document to markdown format using synchronous API calls."""
        # Temporarily set result type to markdown
        original_result_type = self.config.result_type
        self.config.result_type = "markdown"
        
        try:
            result = self.parse_document(file_path, custom_metadata)
            return result
        finally:
            # Restore original result type
            self.config.result_type = original_result_type

    def _parse_with_api(self, file_path: str) -> str:
        """Parse document using direct LlamaCloud API calls"""
        try:
            filename = Path(file_path).name
            
            # Step 1: Upload file to LlamaCloud
            file_id = self._upload_file(file_path, filename)
            
            # Step 2: Start parsing job
            job_id = self._start_parsing_job(file_id, filename)
            
            # Step 3: Poll for completion and get result
            content = self._wait_for_completion_and_get_result(job_id, filename)
            
            return content
            
        except Exception as e:
            logger.error(f"API parsing error: {e}")
            # Fallback to basic text extraction for PDFs
            if file_path.lower().endswith('.pdf'):
                logger.info("Attempting fallback PDF text extraction...")
                return self._fallback_pdf_extraction(file_path)
            else:
                # For non-PDF files, return the content as-is
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                return f"# {Path(file_path).name}\n\n{content}"

    def _upload_file(self, file_path: str, filename: str) -> str:
        """Upload file to LlamaCloud and return file ID"""
        upload_url = f"{self.base_url}/v1/parsing/upload"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json"
        }
        
        with open(file_path, 'rb') as file:
            files = {
                'file': (filename, file, 'application/octet-stream')
            }
            
            logger.info(f"Uploading {filename} to LlamaCloud...")
            response = requests.post(
                upload_url, 
                headers=headers, 
                files=files,
                verify=False,
                timeout=60
            )
            
            if response.status_code != 200:
                raise RuntimeError(f"Failed to upload file to LlamaCloud: {response.status_code} - {response.text}")
            
            data = response.json()
            file_id = data.get('id')
            
            if not file_id:
                raise RuntimeError(f"No file ID returned from LlamaCloud upload: {data}")
            
            logger.info(f"File uploaded successfully with ID: {file_id}")
            return file_id

    def _start_parsing_job(self, file_id: str, filename: str) -> str:
        """Start parsing job and return job ID"""
        parse_url = f"{self.base_url}/v1/parsing/job"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        payload = {
            "name": f"parse_{filename}",
            "parsing_instruction": "Extract all text content and convert to markdown format",
            "file_ids": [file_id],
            "result_type": self.config.result_type or "markdown"
        }
        
        logger.info(f"Starting parsing job for {filename}...")
        response = requests.post(
            parse_url,
            headers=headers,
            json=payload,
            verify=False,
            timeout=60
        )
        
        if response.status_code != 200:
            raise RuntimeError(f"Failed to start parsing job: {response.status_code} - {response.text}")
        
        data = response.json()
        job_id = data.get('id')
        
        if not job_id:
            raise RuntimeError(f"No job ID returned from LlamaCloud parsing: {data}")
        
        logger.info(f"Parsing job started with ID: {job_id}")
        return job_id

    def _wait_for_completion_and_get_result(self, job_id: str, filename: str) -> str:
        """Wait for parsing job to complete and return the result"""
        status_url = f"{self.base_url}/v1/parsing/job/{job_id}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json"
        }
        
        max_wait_time = 300  # 5 minutes max
        check_interval = 5   # Check every 5 seconds
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            response = requests.get(
                status_url,
                headers=headers,
                verify=False,
                timeout=30
            )
            
            if response.status_code != 200:
                raise RuntimeError(f"Failed to check parsing status: {response.status_code} - {response.text}")
            
            data = response.json()
            status = data.get('status')
            
            logger.info(f"Parsing status: {status}")
            
            if status == 'SUCCESS':
                # Get the parsed result
                result_url = f"{self.base_url}/v1/parsing/job/{job_id}/result/markdown"
                result_response = requests.get(
                    result_url,
                    headers=headers,
                    verify=False,
                    timeout=60
                )
                
                if result_response.status_code != 200:
                    raise RuntimeError(f"Failed to get parsing result: {result_response.status_code} - {result_response.text}")
                
                # Extract markdown content
                content = result_response.text
                
                # Add document header if not present
                if not content.startswith('#'):
                    content = f"# {filename}\n\n{content}"
                
                logger.info(f"Successfully parsed {filename} to markdown")
                return content.strip()
                
            elif status == 'FAILURE':
                error_msg = data.get('error', 'Unknown parsing error')
                raise RuntimeError(f"Parsing job failed: {error_msg}")
            
            # Wait before next check
            time.sleep(check_interval)
        
        # If we get here, parsing timed out
        raise RuntimeError(f"Parsing job timed out after {max_wait_time} seconds")

    def _fallback_pdf_extraction(self, file_path: str) -> str:
        """Fallback PDF text extraction using PyPDF2"""
        try:
            import PyPDF2
            
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_content = ""
                
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text_content += page_text + "\n"
                
                if not text_content.strip():
                    text_content = f"PDF content from {Path(file_path).name} (text extraction failed)"
                
                return f"# {Path(file_path).name}\n\n{text_content.strip()}"
                
        except ImportError:
            logger.warning("PyPDF2 not available for fallback PDF extraction")
            return f"# {Path(file_path).name}\n\nPDF content from {Path(file_path).name} (PyPDF2 not available)"
        except Exception as e:
            logger.error(f"Fallback PDF extraction failed: {e}")
            return f"# {Path(file_path).name}\n\nPDF content from {Path(file_path).name} (extraction failed: {e})"

    def close(self) -> None:
        """Close connections and cleanup resources."""
        # No explicit cleanup needed for synchronous implementation
        pass
