"""
Storage Manager for Database Service

Handles MinIO operations for storing intermediate outputs from the preprocessing pipeline
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, BinaryIO
from datetime import datetime
from pathlib import Path
import json
import pickle
import io
import uuid

logger = logging.getLogger(__name__)


class MinIOStorageManager:
    """Manages MinIO operations for storing intermediate outputs"""
    
    def __init__(
        self,
        endpoint: str = "localhost:9000",
        access_key: str = "minioadmin",
        secret_key: str = "minioadmin",
        secure: bool = False
    ):
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key
        self.secure = secure
        self._client = None
        self._initialized = False
    
    async def initialize(self) -> bool:
        """Initialize MinIO client"""
        try:
            logger.info(f"Initializing MinIO client for endpoint: {self.endpoint}")
            # Import minio here to avoid dependency issues
            from minio import Minio
            
            logger.info("MinIO import successful, creating client...")
            self._client = Minio(
                self.endpoint,
                access_key=self.access_key,
                secret_key=self.secret_key,
                secure=self.secure
            )
            logger.info("MinIO client created, testing connection...")
            
            # Test connection
            buckets = self._client.list_buckets()
            logger.info(f"Connection test successful, found {len(list(buckets))} buckets")
            self._initialized = True
            logger.info("MinIO Storage Manager initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize MinIO Storage Manager: {str(e)}")
            logger.error(f"Exception type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    async def ensure_bucket(self, bucket_name: str) -> bool:
        """Ensure bucket exists, create if it doesn't"""
        try:
            logger.info(f"ensure_bucket called with bucket_name: {bucket_name}")
            logger.info(f"self._initialized: {self._initialized}")
            logger.info(f"self._client: {self._client}")
            
            if not self._initialized:
                logger.info("Not initialized, calling initialize...")
                await self.initialize()
                logger.info(f"After initialize, self._initialized: {self._initialized}")
            
            logger.info(f"Checking if bucket {bucket_name} exists...")
            bucket_exists = self._client.bucket_exists(bucket_name)
            logger.info(f"Bucket {bucket_name} exists: {bucket_exists}")
            
            if not bucket_exists:
                logger.info(f"Creating bucket: {bucket_name}")
                self._client.make_bucket(bucket_name)
                logger.info(f"Created bucket: {bucket_name}")
            else:
                logger.info(f"Bucket {bucket_name} already exists")
            
            logger.info(f"ensure_bucket returning True for {bucket_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to ensure bucket {bucket_name}: {str(e)}")
            logger.error(f"Exception type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    async def store_preprocessing_output(
        self,
        job_id: str,
        output_type: str,
        data: Any,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Store preprocessing output in MinIO"""
        try:
            if not self._initialized:
                await self.initialize()
            
            # Debug logging
            logger.info(f"Storing preprocessing output - job_id: {job_id}, output_type: {output_type}")
            logger.info(f"Data type: {type(data)}, Data length: {len(data) if hasattr(data, '__len__') else 'N/A'}")
            if data and hasattr(data, '__len__') and len(data) > 0:
                if isinstance(data, dict):
                    # Handle dictionary data
                    first_key = list(data.keys())[0]
                    first_value = data[first_key]
                    logger.info(f"First key: {first_key}, First value type: {type(first_value)}, First value length: {len(first_value) if hasattr(first_value, '__len__') else 'N/A'}")
                    if hasattr(first_value, '__len__') and len(first_value) > 0:
                        first_item = first_value[0]
                        if isinstance(first_item, dict) and 'embedding' in first_item:
                            # Truncate embedding for logging
                            truncated_item = first_item.copy()
                            if isinstance(truncated_item['embedding'], list) and len(truncated_item['embedding']) > 5:
                                truncated_item['embedding'] = truncated_item['embedding'][:3] + ['...'] + [f"({len(first_item['embedding'])} total)"]
                            logger.info(f"First item in first value: {truncated_item}")
                        else:
                            logger.info(f"First item in first value: {first_value[0]}")
                elif isinstance(data, list):
                    # Handle list data
                    first_item = data[0]
                    if isinstance(first_item, dict) and 'embedding' in first_item:
                        # Truncate embedding for logging
                        truncated_item = first_item.copy()
                        if isinstance(truncated_item['embedding'], list) and len(truncated_item['embedding']) > 5:
                            truncated_item['embedding'] = truncated_item['embedding'][:3] + ['...'] + [f"({len(first_item['embedding'])} total)"]
                        logger.info(f"First item type: {type(data[0])}, First item: {truncated_item}")
                    else:
                        logger.info(f"First item type: {type(data[0])}, First item: {data[0]}")
                else:
                    logger.info(f"Data structure: {data}")
            
            bucket_name = "preprocessing-outputs"
            logger.info(f"About to ensure bucket: {bucket_name}")
            bucket_result = await self.ensure_bucket(bucket_name)
            logger.info(f"ensure_bucket result: {bucket_result}")
            
            if not bucket_result:
                logger.error(f"Failed to ensure bucket {bucket_name}")
                raise Exception(f"Failed to ensure bucket {bucket_name}")
            
            logger.info(f"Bucket {bucket_name} is ready, proceeding with storage...")
            
            # Create object key
            timestamp = datetime.now().isoformat()
            object_key = f"{job_id}/{output_type}/{timestamp}"
            
            # Serialize data based on type
            if isinstance(data, (dict, list)):
                serialized_data = json.dumps(data, default=str).encode('utf-8')
                content_type = "application/json"
            elif isinstance(data, str):
                serialized_data = data.encode('utf-8')
                content_type = "text/plain"
            else:
                # Use pickle for complex objects
                serialized_data = pickle.dumps(data)
                content_type = "application/octet-stream"
            
            # Store data
            logger.info(f"About to store data object: {object_key}")
            logger.info(f"Data size: {len(serialized_data)} bytes")
            logger.info(f"Content type: {content_type}")
            
            try:
                self._client.put_object(
                    bucket_name,
                    object_key,
                    io.BytesIO(serialized_data),
                    len(serialized_data),
                    content_type=content_type
                )
                logger.info(f"Successfully stored data object: {object_key}")
            except Exception as e:
                logger.error(f"Failed to store data object {object_key}: {e}")
                raise
            
            # Also store a "latest" symlink for easy retrieval
            latest_key = f"{job_id}/{output_type}/latest"
            logger.info(f"About to store latest symlink: {latest_key}")
            
            try:
                self._client.put_object(
                    bucket_name,
                    latest_key,
                    io.BytesIO(serialized_data),
                    len(serialized_data),
                    content_type=content_type
                )
                logger.info(f"Successfully stored latest symlink: {latest_key}")
            except Exception as e:
                logger.error(f"Failed to store latest symlink {latest_key}: {e}")
                raise
            
            # Store metadata if provided
            if metadata:
                metadata_key = f"{job_id}/{output_type}/{timestamp}.metadata.json"
                metadata_data = json.dumps(metadata, default=str).encode('utf-8')
                self._client.put_object(
                    bucket_name,
                    metadata_key,
                    io.BytesIO(metadata_data),
                    len(metadata_data),
                    content_type="application/json"
                )
            
            logger.info(f"Stored {output_type} output for job {job_id}: {object_key}")
            return object_key
            
        except Exception as e:
            logger.error(f"Failed to store preprocessing output: {str(e)}")
            raise
    
    async def store_embeddings_output(
        self,
        job_id: str,
        embeddings: List[Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Store embeddings output"""
        return await self.store_preprocessing_output(
            job_id, "embeddings", embeddings, metadata
        )
    
    async def retrieve_output(
        self,
        bucket_name: str,
        object_key: str,
        output_type: str = "json"
    ) -> Any:
        """Retrieve stored output from MinIO"""
        try:
            if not self._initialized:
                await self.initialize()
            
            # Get object
            response = self._client.get_object(bucket_name, object_key)
            data = response.read()
            
            # Deserialize based on type
            if output_type == "json":
                return json.loads(data.decode('utf-8'))
            elif output_type == "text":
                return data.decode('utf-8')
            elif output_type == "binary":
                return data  # Return raw bytes for PDFs and other binary files
            elif output_type == "pickle":
                return pickle.loads(data)
            else:
                return data
                
        except Exception as e:
            logger.error(f"Failed to retrieve output {object_key}: {str(e)}")
            raise

    async def store_output(
        self,
        bucket: str,
        key: str,
        data: Any,
        output_type: str = "json"
    ) -> str:
        """Store data directly to MinIO bucket/key"""
        try:
            if not self._initialized:
                await self.initialize()
            
            await self.ensure_bucket(bucket)
            
            # Serialize data based on type
            if output_type == "json":
                if isinstance(data, (dict, list)):
                    serialized_data = json.dumps(data, default=str).encode('utf-8')
                else:
                    serialized_data = str(data).encode('utf-8')
                content_type = "application/json"
            elif output_type == "text":
                serialized_data = str(data).encode('utf-8')
                content_type = "text/plain"
            elif output_type == "binary":
                serialized_data = data if isinstance(data, bytes) else str(data).encode('utf-8')
                content_type = "application/octet-stream"
            else:
                serialized_data = pickle.dumps(data)
                content_type = "application/octet-stream"
            
            # Store data
            self._client.put_object(
                bucket,
                key,
                io.BytesIO(serialized_data),
                len(serialized_data),
                content_type=content_type
            )
            
            logger.info(f"Stored data to {bucket}/{key}")
            return key
            
        except Exception as e:
            logger.error(f"Failed to store data to {bucket}/{key}: {str(e)}")
            raise

    async def list_objects(self, bucket: str, prefix: str = "") -> List[Any]:
        """List objects in MinIO bucket with optional prefix"""
        try:
            if not self._initialized:
                await self.initialize()
            
            objects = self._client.list_objects(bucket, prefix=prefix, recursive=True)
            return list(objects)
            
        except Exception as e:
            logger.error(f"Failed to list objects in bucket {bucket} with prefix {prefix}: {str(e)}")
            return []

    async def close(self):
        """Close MinIO client connection"""
        try:
            if self._initialized and self._client:
                # MinIO client doesn't have a close method, just mark as not initialized
                self._initialized = False
                logger.info("MinIO Storage Manager closed")
        except Exception as e:
            logger.error(f"Error closing MinIO Storage Manager: {str(e)}")

    # ============================================================================
    # Added methods
    # ============================================================================
    
    async def get_file_info(self, bucket_name: str, object_key: str) -> Optional[Dict[str, Any]]:
        """Get file information from MinIO"""
        try:
            if not self._initialized:
                await self.initialize()
            
            stat = self._client.stat_object(bucket_name, object_key)
            
            # Extract original filename from metadata if available
            original_filename = None
            if hasattr(stat, 'metadata') and stat.metadata:
                original_filename = stat.metadata.get('original_filename')
            
            # If no metadata, try to extract from object name
            if not original_filename and '_' in object_key:
                # Extract filename after the last underscore (UUID_filename format)
                original_filename = object_key.split('_', 1)[1] if '_' in object_key else object_key.split('/')[-1]
            
            return {
                "object_name": object_key,
                "original_filename": original_filename,
                "size": stat.size,
                "last_modified": stat.last_modified.isoformat() if stat.last_modified else None,
                "content_type": stat.content_type,
                "metadata": stat.metadata
            }
            
        except Exception as e:
            logger.error(f"Failed to get file info for {object_key} in bucket {bucket_name}: {e}")
            return None
    
    async def archive_file(self, bucket_name: str, object_key: str, archive_prefix: str = "archives") -> bool:
        """Archive a file instead of deleting it"""
        try:
            if not self._initialized:
                await self.initialize()
            
            # Create archive path
            archive_key = f"{archive_prefix}/{object_key}"
            
            # Copy object to archive location
            self._client.copy_object(
                bucket_name=bucket_name,
                object_source=object_key,
                object_name=archive_key
            )
            
            # Delete original object
            await self.delete_object(bucket_name, object_key)
            
            logger.info(f"Archived file from {object_key} to {archive_key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to archive file {object_key}: {e}")
            return False
    
    async def upload_file_with_structure(
        self, 
        file_data: bytes, 
        filename: str, 
        client_id: str, 
        project_id: str, 
        content_type: str = None,
        bucket_name: str = "documents"
    ) -> str:
        """Upload file with client/project structure"""
        try:
            if not self._initialized:
                await self.initialize()
            
            await self.ensure_bucket(bucket_name)
            
            # Create structured object key
            object_key = f"{client_id}/{project_id}/{uuid.uuid4()}_{filename}"
            
            # Store with metadata
            metadata = {
                "original_filename": filename,
                "client_id": client_id,
                "project_id": project_id
            }
            
            # Store file data
            self._client.put_object(
                bucket_name,
                object_key,
                io.BytesIO(file_data),
                len(file_data),
                content_type=content_type or "application/octet-stream",
                metadata=metadata
            )
            
            # Store metadata separately for easy retrieval
            metadata_key = f"{object_key}.metadata.json"
            await self.store_output(bucket_name, metadata_key, metadata, "json")
            
            logger.info(f"Uploaded file with structure: {object_key}")
            return object_key
            
        except Exception as e:
            logger.error(f"Failed to upload file with structure: {e}")
            raise
