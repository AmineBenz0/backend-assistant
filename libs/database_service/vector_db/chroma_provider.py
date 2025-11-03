import os
import logging
import asyncio
from typing import List, Dict, Any, Optional
from .base import BaseVectorProvider

logger = logging.getLogger(__name__)

class ChromaVectorProvider(BaseVectorProvider):
    """ChromaDB implementation of VectorDBProvider."""

    def __init__(self, url: Optional[str] = None, collection_name: Optional[str] = None, **kwargs: Any):
        from ..models import VectorIndexConfig
        
        # Create a simple config for ChromaDB
        config = VectorIndexConfig(
            name=collection_name or os.getenv("CHROMA_COLLECTION_NAME", "documents"),
            vector_db_type="chroma",
            description="ChromaDB vector database",
            chroma_host=os.getenv("CHROMA_HOST", "localhost"),
            chroma_port=int(os.getenv("CHROMA_PORT", "8000"))
        )
        super().__init__(config)
        
        self.host = config.chroma_host
        self.port = config.chroma_port
        self.base_collection_name = config.name
        self.client = None

    async def initialize(self) -> bool:
        """Initialize the ChromaDB client"""
        try:
            logger.info(f"Initializing ChromaDB client with host: {self.host}, port: {self.port}")
            
            # Use asyncio to run the synchronous ChromaDB operations in a thread pool
            # This follows the same pattern as Neo4j and Weaviate providers
            import asyncio
            
            def _create_client():
                import chromadb
                from chromadb.config import Settings
                
                return chromadb.HttpClient(
                    host=self.host,
                    port=self.port,
                    settings=Settings(allow_reset=True)
                )
            
            def _test_connection(client):
                """Test ChromaDB connection"""
                try:
                    # Test connection by listing collections
                    collections = client.list_collections()
                    logger.info(f"ChromaDB connection successful, found {len(collections)} collections")
                    return True
                except Exception as e:
                    logger.warning(f"ChromaDB connection test failed: {e}")
                    return False
            
            # Run client creation in thread pool (following Neo4j pattern)
            loop = asyncio.get_event_loop()
            self.client = await loop.run_in_executor(None, _create_client)
            logger.info("ChromaDB client created, testing connection...")
            
            # Test connection in thread pool
            connection_success = await loop.run_in_executor(None, _test_connection, self.client)
            
            if connection_success:
                logger.info("ChromaDB is ready, initialization successful")
                self._initialized = True
                logger.info(f"ChromaDB provider initialized with base collection: {self.base_collection_name}")
                return True
            else:
                raise RuntimeError("ChromaDB is not ready after connection test.")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            self._initialized = False
            return False

    def _get_collection_name(self, client_id: str) -> str:
        """Get the collection name for a specific client.
        
        Note: client_id parameter is kept for backward compatibility but not used.
        The collection name is set directly by VectorDatabaseService in base_collection_name
        with the format: chunks_{client_id}_{project_id}
        """
        return self.base_collection_name

    def _ensure_collection(self, client_id: str):
        """Ensure the collection exists for a specific client."""
        try:
            collection_name = self._get_collection_name(client_id)
            
            # Check if collection exists
            collections = self.client.list_collections()
            existing_collection = next((c for c in collections if c.name == collection_name), None)
            
            if existing_collection:
                logger.info(f"ChromaDB collection '{collection_name}' already exists")
                return existing_collection
            
            # Create collection if it doesn't exist
            collection = self.client.create_collection(
                name=collection_name,
                metadata={"client_id": client_id}
            )
            logger.info(f"Created ChromaDB collection: {collection_name}")
            return collection
            
        except Exception as e:
            # If collection creation fails due to existing collection, log and continue
            if "already exists" in str(e):
                logger.info(f"ChromaDB collection '{collection_name}' already exists (handled gracefully)")
                return self.client.get_collection(collection_name)
            raise RuntimeError(f"Failed to ensure ChromaDB collection: {e}") from e

    async def store_chunks(self, chunks: List[Dict[str, Any]], client_id: str, project_id: str) -> Dict[str, Any]:
        """Store document chunks with embeddings, scoped to client_id and project_id."""
        try:
            if not self._initialized or not self.client:
                raise RuntimeError("ChromaDB client not initialized")
            
            # Ensure collection exists for this client
            collection = self._ensure_collection(client_id)
            
            # Use asyncio to run the synchronous ChromaDB operations in a thread pool
            import asyncio
            
            def _store_chunks_sync():
                successful_ids = []
                failed_count = 0
                attempted_count = 0
                
                logger.info(f"Storing {len(chunks)} chunks in ChromaDB collection: {collection.name}")
                
                # Prepare data for ChromaDB
                documents = []
                embeddings = []
                metadatas = []
                ids = []
                
                for i, chunk in enumerate(chunks):
                    attempted_count += 1
                    try:
                        # Derive object_name from chunk metadata if not present at root
                        object_name = (
                            chunk.get("object_name")
                            or chunk.get("metadata", {}).get("source_document", {}).get("object_name", "")
                        )

                        # Get chunk index from metadata
                        chunk_index = chunk.get("metadata", {}).get("chunk_index")
                        try:
                            chunk_id_value = int(chunk_index) if chunk_index is not None else i
                        except (TypeError, ValueError):
                            chunk_id_value = i

                        # Prepare document data
                        documents.append(chunk["text"])
                        embeddings.append(chunk.get("embedding", []))  # Assume embedding is pre-computed
                        metadatas.append({
                            "client_id": client_id,
                            "project_id": project_id,
                            "object_name": object_name,
                            "chunk_id": chunk_id_value,
                        })
                        ids.append(f"{client_id}_{project_id}_{chunk_id_value}")
                        
                    except Exception as e:
                        logger.warning(f"Failed to prepare chunk {i}: {e}")
                        failed_count += 1
                
                # Add documents to collection
                if documents:
                    collection.add(
                        documents=documents,
                        embeddings=embeddings,
                        metadatas=metadatas,
                        ids=ids
                    )
                    successful_ids = ids
                
                stored_count = len(successful_ids)
                logger.info(f"Successfully stored {stored_count} chunks in ChromaDB")
                
                return {
                    "stored_chunks": stored_count,
                    "stored_count": stored_count,
                    "failed_count": failed_count,
                    "successful_uuids": successful_ids
                }
            
            # Run the synchronous operation in a thread pool
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, _store_chunks_sync)
        
        except Exception as e:
            logger.error(f"Failed to store chunks in ChromaDB: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise RuntimeError(f"Failed to store chunks in ChromaDB: {e}") from e

    async def similarity_search(self, query: str, client_id: str, project_id: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Perform similarity search scoped to client_id and project_id."""
        try:
            if not self._initialized or not self.client:
                raise RuntimeError("ChromaDB client not initialized")
            
            # Use asyncio to run the synchronous ChromaDB operations in a thread pool
            import asyncio
            
            def _search_sync():
                collection_name = self._get_collection_name(client_id)
                collection = self.client.get_collection(collection_name)
                
                # Perform similarity search
                results = collection.query(
                    query_texts=[query],
                    n_results=top_k,
                    where={"project_id": project_id}  # Filter by project_id
                )
                
                # Convert results to expected format
                documents = []
                if results['documents'] and results['documents'][0]:
                    for i, doc in enumerate(results['documents'][0]):
                        metadata = results['metadatas'][0][i] if results['metadatas'] and results['metadatas'][0] else {}
                        documents.append({
                            "text": doc,
                            **metadata
                        })
                
                return documents
            
            # Run the synchronous operation in a thread pool
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, _search_sync)
        
        except Exception as e:
            raise RuntimeError(f"Failed to perform similarity search in ChromaDB: {e}") from e

    async def similarity_search_with_custom_embeddings(
        self, 
        query_text: str,
        client_id: str, 
        project_id: str, 
        embedding_model: str = "text-embedding-3-large",
        embedding_provider: str = "azure_openai",
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Perform similarity search using custom embedding model for query text"""
        try:
            if not self._initialized or not self.client:
                raise RuntimeError("ChromaDB client not initialized")
            
            # Generate embedding for the query text using the custom model
            from libs.embeddings_service import EmbeddingGeneratorInterface
            
            embedding_service = EmbeddingGeneratorInterface(default_provider=embedding_provider)
            
            async def generate_query_embedding():
                return await embedding_service.generate_batch_embeddings(
                    texts=[query_text],
                    provider=embedding_provider,
                    model_name=embedding_model
                )
            
            query_embeddings = await generate_query_embedding()
            query_embedding = query_embeddings[0] if query_embeddings else None
            
            if not query_embedding:
                raise RuntimeError("Failed to generate embedding for query text")
            
            def _search_sync():
                collection_name = self._get_collection_name(client_id)
                collection = self.client.get_collection(collection_name)
                
                # Use query_embeddings with the generated embedding
                results = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=top_k,
                    where={"project_id": project_id}
                )
                
                # Format results with similarity scores
                documents = []
                if results['documents'] and results['documents'][0]:
                    for i, doc in enumerate(results['documents'][0]):
                        metadata = results['metadatas'][0][i] if results['metadatas'] and results['metadatas'][0] else {}
                        distance = results['distances'][0][i] if results.get('distances') and results['distances'][0] else 0.0
                        documents.append({
                            "text": doc,
                            "similarity": 1.0 - distance,  # Convert distance to similarity
                            **metadata
                        })
                
                return documents
            
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, _search_sync)
        
        except Exception as e:
            raise RuntimeError(f"Failed to perform similarity search with custom embeddings: {e}") from e

    def delete_chunks(self, client_id: str, project_id: str, object_name: str) -> Dict[str, Any]:
        """Delete chunks associated with a document in a client's project."""
        try:
            collection_name = self._get_collection_name(client_id)
            collection = self.client.get_collection(collection_name)
            
            # Delete chunks by metadata filter
            collection.delete(
                where={
                    "project_id": project_id,
                    "object_name": object_name
                }
            )
            
            return {"deleted_count": 1, "failed_count": 0}
        
        except Exception as e:
            raise RuntimeError(f"Failed to delete chunks in ChromaDB: {e}") from e
    
    def delete_document_chunks(self, client_id: str, project_id: str, object_name: str) -> Dict[str, Any]:
        """Alias for delete_chunks for backward compatibility."""
        return self.delete_chunks(client_id, project_id, object_name)

    def name(self) -> str:
        return "chroma"
    
    def get_collection_stats(self, client_id: str) -> Dict[str, Any]:
        """Get collection statistics for a specific client."""
        try:
            collection_name = self._get_collection_name(client_id)
            collection = self.client.get_collection(collection_name)
            count = collection.count()
            return {
                "total_count": count,
                "collection_name": collection_name,
                "client_id": client_id
            }
        except Exception as e:
            raise RuntimeError(f"Failed to get collection stats: {e}") from e

    async def create_index(self) -> bool:
        """Create a new vector index"""
        return True  # ChromaDB creates collections automatically
    
    async def delete_index(self) -> bool:
        """Delete the vector index"""
        return True  # Not implemented for ChromaDB
    
    async def add_documents(self, documents: List[Any]) -> List[str]:
        """Add documents to the index"""
        return []  # Not implemented for ChromaDB
    
    async def update_documents(self, documents: List[Any]) -> bool:
        """Update existing documents"""
        return True  # Not implemented for ChromaDB
    
    async def delete_documents(self, document_ids: List[str]) -> bool:
        """Delete documents from the index"""
        return True  # Not implemented for ChromaDB
    
    async def get_document(self, document_id: str) -> Optional[Any]:
        """Retrieve a specific document"""
        return None  # Not implemented for ChromaDB
    
    async def get_index_stats(self) -> Dict[str, Any]:
        """Get index statistics"""
        return {"total_count": 0}
    
    async def health_check(self) -> Dict[str, Any]:
        """Check provider health"""
        return {"status": "healthy" if self._initialized else "unhealthy"}

    async def close(self) -> None:
        """Close the ChromaDB connection."""
        if hasattr(self, 'client') and self.client:
            # ChromaDB client doesn't need explicit closing
            logger.info("ChromaDB connection closed")
