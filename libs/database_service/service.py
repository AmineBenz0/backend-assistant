#!/usr/bin/env python3
"""
Database Service for GraphRAG Pipeline
"""
import logging

logger = logging.getLogger(__name__)

class DatabaseService:
    """Database service with real storage manager and Neo4j provider"""
    
    def __init__(self):
        self.connected = False
        self.initialized = False
        # Initialize real Neo4j provider
        from .graph_db.providers import Neo4jProvider
        from .models import GraphIndexConfig
        import os
        
        # Create Neo4j configuration
        neo4j_config = GraphIndexConfig(
            name="kotaemon_graph",
            graph_db_type="neo4j",
            description="Kotaemon graph database",
            neo4j_uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            neo4j_user=os.getenv("NEO4J_USER", "neo4j"),
            neo4j_password=os.getenv("NEO4J_PASSWORD", "password"),
            database_name=os.getenv("NEO4J_DATABASE", "neo4j"),
            enable_constraints=True,
            enable_indexes=True
        )
        
        self.graph_manager = Neo4jProvider(neo4j_config)
        # Initialize real storage manager
        from .storage import MinIOStorageManager
        import os
        self.storage_manager = MinIOStorageManager(
            endpoint=os.getenv("MINIO_ENDPOINT", "localhost:9000"),
            access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
            secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin"),
            secure=os.getenv("MINIO_SECURE", "false").lower() == "true"
        )
        
        # Initialize vector database service
        from .vector_db import VectorDatabaseService
        self.vector_manager = VectorDatabaseService()
    
    async def initialize(self):
        """Initialize the database service"""
        try:
            # Initialize the storage manager
            await self.storage_manager.initialize()
            
            # Initialize the vector database service
            vector_init_success = await self.vector_manager.initialize()
            
            if not vector_init_success:
                logger.warning("Vector database service initialization failed, but continuing...")
            
            self.initialized = True
            return True
        except Exception as e:
            logger.error(f"Failed to initialize database service: {e}")
            import traceback
            self.initialized = False
            return False
    
    async def store_preprocessing_output(self, job_id: str, output_type: str, data: dict, metadata: dict):
        """Store preprocessing output using storage manager"""
        if not self.storage_manager:
            raise RuntimeError("Storage manager not initialized")
        return await self.storage_manager.store_preprocessing_output(job_id, output_type, data, metadata)
    
    async def create_vector_index(self, config) -> dict:
        """Create a vector index (mock implementation)"""
        # Mock implementation for vector index creation
        # Handle both dict and Pydantic model formats
        try:
            # Try dictionary access first
            index_name = config.get("index_name", "default_index")
            dimension = config.get("dimension", 1536)
            metric = config.get("metric", "cosine")
        except AttributeError:
            # Pydantic model - use getattr
            index_name = getattr(config, 'index_name', 'default_index')
            dimension = getattr(config, 'dimension', 1536)
            metric = getattr(config, 'metric', 'cosine')
        
        return {
            "status": "success",
            "index_name": index_name,
            "dimension": dimension,
            "metric": metric,
            "message": "Mock vector index created successfully"
        }
    
    async def create_graph_index(self, config) -> dict:
        """Create a graph index (mock implementation)"""
        # Mock implementation for graph index creation
        # Handle both dict and Pydantic model formats
        try:
            # Try dictionary access first
            index_name = config.get("name", "default_graph_index")
            graph_db_type = config.get("graph_db_type", "neo4j")
            database_name = config.get("database_name", "neo4j")
        except AttributeError:
            # Pydantic model - use getattr
            index_name = getattr(config, 'name', 'default_graph_index')
            graph_db_type = getattr(config, 'graph_db_type', 'neo4j')
            database_name = getattr(config, 'database_name', 'neo4j')
        
        return {
            "status": "success",
            "index_name": index_name,
            "graph_db_type": graph_db_type,
            "database_name": database_name,
            "message": "Mock graph index created successfully"
        }
    
    async def add_documents(self, index_id: str, documents: list) -> dict:
        """Add documents to vector index (mock implementation)"""
        return {
            "status": "success",
            "index_id": index_id,
            "documents_added": len(documents),
            "message": f"Mock: Added {len(documents)} documents to index {index_id}"
        }
    
    async def add_nodes(self, index_id: str, nodes: list) -> dict:
        """Add nodes to graph index using Neo4j provider"""
        try:
            # Initialize Neo4j provider if not already done
            if not self.graph_manager._initialized:
                await self.graph_manager.initialize()
                await self.graph_manager.create_index()
            
            # Add nodes using Neo4j provider
            node_ids = await self.graph_manager.add_nodes(nodes)
            
            return {
                "status": "success",
                "index_id": index_id,
                "nodes_added": len(node_ids),
                "node_ids": node_ids,
                "message": f"Added {len(node_ids)} nodes to Neo4j graph index {index_id}"
            }
        except Exception as e:
            logger.error(f"Failed to add nodes to Neo4j: {e}")
            return {
                "status": "error",
                "index_id": index_id,
                "nodes_added": 0,
                "error": str(e),
                "message": f"Failed to add nodes to Neo4j: {e}"
            }
    
    async def add_relationships(self, index_id: str, relationships: list) -> dict:
        """Add relationships to graph index using Neo4j provider"""
        try:
            # Initialize Neo4j provider if not already done
            if not self.graph_manager._initialized:
                await self.graph_manager.initialize()
                await self.graph_manager.create_index()
            
            # Add relationships using Neo4j provider
            relationship_ids = await self.graph_manager.add_relationships(relationships)
            
            return {
                "status": "success",
                "index_id": index_id,
                "relationships_added": len(relationship_ids),
                "relationship_ids": relationship_ids,
                "message": f"Added {len(relationship_ids)} relationships to Neo4j graph index {index_id}"
            }
        except Exception as e:
            logger.error(f"Failed to add relationships to Neo4j: {e}")
            return {
                "status": "error",
                "index_id": index_id,
                "relationships_added": 0,
                "error": str(e),
                "message": f"Failed to add relationships to Neo4j: {e}"
            }
    #########################################################
    # Upload function Added
    #########################################################
    async def upload_file(
        self,
        file_data: bytes,
        filename: str,
        client_id: str,
        project_id: str,
        content_type: str = None
    ) -> str:
        """Upload file to object storage using storage manager"""
        if not self.storage_manager:
            raise RuntimeError("Storage manager not initialized")
        
        return await self.storage_manager.upload_file_with_structure(
            file_data=file_data,
            filename=filename,
            client_id=client_id,
            project_id=project_id,
            content_type=content_type
        )
    
    async def store_chunks(self, chunks, client_id: str, project_id: str):
        """Store chunks in vector database using vector manager"""
        if not self.vector_manager:
            raise RuntimeError("Vector manager not initialized")
        return await self.vector_manager.store_chunks(chunks, client_id, project_id)
    
    async def search_chunks(self, query: str, client_id: str, project_id: str, top_k: int = 5):
        """Search chunks in vector database using vector manager"""
        if not self.vector_manager:
            raise RuntimeError("Vector manager not initialized")
        return await self.vector_manager.similarity_search(query, client_id, project_id, top_k)
    
    async def close(self):
        """Close database connections"""
        if hasattr(self.storage_manager, 'close'):
            await self.storage_manager.close()
        if hasattr(self.vector_manager, 'close'):
            await self.vector_manager.close()
        self.connected = False