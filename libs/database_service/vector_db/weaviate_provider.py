import os
import logging
import weaviate
import weaviate.classes as wvc
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
from .base import BaseVectorProvider

logger = logging.getLogger(__name__)

class WeaviateVectorProvider(BaseVectorProvider):
    """Weaviate implementation of VectorDBProvider."""

    def __init__(self, url: Optional[str] = None, api_key: Optional[str] = None, 
                 collection_name: Optional[str] = None, **kwargs: Any):
        from ..models import VectorIndexConfig
        
        # Create a simple config for Weaviate
        config = VectorIndexConfig(
            name=collection_name or os.getenv("WEAVIATE_COLLECTION_NAME", "documents"),
            vector_db_type="weaviate",
            description="Weaviate vector database",
            weaviate_url=url or os.getenv("WEAVIATE_URL", "http://localhost:8082"),
            weaviate_api_key=api_key or os.getenv("WEAVIATE_API_KEY")
        )
        super().__init__(config)
        
        self.url = config.weaviate_url
        self.api_key = config.weaviate_api_key
        self.base_collection_name = config.name
        self.client = None

    async def initialize(self) -> bool:
        """Initialize the Weaviate client"""
        print("🔍 [DEBUG] WeaviateVectorProvider.initialize() - START")
        print(f"🔍 [DEBUG] URL: {self.url}")
        print(f"🔍 [DEBUG] API Key: {'SET' if self.api_key else 'NOT SET'}")
        print(f"🔍 [DEBUG] Collection: {self.base_collection_name}")
        
        try:
            logger.info(f"Initializing Weaviate client with URL: {self.url}")
            parsed_url = urlparse(self.url)
            logger.info(f"Parsed URL - Host: {parsed_url.hostname}, Port: {parsed_url.port or 8082}, Secure: {parsed_url.scheme == 'https'}")
            
            print(f"🔍 [DEBUG] Parsed URL - Host: {parsed_url.hostname}, Port: {parsed_url.port or 8082}")
            
            # Create auth credentials if API key is provided
            auth_credentials = None
            if self.api_key:
                print("🔍 [DEBUG] Using API key authentication")
                logger.info("Using API key authentication")
                auth_credentials = weaviate.auth.AuthApiKey(self.api_key)
            else:
                print("🔍 [DEBUG] No API key provided, using anonymous access")
                logger.info("No API key provided, using anonymous access")
            
            # Use asyncio to run the synchronous Weaviate operations in a thread pool
            # This follows the same pattern as Neo4j provider
            import asyncio
            
            def _create_client():
                print("🔍 [DEBUG] Creating Weaviate client...")
                print(f"🔍 [DEBUG] HTTP Host: {parsed_url.hostname}")
                print(f"🔍 [DEBUG] HTTP Port: {parsed_url.port or 8082}")
                print(f"🔍 [DEBUG] HTTP Secure: {parsed_url.scheme == 'https'}")
                print(f"🔍 [DEBUG] Auth Credentials: {'SET' if auth_credentials else 'NONE'}")
                
                try:
                    client = weaviate.connect_to_custom(
                        http_host=parsed_url.hostname,
                        http_port=parsed_url.port or 8082,
                        http_secure=parsed_url.scheme == "https",
                        grpc_host=parsed_url.hostname,
                        grpc_port=50051,
                        grpc_secure=False,
                        auth_credentials=auth_credentials
                    )
                    print("🔍 [DEBUG] Weaviate client created successfully")
                    return client
                except Exception as e:
                    print(f"🔍 [DEBUG] ERROR creating Weaviate client: {e}")
                    raise
            
            def _test_connection(client):
                """Test Weaviate connection with retry logic"""
                print("🔍 [DEBUG] Testing Weaviate connection...")
                max_retries = 3
                for attempt in range(max_retries):
                    print(f"🔍 [DEBUG] Connection test attempt {attempt + 1}/{max_retries}")
                    try:
                        if client.is_ready():
                            print("🔍 [DEBUG] Weaviate connection test PASSED")
                            return True
                        else:
                            print(f"🔍 [DEBUG] Weaviate readiness check failed, attempt {attempt + 1}/{max_retries}")
                            logger.warning(f"Weaviate readiness check failed, attempt {attempt + 1}/{max_retries}")
                            if attempt < max_retries - 1:
                                import time
                                time.sleep(2)  # Wait 2 seconds before retry
                    except Exception as e:
                        print(f"🔍 [DEBUG] Weaviate readiness check error on attempt {attempt + 1}: {e}")
                        logger.warning(f"Weaviate readiness check error on attempt {attempt + 1}: {e}")
                        if attempt < max_retries - 1:
                            import time
                            time.sleep(2)
                print("🔍 [DEBUG] Weaviate connection test FAILED after all retries")
                return False
            
            # Run client creation in thread pool (following Neo4j pattern)
            print("🔍 [DEBUG] Running client creation in thread pool...")
            loop = asyncio.get_event_loop()
            self.client = await loop.run_in_executor(None, _create_client)
            print("🔍 [DEBUG] Weaviate client created, checking if ready...")
            logger.info("Weaviate client created, checking if ready...")
            
            # Test connection in thread pool
            print("🔍 [DEBUG] Testing connection in thread pool...")
            connection_success = await loop.run_in_executor(None, _test_connection, self.client)
            
            if connection_success:
                print("🔍 [DEBUG] Weaviate is ready, initialization successful")
                logger.info("Weaviate is ready, initialization successful")
                self._initialized = True
                print(f"🔍 [DEBUG] Weaviate provider initialized with base collection: {self.base_collection_name}")
                logger.info(f"Weaviate provider initialized with base collection: {self.base_collection_name}")
                return True
            else:
                print("🔍 [DEBUG] Weaviate is not ready after multiple attempts")
                raise RuntimeError("Weaviate is not ready after multiple attempts.")
            
        except Exception as e:
            print(f"🔍 [DEBUG] ERROR in WeaviateVectorProvider.initialize(): {e}")
            logger.error(f"Failed to initialize Weaviate: {e}")
            import traceback
            print(f"🔍 [DEBUG] Traceback: {traceback.format_exc()}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            self._initialized = False
            return False

    def _get_collection_name(self, client_id: str) -> str:
        """Get the collection name for a specific client."""
        return f"{self.base_collection_name}_{client_id}"

    def _ensure_schema(self, client_id: str):
        """Ensure the collection schema exists for a specific client."""
        try:
            collection_name = self._get_collection_name(client_id)
            
            # Check if collection exists
            if self.client.collections.exists(collection_name):
                logger.info(f"Weaviate collection '{collection_name}' already exists")
                return
            
            # Create collection if it doesn't exist - simple configuration without automatic vectorizer
            self.client.collections.create(
                name=collection_name,
                properties=[
                    wvc.config.Property(name="text", data_type=wvc.config.DataType.TEXT),
                    wvc.config.Property(name="client_id", data_type=wvc.config.DataType.TEXT),
                    wvc.config.Property(name="project_id", data_type=wvc.config.DataType.TEXT),
                    wvc.config.Property(name="object_name", data_type=wvc.config.DataType.TEXT),
                    wvc.config.Property(name="chunk_id", data_type=wvc.config.DataType.INT),
                ]
            )
            logger.info(f"Created Weaviate collection: {collection_name}")
            
        except Exception as e:
            # If collection creation fails due to existing collection, log and continue
            if "already exists" in str(e):
                logger.info(f"Weaviate collection '{collection_name}' already exists (handled gracefully)")
                return
            raise RuntimeError(f"Failed to ensure Weaviate schema: {e}") from e

    async def store_chunks(self, chunks: List[Dict[str, Any]], client_id: str, project_id: str) -> Dict[str, Any]:
        """Store document chunks with embeddings, scoped to client_id and project_id."""
        try:
            if not self._initialized or not self.client:
                raise RuntimeError("Weaviate client not initialized")
            
            # Ensure schema exists for this client
            self._ensure_schema(client_id)
            
            # Use asyncio to run the synchronous Weaviate operations in a thread pool
            import asyncio
            
            def _store_chunks_sync():
                collection_name = self._get_collection_name(client_id)
                collection = self.client.collections.get(collection_name)
                successful_uuids = []
                failed_count = 0
                attempted_count = 0
                
                logger.info(f"Storing {len(chunks)} chunks in Weaviate collection: {collection_name}")
                
                with collection.batch.dynamic() as batch:
                    for chunk in chunks:
                        attempted_count += 1
                        # Derive object_name from chunk metadata if not present at root
                        object_name = (
                            chunk.get("object_name")
                            or chunk.get("metadata", {}).get("source_document", {}).get("object_name", "")
                        )

                        # Weaviate schema defines chunk_id as INT; use chunk_index from metadata
                        chunk_index = chunk.get("metadata", {}).get("chunk_index")
                        try:
                            chunk_id_value = int(chunk_index) if chunk_index is not None else 0
                        except (TypeError, ValueError):
                            chunk_id_value = 0

                        data_object = {
                            "text": chunk["text"],
                            "client_id": client_id,
                            "project_id": project_id,
                            "object_name": object_name,
                            "chunk_id": chunk_id_value,
                        }
                        
                        # Add object to batch and collect UUID
                        batch_result = batch.add_object(
                            properties=data_object,
                            vector=chunk.get("embedding")  # Assume embedding is pre-computed if needed
                        )
                        
                        # Collect successful UUIDs
                        if hasattr(batch_result, 'uuid'):
                            successful_uuids.append(str(batch_result.uuid))
                        elif hasattr(batch_result, 'id'):
                            successful_uuids.append(str(batch_result.id))
                
                # Check for batch errors
                if hasattr(batch, 'number_errors') and batch.number_errors > 0:
                    failed_count = batch.number_errors
                    logger.warning(f"Batch insert had {failed_count} errors")
                
                # Derive stored count even if UUIDs are not returned by the SDK
                stored_count = max(0, attempted_count - failed_count)
                
                logger.info(f"Successfully stored {stored_count} chunks in Weaviate")
                
                return {
                    "stored_chunks": stored_count,  # Match gateway expectation
                    "stored_count": stored_count,   # Keep for backward compatibility
                    "failed_count": failed_count,
                    "successful_uuids": successful_uuids     # Match gateway expectation
                }
            
            # Run the synchronous operation in a thread pool
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, _store_chunks_sync)
        
        except Exception as e:
            logger.error(f"Failed to store chunks in Weaviate: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise RuntimeError(f"Failed to store chunks in Weaviate: {e}") from e

    async def similarity_search(self, query: str, client_id: str, project_id: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Perform similarity search scoped to client_id and project_id."""
        try:
            if not self._initialized or not self.client:
                raise RuntimeError("Weaviate client not initialized")
            
            # Use asyncio to run the synchronous Weaviate operations in a thread pool
            import asyncio
            
            def _search_sync():
                collection_name = self._get_collection_name(client_id)
                collection = self.client.collections.get(collection_name)
                response = collection.query.near_text(
                    query=query,
                    filters=wvc.query.Filter.by_property("project_id").equal(project_id),
                    limit=top_k,
                    return_properties=["text", "client_id", "project_id", "object_name", "chunk_id"]
                )
                return [obj.properties for obj in response.objects]
            
            # Run the synchronous operation in a thread pool
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, _search_sync)
        
        except Exception as e:
            raise RuntimeError(f"Failed to perform similarity search in Weaviate: {e}") from e

    def delete_chunks(self, client_id: str, project_id: str, object_name: str) -> Dict[str, Any]:
        """Delete chunks associated with a document in a client's project."""
        try:
            collection_name = self._get_collection_name(client_id)
            collection = self.client.collections.get(collection_name)
            delete_filter = (
                wvc.query.Filter.by_property("project_id").equal(project_id)
                & wvc.query.Filter.by_property("object_name").equal(object_name)
            )
            result = collection.data.delete_many(where=delete_filter)
            return {"deleted_count": result.successful, "failed_count": result.failed}
        
        except Exception as e:
            raise RuntimeError(f"Failed to delete chunks in Weaviate: {e}") from e
    
    def delete_document_chunks(self, client_id: str, project_id: str, object_name: str) -> Dict[str, Any]:
        """Alias for delete_chunks for backward compatibility."""
        return self.delete_chunks(client_id, project_id, object_name)

    def name(self) -> str:
        return "weaviate"
    
    def get_collection_stats(self, client_id: str) -> Dict[str, Any]:
        """Get collection statistics for a specific client."""
        try:
            collection_name = self._get_collection_name(client_id)
            collection = self.client.collections.get(collection_name)
            stats = collection.aggregate.over_all(total_count=True)
            return {
                "total_count": stats.total_count,
                "collection_name": collection_name,
                "client_id": client_id
            }
        except Exception as e:
            raise RuntimeError(f"Failed to get collection stats: {e}") from e

    async def create_index(self) -> bool:
        """Create a new vector index"""
        return True  # Weaviate creates collections automatically
    
    async def delete_index(self) -> bool:
        """Delete the vector index"""
        return True  # Not implemented for Weaviate
    
    async def add_documents(self, documents: List[Any]) -> List[str]:
        """Add documents to the index"""
        return []  # Not implemented for Weaviate
    
    async def update_documents(self, documents: List[Any]) -> bool:
        """Update existing documents"""
        return True  # Not implemented for Weaviate
    
    async def delete_documents(self, document_ids: List[str]) -> bool:
        """Delete documents from the index"""
        return True  # Not implemented for Weaviate
    
    async def get_document(self, document_id: str) -> Optional[Any]:
        """Retrieve a specific document"""
        return None  # Not implemented for Weaviate
    
    async def get_index_stats(self) -> Dict[str, Any]:
        """Get index statistics"""
        return {"total_count": 0}
    
    async def health_check(self) -> Dict[str, Any]:
        """Check provider health"""
        return {"status": "healthy" if self._initialized else "unhealthy"}

    async def close(self) -> None:
        """Close the Weaviate connection."""
        if hasattr(self, 'client') and self.client:
            self.client.close()
            logger.info("Weaviate connection closed")