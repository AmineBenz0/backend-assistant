import os
import time
import logging
from datetime import datetime
from elasticsearch import Elasticsearch, NotFoundError
from elasticsearch.helpers import bulk
from typing import Dict, Any, Optional, List, Tuple, Union
from .base import BaseDocProvider

logger = logging.getLogger(__name__)

class ElasticsearchDocProvider(BaseDocProvider):
    """Elasticsearch implementation of DocDBProvider."""

    def __init__(self, url: Optional[str] = None, username: Optional[str] = None, 
                 password: Optional[str] = None, **kwargs: Any):
        config = {
            "url": url or os.getenv("ELASTICSEARCH_URL", "http://localhost:9200"),
            "username": username or os.getenv("ELASTICSEARCH_USERNAME"),
            "password": password or os.getenv("ELASTICSEARCH_PASSWORD"),
            "provider_type": "elasticsearch"
        }
        super().__init__(config)
        
        self.url = config["url"]
        self.username = config["username"]
        self.password = config["password"]
        self.client = None
        logger.info("Elasticsearch provider initialized (client will be created when needed).")

    async def initialize(self) -> bool:
        """Initialize the Elasticsearch client"""
        try:
            self._ensure_client()
            self._initialized = True
            logger.info("Elasticsearch provider initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Elasticsearch provider: {e}")
            return False

    def _ensure_client(self):
        """Ensure the Elasticsearch client is initialized."""
        if self.client is None:
            try:
                auth = (self.username, self.password) if self.username and self.password else None
                self.client = Elasticsearch(
                    self.url,
                    basic_auth=auth,
                    verify_certs=False  # Adjust based on your security needs
                )
                
                if not self.client.ping():
                    raise RuntimeError("Elasticsearch is not reachable.")
                
                logger.debug("Elasticsearch client created successfully.")
            except Exception as e:
                raise RuntimeError(f"Failed to initialize Elasticsearch: {e}") from e

    async def save(self, index: str, doc_id: str, data: Dict[str, Any], client_id: Optional[str] = None, project_id: Optional[str] = None) -> bool:
        """Save or update a document."""
        try:
            self._ensure_client()
            # Add client_id to data if provided
            if client_id:
                data["client_id"] = client_id
            if project_id:
                data["project_id"] = project_id
            self.client.index(index=index, id=doc_id, body=data)
            self.client.indices.refresh(index=index)
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to save document in Elasticsearch: {e}") from e

    async def load(self, index: str, doc_id: str, client_id: Optional[str] = None, project_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Load a document by ID."""
        try:
            self._ensure_client()
            resp = self.client.get(index=index, id=doc_id)
            return resp["_source"]
        except NotFoundError:
            return None
        except Exception as e:
            raise RuntimeError(f"Failed to load document from Elasticsearch: {e}") from e

    async def search(self, index: str, query: Dict[str, Any], size: int = 10, client_id: Optional[str] = None, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Perform a search query."""
        try:
            self._ensure_client()
            # Add client_id filter if provided
            if client_id or project_id:
                if "query" not in query:
                    query["query"] = {}
                if "bool" not in query["query"]:
                    query["query"]["bool"] = {"must": []}
                if "must" not in query["query"]["bool"]:
                    query["query"]["bool"]["must"] = []

                if client_id:
                    query["query"]["bool"]["must"].append({
                        "term": {"client_id": client_id}
                    })
                if project_id:
                    query["query"]["bool"]["must"].append({
                        "term": {"project_id": project_id}
                    })
            
            resp = self.client.search(index=index, body=query, size=size)
            return [hit["_source"] for hit in resp["hits"]["hits"]]
        except Exception as e:
            raise RuntimeError(f"Failed to search in Elasticsearch: {e}") from e

    async def delete(self, index: str, doc_id: str, client_id: Optional[str] = None) -> bool:
        """Delete a document."""
        try:
            self._ensure_client()
            self.client.delete(index=index, id=doc_id)
            self.client.indices.refresh(index=index)
            return True
        except NotFoundError:
            return False
        except Exception as e:
            raise RuntimeError(f"Failed to delete document in Elasticsearch: {e}") from e

    async def create_document_to_chunks_mapping(self, index_name: str, document_id: str, 
                                        storage_object_name: str, vector_chunk_ids: List[str], 
                                        metadata: Dict[str, Any], client_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a mapping document that links a storage object to its vector chunks.
        
        Args:
            index_name: Name of the index to store the mapping
            document_id: Unique identifier for the mapping document
            storage_object_name: Name/key of the object in storage
            vector_chunk_ids: List of vector chunk UUIDs
            metadata: Additional metadata about the document
            
        Returns:
            Response from Elasticsearch with document ID
        """
        try:
            self._ensure_client()
            
            # Create the mapping document
            # Convert timestamp to ISO format for Elasticsearch date field
            upload_timestamp = metadata.get("upload_timestamp", time.time())
            if isinstance(upload_timestamp, (int, float)):
                created_at_iso = datetime.fromtimestamp(upload_timestamp).isoformat()
            else:
                # If it's already a datetime or ISO string, use as is
                created_at_iso = upload_timestamp
            
            mapping_doc = {
                "storage_object_name": storage_object_name,
                "vector_chunk_ids": vector_chunk_ids,
                "created_at": created_at_iso,
                **metadata
            }
            
            # Add client_id if provided
            if client_id:
                mapping_doc["client_id"] = client_id
            
            # Save the mapping document
            response = self.client.index(
                index=index_name,
                id=document_id,
                body=mapping_doc
            )
            
            # Refresh the index to make the document searchable
            self.client.indices.refresh(index=index_name)
            
            logger.info(f"Created document-to-chunks mapping in {index_name}: {document_id}")
            return {"_id": response["_id"], "result": response["result"]}
            
        except Exception as e:
            logger.error(f"Failed to create document-to-chunks mapping: {e}")
            raise RuntimeError(f"Failed to create document-to-chunks mapping: {e}") from e

    async def delete_document_mapping(self, index_name: str, document_id: str, client_id: Optional[str] = None) -> bool:
        """Delete a document mapping from Elasticsearch."""
        try:
            self._ensure_client()
            self.client.delete(index=index_name, id=document_id)
            self.client.indices.refresh(index=index_name)
            logger.info(f"Deleted document mapping {document_id} from index {index_name}")
            return True
        except NotFoundError:
            logger.warning(f"Document mapping {document_id} not found in index {index_name}")
            return False
        except Exception as e:
            logger.error(f"Failed to delete document mapping: {e}")
            return False

    async def save_chunk_embedding_mapping_to_document_db(
        self,
        index_name: str,
        file_name: str,
        chunks: List[Union[Tuple[str, Any], Dict[str, Any]]],
        client_id: Optional[str] = None,
        project_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Save chunk embeddings for a single file to Elasticsearch in bulk.

        Input (per call):
            file_name: "file_name.ext"
            chunks: [("chunk_id_1", embedding_vector_1), ("chunk_id_2", embedding_vector_2), ...]
                    or [{"chunk_id": "...", "embedding": [...]}, ...]

        Each (file_name, chunk_id) pair is stored as a separate document with fields:
            file_name, chunk_id, embedding, created_at, [client_id], [project_id]
        """
        try:
            self._ensure_client()

            created_at_iso = datetime.fromtimestamp(time.time()).isoformat()

            actions: List[Dict[str, Any]] = []

            if not chunks:
                return {"indexed": 0, "errors": []}

            for item in chunks:
                # Support (chunk_id, embedding) tuples or dicts {chunk_id, embedding}
                if isinstance(item, (list, tuple)) and len(item) == 2:
                    chunk_id, embedding = item  # type: ignore[assignment]
                elif isinstance(item, dict):
                    chunk_id = item.get("chunk_id")
                    embedding = item.get("embedding")
                else:
                    raise ValueError("Chunks must be tuples (chunk_id, embedding) or dicts with those keys.")

                if chunk_id is None or embedding is None:
                    raise ValueError("chunk_id and embedding must be provided for each chunk.")

                doc: Dict[str, Any] = {
                    "file_name": file_name,
                    "chunk_id": chunk_id,
                    "embedding": embedding,
                    "created_at": created_at_iso,
                }

                if client_id:
                    doc["client_id"] = client_id
                if project_id:
                    doc["project_id"] = project_id

                actions.append({
                    "_op_type": "index",
                    "_index": index_name,
                    "_id": f"{file_name}:{chunk_id}",
                    "_source": doc,
                })

            if not actions:
                return {"indexed": 0, "errors": []}

            success_count, errors = bulk(self.client, actions, refresh=True)

            # success_count equals number of actions processed; errors is a list of failures
            if errors:
                logger.error(f"Bulk indexing completed with errors: {errors[:3]} ...")

            return {"indexed": success_count, "errors": errors}

        except Exception as e:
            raise RuntimeError(f"Failed to save chunk embeddings in Elasticsearch: {e}") from e

    async def close(self) -> None:
        """Close the Elasticsearch connection."""
        if hasattr(self, 'client') and self.client:
            self.client.close()
            logger.info("Elasticsearch connection closed")
