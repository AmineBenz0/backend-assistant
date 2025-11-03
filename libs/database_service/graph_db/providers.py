"""
Graph database provider implementations
"""
import asyncio
from typing import List
import logging

from .base import BaseGraphProvider
from ..models import GraphIndexConfig, GraphNode, GraphRelationship

logger = logging.getLogger(__name__)


class Neo4jProvider(BaseGraphProvider):
    """Neo4j graph database provider"""
    
    def __init__(self, config: GraphIndexConfig):
        super().__init__(config)
        self._driver = None
        self._session = None
    
    async def initialize(self) -> bool:
        """Initialize Neo4j driver"""
        try:
            import neo4j
            from neo4j import GraphDatabase
            
            # Create driver
            self._driver = GraphDatabase.driver(
                self.config.neo4j_uri,
                auth=(self.config.neo4j_user, self.config.neo4j_password)
            )
            
            # Test connection
            await self._test_connection()
            
            self._initialized = True
            logger.info(f"Neo4j provider initialized for database: {self.config.database_name}")
            return True
            
        except ImportError:
            logger.error("Neo4j driver not installed. Install with: pip install neo4j")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize Neo4j provider: {str(e)}")
            return False
    
    async def _test_connection(self) -> bool:
        """Test Neo4j connection"""
        try:
            # Use asyncio to run the synchronous Neo4j operation
            def test_connection():
                with self._driver.session(database=self.config.database_name) as session:
                    result = session.run("RETURN 1 as test")
                    return result.single()["test"] == 1
            
            # Run in thread pool since Neo4j operations are blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, test_connection)
            
            return result
            
        except Exception as e:
            logger.error(f"Neo4j connection test failed: {str(e)}")
            return False
    
    async def create_index(self) -> bool:
        """Create Neo4j database and indexes"""
        if not self._initialized:
            await self.initialize()
        
        try:
            # Create constraints and indexes
            if self.config.enable_constraints:
                await self._create_constraints()
            
            if self.config.enable_indexes:
                await self._create_indexes()
            
            logger.info(f"Neo4j database setup completed: {self.config.database_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create Neo4j database: {str(e)}")
            return False
    
    async def _create_constraints(self) -> None:
        """Skip global constraint creation to avoid forcing a base label."""
        logger.info("Skipping constraint creation (no generic base label)")
    
    async def _create_indexes(self) -> None:
        """Skip global index creation to avoid introducing unwanted labels."""
        logger.info("Skipping index creation (no generic base label)")


    async def add_nodes(self, nodes: List[GraphNode]) -> List[str]:
        """Add nodes to Neo4j"""
        if not self._initialized:
            await self.create_index()
        
        try:
            def add_nodes():
                with self._driver.session(database=self.config.database_name) as session:
                    node_ids = []
                    for node in nodes:
                        # Flatten properties for Neo4j compatibility with embedding support
                        flat_properties = {}
                        if node.properties:
                            logger.debug(f"Processing node {node.name} with properties: {list(node.properties.keys())}")
                            for key, value in node.properties.items():
                                # Convert property names to valid Neo4j format
                                prop_key = key.replace('-', '_').replace(' ', '_')
                                
                                # Debug logging for description_embedding
                                if key == "description_embedding":
                                    logger.info(f"Found description_embedding for {node.name}: type={type(value)}, size={len(value) if isinstance(value, list) else 'N/A'}")
                                
                                # Handle embedding arrays specially
                                if key in ["embedding", "description_embedding"] and isinstance(value, list):
                                    # Store embedding as a list property in Neo4j
                                    flat_properties[prop_key] = value
                                    logger.info(f"Stored {key} for {node.name}: {len(value)} dimensions")
                                elif isinstance(value, (str, int, float, bool)):
                                    # Store simple types directly
                                    flat_properties[prop_key] = value
                                elif isinstance(value, list) and all(isinstance(x, (int, float)) for x in value):
                                    # Store numeric arrays (like embeddings)
                                    flat_properties[prop_key] = value
                                    logger.debug(f"Stored numeric array {key} for {node.name}: {len(value)} elements")
                                else:
                                    # Convert complex types to string
                                    flat_properties[prop_key] = str(value)
                                    logger.debug(f"Converted {key} to string for {node.name}")
                            
                            logger.debug(f"Final flat_properties for {node.name}: {list(flat_properties.keys())}")
                        
                        # Create node labels string using only provided labels (no base label)
                        labels_str = ""
                        if node.labels:
                            for label in node.labels:
                                labels_str += f":{label}"
                        
                        # Build the node properties dynamically (exclude node_id from SET)
                        node_properties = {
                            'name': '$name',
                            'node_type': '$node_type',
                            'created_at': '$created_at'
                        }
                        
                        # Add flattened properties
                        if flat_properties:
                            for key, value in flat_properties.items():
                                node_properties[key] = f'${key}'
                        
                        # Convert properties to Cypher format
                        prop_pairs = []
                        for key, param in node_properties.items():
                            prop_pairs.append(f"{key}: {param}")
                        
                        # Create the complete query using MERGE to avoid duplicate nodes by node_id
                        query = f"""
                        MERGE (n{labels_str} {{node_id: $node_id}})
                        SET n += {{{', '.join(prop_pairs)}}}
                        RETURN n.node_id as node_id
                        """
                        
                        # Debug: Log the generated query
                        logger.debug(f"Generated Cypher query: {query}")
                        
                        # Prepare parameters
                        params = {
                            'node_id': node.node_id,
                            'name': node.name,
                            'node_type': node.node_type,
                            'created_at': node.created_at.isoformat()
                        }
                        # Add flattened properties to parameters
                        params.update(flat_properties)
                        
                        # Debug: Log parameters being sent to Neo4j
                        if 'description_embedding' in params:
                            logger.info(f"Sending description_embedding to Neo4j for {node.name}: {len(params['description_embedding'])} dimensions")
                        else:
                            logger.warning(f"No description_embedding in params for {node.name}. Available params: {list(params.keys())}")
                        
                        logger.debug(f"All parameters for {node.name}: {list(params.keys())}")
                        
                        result = session.run(query, params)
                        node_ids.append(result.single()["node_id"])
                    
                    return node_ids
            
            loop = asyncio.get_event_loop()
            node_ids = await loop.run_in_executor(None, add_nodes)
            
            logger.info(f"Added {len(nodes)} nodes to Neo4j")
            return node_ids
            
        except Exception as e:
            logger.error(f"Failed to add nodes to Neo4j: {str(e)}")
            return []
    
    async def add_relationships(self, relationships: List[GraphRelationship]) -> List[str]:
        """Add relationships to Neo4j"""
        if not self._initialized:
            await self.create_index()
        
        try:
            def add_relationships():
                with self._driver.session(database=self.config.database_name) as session:
                    relationship_ids = []
                    for rel in relationships:
                        # Debug: Log the relationship object first
                        logger.debug(f"Processing relationship: {rel}")
                        logger.debug(f"rel.source_node_id: {rel.source_node_id}")
                        logger.debug(f"rel.target_node_id: {rel.target_node_id}")
                        logger.debug(f"rel.relationship_id: {rel.relationship_id}")
                        logger.debug(f"rel.relationship_type: {rel.relationship_type}")
                        logger.debug(f"rel.weight: {rel.weight}")
                        logger.debug(f"rel.bidirectional: {rel.bidirectional}")
                        logger.debug(f"rel.created_at: {rel.created_at}")
                        
                        # Flatten properties for Neo4j compatibility
                        flat_properties = {}
                        if rel.properties:
                            for key, value in rel.properties.items():
                                # Convert property names to valid Neo4j format
                                prop_key = key.replace('-', '_').replace(' ', '_')
                                flat_properties[prop_key] = value
                        
                        # Build the relationship properties dynamically
                        rel_properties = {
                            'relationship_id': '$relationship_id',
                            'relationship_type': '$relationship_type',
                            'weight': '$weight',
                            'bidirectional': '$bidirectional',
                            'created_at': '$created_at'
                        }
                        
                        # Add flattened properties
                        if flat_properties:
                            for key, value in flat_properties.items():
                                rel_properties[key] = f'${key}'
                        
                        # Convert properties to Cypher format
                        prop_pairs = []
                        for key, param in rel_properties.items():
                            prop_pairs.append(f"{key}: {param}")
                        
                        # Create the complete query with dynamic relationship type label
                        rel_type_label = (rel.relationship_type or "RELATED_TO").upper()
                        import re as _re
                        rel_type_label = _re.sub(r"[^A-Z0-9_]", "_", rel_type_label)
                        
                        # Enhanced query that creates missing nodes automatically
                        query = f"""
                        MERGE (source {{node_id: $source_id}})
                        ON CREATE SET source.name = $source_entity, source.node_type = 'ENTITY', source.created_at = $created_at, source.source = 'auto_created'
                        MERGE (target {{node_id: $target_id}})
                        ON CREATE SET target.name = $target_entity, target.node_type = 'ENTITY', target.created_at = $created_at, target.source = 'auto_created'
                        MERGE (source)-[r:{rel_type_label}]->(target)
                        SET r += {{{', '.join(prop_pairs)}}}
                        RETURN COALESCE(r.relationship_id, $relationship_id) as relationship_id
                        """
                        
                        # Debug: Log the generated query
                        logger.debug(f"Generated Cypher query: {query}")
                        logger.debug(f"Relationship object: {rel}")
                        logger.debug(f"rel.created_at: {rel.created_at}, type: {type(rel.created_at)}")
                        
                        # Prepare parameters
                        params = {
                            'source_id': rel.source_node_id,
                            'target_id': rel.target_node_id,
                            'source_entity': flat_properties.get('source_entity', rel.source_node_id),
                            'target_entity': flat_properties.get('target_entity', rel.target_node_id),
                            'relationship_id': rel.relationship_id,
                            'relationship_type': rel.relationship_type,
                            'weight': rel.weight,
                            'bidirectional': rel.bidirectional,
                            'created_at': rel.created_at.isoformat()
                        }
                        # Add flattened properties to parameters
                        params.update(flat_properties)
                        
                        result = session.run(query, params)
                        record = result.single()
                        if record is None:
                            logger.error(f"Query returned no results for relationship: {rel.source_node_id} -> {rel.target_node_id}")
                            logger.error(f"Query: {query}")
                            logger.error(f"Params: {params}")
                            continue
                        
                        relationship_id = record.get("relationship_id")
                        if relationship_id is None:
                            logger.error(f"relationship_id is None for relationship: {rel.source_node_id} -> {rel.target_node_id}")
                            logger.error(f"Record: {dict(record)}")
                            continue
                            
                        relationship_ids.append(relationship_id)
                    
                    return relationship_ids
            
            loop = asyncio.get_event_loop()
            relationship_ids = await loop.run_in_executor(None, add_relationships)
            
            logger.info(f"Added {len(relationships)} relationships to Neo4j")
            return relationship_ids
            
        except Exception as e:
            logger.error(f"Failed to add relationships to Neo4j: {str(e)}")
            return []



    async def run_query(self, query: str, params: dict | None = None):
        if not self._initialized:
            await self.initialize()

        def _run():
            with self._driver.session(database=self.config.database_name) as session:
                return [record.data() for record in session.run(query, params or {})]

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _run)