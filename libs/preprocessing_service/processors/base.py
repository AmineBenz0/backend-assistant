"""
Abstract base classes for document processors
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, AsyncGenerator
import uuid
import time

from ..models import (
    ProcessingJob, ProcessingResult, ProcessingConfig,
    ProcessingStatus, ProcessingProgress
)


class AbstractDocumentProcessor(ABC):
    """Abstract base class for document processors"""
    
    def __init__(self):
        self.active_jobs: Dict[str, ProcessingJob] = {}
        self.job_results: Dict[str, ProcessingResult] = {}
    
    @abstractmethod
    async def process_documents(
        self, 
        file_paths: List[str],
        config: ProcessingConfig,
        job_id: Optional[str] = None
    ) -> ProcessingResult:
        """
        Process documents according to configuration
        
        Args:
            file_paths: List of file paths to process
            config: Processing configuration
            job_id: Optional job ID for tracking
            
        Returns:
            Processing result
        """
        pass
    
    @abstractmethod
    async def process_documents_stream(
        self, 
        file_paths: List[str],
        config: ProcessingConfig,
        job_id: Optional[str] = None
    ) -> AsyncGenerator[ProcessingProgress, None]:
        """
        Process documents with progress streaming
        
        Args:
            file_paths: List of file paths to process
            config: Processing configuration
            job_id: Optional job ID for tracking
            
        Yields:
            Processing progress updates, with the final ProcessingResult as the last yielded item
        """
        pass
    
    def create_job(
        self, 
        file_paths: List[str],
        config: ProcessingConfig
    ) -> ProcessingJob:
        """Create a new processing job"""
        job_id = str(uuid.uuid4())
        
        job = ProcessingJob(
            job_id=job_id,
            files=file_paths,
            config=config,
            status=ProcessingStatus.PENDING
        )
        
        self.active_jobs[job_id] = job
        return job
    
    def get_job(self, job_id: str) -> Optional[ProcessingJob]:
        """Get job by ID"""
        return self.active_jobs.get(job_id)
    
    def get_job_result(self, job_id: str) -> Optional[ProcessingResult]:
        """Get job result by ID"""
        return self.job_results.get(job_id)
    
    def update_job_status(
        self, 
        job_id: str, 
        status: ProcessingStatus,
        progress: float = 0.0,
        error_message: Optional[str] = None
    ):
        """Update job status"""
        if job_id in self.active_jobs:
            job = self.active_jobs[job_id]
            job.status = status
            job.progress = progress
            
            if error_message:
                job.error_message = error_message
            
            if status == ProcessingStatus.PROCESSING and job.started_at is None:
                job.started_at = time.time()
            elif status in [ProcessingStatus.COMPLETED, ProcessingStatus.FAILED]:
                job.completed_at = time.time()
    
    def list_active_jobs(self) -> List[ProcessingJob]:
        """List all active jobs"""
        return list(self.active_jobs.values())
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a job"""
        if job_id in self.active_jobs:
            job = self.active_jobs[job_id]
            if job.status in [ProcessingStatus.PENDING, ProcessingStatus.PROCESSING]:
                job.status = ProcessingStatus.CANCELLED
                return True
        return False
    
    async def cleanup_completed_jobs(self, max_age_hours: int = 24):
        """Clean up old completed jobs"""
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        jobs_to_remove = []
        
        for job_id, job in self.active_jobs.items():
            if (job.status in [ProcessingStatus.COMPLETED, ProcessingStatus.FAILED, ProcessingStatus.CANCELLED] and
                job.completed_at and 
                current_time - job.completed_at > max_age_seconds):
                jobs_to_remove.append(job_id)
        
        for job_id in jobs_to_remove:
            del self.active_jobs[job_id]
            if job_id in self.job_results:
                del self.job_results[job_id]
    
    async def health_check(self) -> Dict[str, Any]:
        """Check processor health"""
        return {
            "status": "healthy",
            "active_jobs": len(self.active_jobs),
            "completed_jobs": len([j for j in self.active_jobs.values() 
                                 if j.status == ProcessingStatus.COMPLETED]),
            "failed_jobs": len([j for j in self.active_jobs.values() 
                               if j.status == ProcessingStatus.FAILED])
        }

