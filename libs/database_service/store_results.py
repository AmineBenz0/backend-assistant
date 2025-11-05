"""
General Storage Results Manager

Provides a flexible, database-agnostic way to store pipeline step results.
Supports multiple storage backends (MinIO, MongoDB, etc.) based on configuration.
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional, Union
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class StorageBackend(ABC):
    """Abstract base class for storage backends"""
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the storage backend"""
        pass
    
    @abstractmethod
    async def store_data(
        self, 
        job_id: str, 
        step_name: str, 
        data: Any, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Store data and return storage key/path"""
        pass
    
    @abstractmethod
    async def retrieve_data(self, storage_key: str) -> Any:
        """Retrieve data by storage key"""
        pass


class MinIOBackend(StorageBackend):
    """MinIO storage backend implementation"""
    
    def __init__(self):
        self.storage_manager = None
    
    async def initialize(self) -> bool:
        """Initialize MinIO storage manager"""
        try:
            from libs.database_service.storage import MinIOStorageManager
            import os
            
            self.storage_manager = MinIOStorageManager(
                endpoint=os.getenv("MINIO_ENDPOINT", "localhost:9000"),
                access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
                secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin"),
                secure=os.getenv("MINIO_SECURE", "false").lower() == "true",
            )
            
            return await self.storage_manager.initialize()
            
        except Exception as e:
            logger.error(f"Failed to initialize MinIO backend: {e}")
            return False
    
    async def store_data(
        self, 
        job_id: str, 
        step_name: str, 
        data: Any, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Store data in MinIO"""
        if not self.storage_manager:
            raise RuntimeError("MinIO backend not initialized")
        
        return await self.storage_manager.store_preprocessing_output(
            job_id, step_name, data, metadata
        )
    
    async def retrieve_data(self, storage_key: str) -> Any:
        """Retrieve data from MinIO"""
        if not self.storage_manager:
            raise RuntimeError("MinIO backend not initialized")
        
        # Parse storage key to extract bucket and object key
        # Format: bucket/object_key
        parts = storage_key.split('/', 1)
        if len(parts) != 2:
            raise ValueError(f"Invalid MinIO storage key format: {storage_key}")
        
        bucket, object_key = parts
        return await self.storage_manager.retrieve_output(bucket, object_key)


class MongoDBBackend(StorageBackend):
    """MongoDB storage backend implementation (placeholder for future)"""
    
    async def initialize(self) -> bool:
        """Initialize MongoDB connection"""
        logger.info("MongoDB backend not yet implemented")
        return False
    
    async def store_data(
        self, 
        job_id: str, 
        step_name: str, 
        data: Any, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Store data in MongoDB"""
        raise NotImplementedError("MongoDB backend not yet implemented")
    
    async def retrieve_data(self, storage_key: str) -> Any:
        """Retrieve data from MongoDB"""
        raise NotImplementedError("MongoDB backend not yet implemented")


class StoreResults:
    """
    General storage manager that can work with different storage backends
    based on configuration.
    """
    
    def __init__(self):
        self.backends = {
            'minio': MinIOBackend(),
            'mongodb': MongoDBBackend(),
        }
        self.initialized_backends = set()
    
    async def store_step_results(
        self,
        step_name: str,
        data: Any,
        project_name: str,
        storage_type: str,
        pipeline_key: Optional[str] = None,
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Store pipeline step results using the specified storage backend.
        
        Args:
            step_name: Name of the pipeline step
            data: Data to store
            project_name: Project name for organization
            storage_type: Storage backend type ('minio', 'mongodb', etc.)
            pipeline_key: Optional pipeline key for additional context
            additional_metadata: Optional additional metadata
            
        Returns:
            Storage key/path if successful, None if failed
        """
        try:
            # Validate storage type
            if storage_type not in self.backends:
                logger.error(f"Unsupported storage type: {storage_type}")
                return None
            
            backend = self.backends[storage_type]
            
            # Initialize backend if not already done
            if storage_type not in self.initialized_backends:
                logger.info(f"Initializing {storage_type} backend...")
                if not await backend.initialize():
                    logger.error(f"Failed to initialize {storage_type} backend")
                    return None
                self.initialized_backends.add(storage_type)
            
            # Create job ID
            job_id = f"{step_name}_{project_name}_{int(time.time())}"
            
            # Prepare metadata
            metadata = {
                "step": step_name,
                "project_name": project_name,
                "pipeline_key": pipeline_key,
                "storage_type": storage_type,
                "timestamp": time.time(),
                "data_type": type(data).__name__,
            }
            
            # Add data-specific metadata
            if isinstance(data, (list, dict)):
                if hasattr(data, '__len__'):
                    metadata["data_length"] = len(data)
            
            # Merge additional metadata
            if additional_metadata:
                metadata.update(additional_metadata)
            
            # Store data
            logger.info(f"Storing {step_name} results using {storage_type} backend...")
            storage_key = await backend.store_data(job_id, step_name, data, metadata)
            
            logger.info(f"Successfully stored {step_name} results with key: {storage_key}")
            return storage_key
            
        except Exception as e:
            logger.error(f"Failed to store {step_name} results using {storage_type}: {e}")
            return None
    
    async def retrieve_step_results(
        self,
        storage_key: str,
        storage_type: str
    ) -> Optional[Any]:
        """
        Retrieve pipeline step results using the specified storage backend.
        
        Args:
            storage_key: Storage key/path returned from store_step_results
            storage_type: Storage backend type ('minio', 'mongodb', etc.)
            
        Returns:
            Retrieved data if successful, None if failed
        """
        try:
            # Validate storage type
            if storage_type not in self.backends:
                logger.error(f"Unsupported storage type: {storage_type}")
                return None
            
            backend = self.backends[storage_type]
            
            # Initialize backend if not already done
            if storage_type not in self.initialized_backends:
                logger.info(f"Initializing {storage_type} backend...")
                if not await backend.initialize():
                    logger.error(f"Failed to initialize {storage_type} backend")
                    return None
                self.initialized_backends.add(storage_type)
            
            # Retrieve data
            logger.info(f"Retrieving data from {storage_type} with key: {storage_key}")
            data = await backend.retrieve_data(storage_key)
            
            logger.info(f"Successfully retrieved data from {storage_type}")
            return data
            
        except Exception as e:
            logger.error(f"Failed to retrieve data from {storage_type} with key {storage_key}: {e}")
            return None
    
    def store_step_results_sync(
        self,
        step_name: str,
        data: Any,
        project_name: str,
        storage_type: str,
        pipeline_key: Optional[str] = None,
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Synchronous wrapper for store_step_results.
        Useful for integration with existing synchronous pipeline code.
        """
        try:
            return asyncio.run(
                self.store_step_results(
                    step_name, data, project_name, storage_type, 
                    pipeline_key, additional_metadata
                )
            )
        except Exception as e:
            logger.error(f"Failed to store {step_name} results synchronously: {e}")
            return None


# Global instance for easy access
_store_results_instance = None

def get_store_results() -> StoreResults:
    """Get global StoreResults instance"""
    global _store_results_instance
    if _store_results_instance is None:
        _store_results_instance = StoreResults()
    return _store_results_instance