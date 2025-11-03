#!/usr/bin/env python3
"""
Database Cleanup Script for Kotaemon Backend
============================================

This script cleans all databases used by the Kotaemon backend:
- Neo4j (Graph database)
- ChromaDB (Vector database)
- Qdrant (Vector database)
- Weaviate (Vector database)
- MinIO (Object storage)

Usage:
    python cleanup_databases.py [--confirm] [--verbose]
"""

import asyncio
import argparse
import logging
import sys
import os
from pathlib import Path
from typing import Dict, Any, List
import time

# Load environment variables
from dotenv import load_dotenv

# Get the directory where this script is located (now in tests/)
script_dir = Path(__file__).parent
backend_dir = script_dir.parent  # Parent is the backend directory
env_path = backend_dir / "local_dev.env"
if not env_path.exists():
    env_path = backend_dir / "local.env"
load_dotenv(env_path)

# Add libs to path
sys.path.insert(0, str(backend_dir / "libs"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatabaseCleaner:
    """Comprehensive database cleanup utility"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.cleanup_results = {}
        
        if verbose:
            logging.getLogger().setLevel(logging.DEBUG)
    
    async def cleanup_neo4j(self) -> Dict[str, Any]:
        """Clean Neo4j graph database"""
        logger.info("🗑️ Cleaning Neo4j database...")
        
        try:
            from neo4j import GraphDatabase
            
            # Neo4j connection parameters
            uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
            username = os.getenv("NEO4J_USERNAME", "neo4j")
            password = os.getenv("NEO4J_PASSWORD", "password")
            
            logger.info(f"Connecting to Neo4j at {uri}")
            
            with GraphDatabase.driver(uri, auth=(username, password)) as driver:
                with driver.session() as session:
                    # Get count before cleanup
                    result = session.run("MATCH (n) RETURN count(n) as node_count")
                    node_count_before = result.single()["node_count"]
                    
                    result = session.run("MATCH ()-[r]->() RETURN count(r) as rel_count")
                    rel_count_before = result.single()["rel_count"]
                    
                    logger.info(f"Found {node_count_before} nodes and {rel_count_before} relationships")
                    
                    # Step 1: Drop all constraints first (they might prevent deletion)
                    logger.info("Dropping all constraints...")
                    try:
                        constraints = session.run("SHOW CONSTRAINTS").data()
                        for constraint in constraints:
                            if constraint.get("name"):
                                try:
                                    session.run(f"DROP CONSTRAINT {constraint['name']} IF EXISTS")
                                    logger.debug(f"Dropped constraint: {constraint['name']}")
                                except Exception as e:
                                    logger.warning(f"Could not drop constraint {constraint['name']}: {e}")
                    except Exception as e:
                        logger.warning(f"Could not list/drop constraints: {e}")
                    
                    # Step 2: Drop all indexes (they might prevent deletion)
                    logger.info("Dropping all indexes...")
                    try:
                        indexes = session.run("SHOW INDEXES").data()
                        for index in indexes:
                            if index.get("name") and not index.get("name").startswith("system"):
                                try:
                                    session.run(f"DROP INDEX {index['name']} IF EXISTS")
                                    logger.debug(f"Dropped index: {index['name']}")
                                except Exception as e:
                                    logger.warning(f"Could not drop index {index['name']}: {e}")
                    except Exception as e:
                        logger.warning(f"Could not list/drop indexes: {e}")
                    
                    # Step 3: Use DETACH DELETE to remove all nodes and relationships at once
                    logger.info("Performing DETACH DELETE on all nodes...")
                    session.run("MATCH (n) DETACH DELETE n")
                    
                    # Step 4: Verify and handle any remaining nodes with specific approaches
                    result = session.run("MATCH (n) RETURN count(n) as remaining_count")
                    remaining_count = result.single()["remaining_count"]
                    
                    if remaining_count > 0:
                        logger.warning(f"Found {remaining_count} remaining nodes, trying specific deletion approaches...")
                        
                        # Get all labels in the database
                        try:
                            labels_result = session.run("CALL db.labels()")
                            labels = [record["label"] for record in labels_result]
                            logger.info(f"Found labels: {labels}")
                            
                            # Delete nodes by each label
                            for label in labels:
                                try:
                                    result = session.run(f"MATCH (n:{label}) RETURN count(n) as count")
                                    count = result.single()["count"]
                                    if count > 0:
                                        logger.info(f"Deleting {count} nodes with label '{label}'...")
                                        session.run(f"MATCH (n:{label}) DETACH DELETE n")
                                except Exception as e:
                                    logger.warning(f"Could not delete nodes with label '{label}': {e}")
                        except Exception as e:
                            logger.warning(f"Could not get labels: {e}")
                        
                        # Final brute force cleanup
                        logger.info("Final cleanup attempt...")
                        session.run("MATCH (n) DETACH DELETE n")
                    
                    # Step 5: Final verification
                    result = session.run("MATCH (n) RETURN count(n) as node_count")
                    node_count_after = result.single()["node_count"]
                    
                    result = session.run("MATCH ()-[r]->() RETURN count(r) as rel_count")
                    rel_count_after = result.single()["rel_count"]
                    
                    # Check for any remaining labels
                    try:
                        labels_result = session.run("CALL db.labels()")
                        remaining_labels = [record["label"] for record in labels_result]
                        if remaining_labels:
                            logger.warning(f"Remaining labels after cleanup: {remaining_labels}")
                        else:
                            logger.info("No remaining labels - database is clean")
                    except Exception as e:
                        logger.warning(f"Could not check remaining labels: {e}")
                    
                    if node_count_after == 0 and rel_count_after == 0:
                        logger.info(f"[PASS] Neo4j cleanup completed successfully: {node_count_before} → {node_count_after} nodes, {rel_count_before} → {rel_count_after} relationships")
                    else:
                        logger.error(f"[FAIL] Neo4j cleanup incomplete: {node_count_after} nodes and {rel_count_after} relationships remain")
                    
                    return {
                        "status": "success" if node_count_after == 0 else "partial",
                        "nodes_deleted": node_count_before - node_count_after,
                        "relationships_deleted": rel_count_before - rel_count_after,
                        "final_nodes": node_count_after,
                        "final_relationships": rel_count_after
                    }
        
        except ImportError:
            logger.warning("[WARN] Neo4j driver not installed, skipping Neo4j cleanup")
            return {"status": "skipped", "reason": "neo4j driver not installed"}
        except Exception as e:
            logger.error(f"[FAIL] Neo4j cleanup failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def cleanup_chromadb(self) -> Dict[str, Any]:
        """Clean ChromaDB vector database"""
        logger.info("🗑️ Cleaning ChromaDB database...")
        
        try:
            import chromadb
            from chromadb.config import Settings
            
            # ChromaDB connection
            host = os.getenv("CHROMADB_HOST", "localhost")
            port = int(os.getenv("CHROMADB_PORT", "8001"))
            
            logger.info(f"Connecting to ChromaDB at {host}:{port}")
            
            client = chromadb.HttpClient(
                host=host,
                port=port,
                settings=Settings(allow_reset=True)
            )
            
            # Get collections before cleanup
            collections_before = client.list_collections()
            collection_count_before = len(collections_before)
            
            logger.info(f"Found {collection_count_before} collections")
            
            # Delete all collections
            total_documents = 0
            for collection in collections_before:
                try:
                    coll = client.get_collection(collection.name)
                    doc_count = coll.count()
                    total_documents += doc_count
                    logger.debug(f"Deleting collection '{collection.name}' with {doc_count} documents")
                    client.delete_collection(collection.name)
                except Exception as e:
                    logger.warning(f"Could not delete collection {collection.name}: {e}")
            
            # Verify cleanup
            collections_after = client.list_collections()
            collection_count_after = len(collections_after)
            
            # Attempt hard reset if supported and some collections remain
            if collection_count_after > 0:
                try:
                    client.reset()
                    collections_after = client.list_collections()
                    collection_count_after = len(collections_after)
                    logger.info("ChromaDB hard reset executed")
                except Exception as e:
                    logger.warning(f"ChromaDB hard reset not available/failed: {e}")
            
            logger.info(f"[PASS] ChromaDB cleanup completed: {collection_count_before} → {collection_count_after} collections, ~{total_documents} documents deleted")
            
            return {
                "status": "success",
                "collections_deleted": collection_count_before,
                "documents_deleted": total_documents,
                "final_collections": collection_count_after
            }
        
        except ImportError:
            logger.warning("[WARN] ChromaDB not installed, skipping ChromaDB cleanup")
            return {"status": "skipped", "reason": "chromadb not installed"}
        except Exception as e:
            logger.error(f"[FAIL] ChromaDB cleanup failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def cleanup_qdrant(self) -> Dict[str, Any]:
        """Clean Qdrant vector database"""
        logger.info("🗑️ Cleaning Qdrant database...")
        
        try:
            from qdrant_client import QdrantClient
            
            # Qdrant connection
            host = os.getenv("QDRANT_HOST", "localhost")
            port = int(os.getenv("QDRANT_PORT", "6333"))
            
            logger.info(f"Connecting to Qdrant at {host}:{port}")
            
            client = QdrantClient(host=host, port=port)
            
            # Get collections before cleanup
            collections_before = client.get_collections().collections
            collection_count_before = len(collections_before)
            
            logger.info(f"Found {collection_count_before} collections")
            
            # Delete all collections
            total_points = 0
            for collection in collections_before:
                try:
                    collection_info = client.get_collection(collection.name)
                    point_count = collection_info.points_count or 0
                    total_points += point_count
                    logger.debug(f"Deleting collection '{collection.name}' with {point_count} points")
                    client.delete_collection(collection.name)
                except Exception as e:
                    logger.warning(f"Could not delete collection {collection.name}: {e}")
            
            # Verify cleanup
            collections_after = client.get_collections().collections
            collection_count_after = len(collections_after)
            
            logger.info(f"[PASS] Qdrant cleanup completed: {collection_count_before} → {collection_count_after} collections, ~{total_points} points deleted")
            
            return {
                "status": "success",
                "collections_deleted": collection_count_before,
                "points_deleted": total_points,
                "final_collections": collection_count_after
            }
        
        except ImportError:
            logger.warning("[WARN] Qdrant client not installed, skipping Qdrant cleanup")
            return {"status": "skipped", "reason": "qdrant-client not installed"}
        except Exception as e:
            logger.error(f"[FAIL] Qdrant cleanup failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def cleanup_weaviate(self) -> Dict[str, Any]:
        """Clean Weaviate vector database"""
        logger.info("🗑️ Cleaning Weaviate database...")
        
        try:
            import weaviate
            
            # Weaviate connection
            host = os.getenv("WEAVIATE_HOST", "localhost")
            port = int(os.getenv("WEAVIATE_PORT", "8080"))
            url = f"http://{host}:{port}"
            
            logger.info(f"Connecting to Weaviate at {url}")
            
            client = weaviate.Client(url)
            
            # Get schema before cleanup
            schema = client.schema.get()
            classes_before = schema.get("classes", [])
            class_count_before = len(classes_before)
            
            logger.info(f"Found {class_count_before} classes")
            
            # Delete all classes (this deletes all data)
            total_objects = 0
            for class_obj in classes_before:
                class_name = class_obj["class"]
                try:
                    # Get object count (approximate)
                    result = client.query.aggregate(class_name).with_meta_count().do()
                    if result.get("data", {}).get("Aggregate", {}).get(class_name):
                        count_info = result["data"]["Aggregate"][class_name][0]
                        object_count = count_info.get("meta", {}).get("count", 0)
                        total_objects += object_count
                    
                    logger.debug(f"Deleting class '{class_name}' with ~{object_count} objects")
                    client.schema.delete_class(class_name)
                except Exception as e:
                    logger.warning(f"Could not delete class {class_name}: {e}")
            
            # Verify cleanup
            schema_after = client.schema.get()
            classes_after = schema_after.get("classes", [])
            class_count_after = len(classes_after)
            
            logger.info(f"[PASS] Weaviate cleanup completed: {class_count_before} → {class_count_after} classes, ~{total_objects} objects deleted")
            
            return {
                "status": "success",
                "classes_deleted": class_count_before,
                "objects_deleted": total_objects,
                "final_classes": class_count_after
            }
        
        except ImportError:
            logger.warning("[WARN] Weaviate client not installed, skipping Weaviate cleanup")
            return {"status": "skipped", "reason": "weaviate-client not installed"}
        except Exception as e:
            logger.error(f"[FAIL] Weaviate cleanup failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def cleanup_minio(self) -> Dict[str, Any]:
        """Clean MinIO object storage"""
        logger.info("🗑️ Cleaning MinIO storage...")
        
        try:
            from minio import Minio
            
            # MinIO connection
            endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9000")
            access_key = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
            secret_key = os.getenv("MINIO_SECRET_KEY", "minioadmin")
            secure = os.getenv("MINIO_SECURE", "false").lower() == "true"
            
            logger.info(f"Connecting to MinIO at {endpoint}")
            
            client = Minio(
                endpoint,
                access_key=access_key,
                secret_key=secret_key,
                secure=secure
            )
            
            # Get buckets before cleanup
            buckets_before = list(client.list_buckets())
            bucket_count_before = len(buckets_before)
            
            logger.info(f"Found {bucket_count_before} buckets")
            
            # Delete all objects in all buckets
            total_objects = 0
            buckets_deleted = 0
            
            for bucket in buckets_before:
                bucket_name = bucket.name
                try:
                    # List and delete all objects in bucket (individually for compatibility)
                    objects = client.list_objects(bucket_name, recursive=True)
                    count_in_bucket = 0
                    for obj in objects:
                        try:
                            client.remove_object(bucket_name, obj.object_name)
                            count_in_bucket += 1
                        except Exception as oe:
                            logger.warning(f"Error deleting object '{obj.object_name}' in bucket '{bucket_name}': {oe}")
                    total_objects += count_in_bucket
                    
                    # Delete the bucket itself
                    client.remove_bucket(bucket_name)
                    buckets_deleted += 1
                    logger.debug(f"Deleted bucket '{bucket_name}'")
                    
                except Exception as e:
                    logger.warning(f"Could not clean bucket {bucket_name}: {e}")
            
            # Verify cleanup
            buckets_after = list(client.list_buckets())
            bucket_count_after = len(buckets_after)
            
            logger.info(f"[PASS] MinIO cleanup completed: {bucket_count_before} → {bucket_count_after} buckets, ~{total_objects} objects deleted")
            
            return {
                "status": "success",
                "buckets_deleted": buckets_deleted,
                "objects_deleted": total_objects,
                "final_buckets": bucket_count_after
            }
        
        except ImportError:
            logger.warning("[WARN] MinIO client not installed, skipping MinIO cleanup")
            return {"status": "skipped", "reason": "minio not installed"}
        except Exception as e:
            logger.error(f"[FAIL] MinIO cleanup failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_database_connectivity(self) -> Dict[str, Any]:
        """Test connectivity to all databases after cleanup"""
        logger.info("[SEARCH] Testing database connectivity...")
        
        connectivity_results = {}
        
        # Test Neo4j
        try:
            from neo4j import GraphDatabase
            uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
            username = os.getenv("NEO4J_USERNAME", "neo4j")
            password = os.getenv("NEO4J_PASSWORD", "password")
            
            with GraphDatabase.driver(uri, auth=(username, password)) as driver:
                with driver.session() as session:
                    result = session.run("RETURN 1 as test")
                    test_value = result.single()["test"]
                    connectivity_results["neo4j"] = {"status": "connected", "test_value": test_value}
        except Exception as e:
            connectivity_results["neo4j"] = {"status": "error", "error": str(e)}
        
        # Test ChromaDB
        try:
            import chromadb
            host = os.getenv("CHROMADB_HOST", "localhost")
            port = int(os.getenv("CHROMADB_PORT", "8001"))
            
            client = chromadb.HttpClient(host=host, port=port)
            collections = client.list_collections()
            connectivity_results["chromadb"] = {"status": "connected", "collections": len(collections)}
        except Exception as e:
            connectivity_results["chromadb"] = {"status": "error", "error": str(e)}
        
        # Test Qdrant
        try:
            from qdrant_client import QdrantClient
            host = os.getenv("QDRANT_HOST", "localhost")
            port = int(os.getenv("QDRANT_PORT", "6333"))
            
            client = QdrantClient(host=host, port=port)
            collections = client.get_collections()
            connectivity_results["qdrant"] = {"status": "connected", "collections": len(collections.collections)}
        except Exception as e:
            connectivity_results["qdrant"] = {"status": "error", "error": str(e)}
        
        # Test Weaviate
        try:
            import weaviate
            host = os.getenv("WEAVIATE_HOST", "localhost")
            port = int(os.getenv("WEAVIATE_PORT", "8080"))
            url = f"http://{host}:{port}"
            
            client = weaviate.Client(url)
            schema = client.schema.get()
            classes = schema.get("classes", [])
            connectivity_results["weaviate"] = {"status": "connected", "classes": len(classes)}
        except Exception as e:
            connectivity_results["weaviate"] = {"status": "error", "error": str(e)}
        
        # Test MinIO
        try:
            from minio import Minio
            endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9000")
            access_key = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
            secret_key = os.getenv("MINIO_SECRET_KEY", "minioadmin")
            secure = os.getenv("MINIO_SECURE", "false").lower() == "true"
            
            client = Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=secure)
            buckets = list(client.list_buckets())
            connectivity_results["minio"] = {"status": "connected", "buckets": len(buckets)}
        except Exception as e:
            connectivity_results["minio"] = {"status": "error", "error": str(e)}
        
        return connectivity_results
    
    async def run_cleanup(self) -> Dict[str, Any]:
        """Run complete database cleanup"""
        logger.info("[START] Starting comprehensive database cleanup...")
        logger.info("=" * 60)
        
        start_time = time.time()
        
        # Run all cleanup operations
        cleanup_tasks = [
            ("neo4j", self.cleanup_neo4j()),
            ("chromadb", self.cleanup_chromadb()),
            ("qdrant", self.cleanup_qdrant()),
            ("weaviate", self.cleanup_weaviate()),
            ("minio", self.cleanup_minio())
        ]
        
        # Execute cleanup tasks
        for db_name, task in cleanup_tasks:
            try:
                result = await task
                self.cleanup_results[db_name] = result
            except Exception as e:
                logger.error(f"[FAIL] {db_name} cleanup failed: {e}")
                self.cleanup_results[db_name] = {"status": "error", "error": str(e)}
        
        # Test connectivity
        connectivity_results = await self.test_database_connectivity()
        
        cleanup_time = time.time() - start_time
        
        # Print summary
        logger.info("=" * 60)
        logger.info("📊 Database Cleanup Summary")
        logger.info("=" * 60)
        
        for db_name, result in self.cleanup_results.items():
            status = result.get("status", "unknown")
            if status == "success":
                logger.info(f"[PASS] {db_name.upper()}: Cleaned successfully")
                if "nodes_deleted" in result:
                    logger.info(f"   - Nodes deleted: {result['nodes_deleted']}")
                    logger.info(f"   - Relationships deleted: {result['relationships_deleted']}")
                elif "collections_deleted" in result:
                    logger.info(f"   - Collections deleted: {result['collections_deleted']}")
                elif "buckets_deleted" in result:
                    logger.info(f"   - Buckets deleted: {result['buckets_deleted']}")
                    logger.info(f"   - Objects deleted: {result['objects_deleted']}")
            elif status == "skipped":
                logger.info(f"[WARN] {db_name.upper()}: Skipped ({result.get('reason', 'unknown reason')})")
            else:
                logger.error(f"[FAIL] {db_name.upper()}: Failed ({result.get('error', 'unknown error')})")
        
        logger.info(f"\n🕐 Total cleanup time: {cleanup_time:.2f} seconds")
        
        # Connectivity summary
        logger.info("\n[SEARCH] Database Connectivity Test Results:")
        for db_name, conn_result in connectivity_results.items():
            status = conn_result.get("status", "unknown")
            if status == "connected":
                logger.info(f"[PASS] {db_name.upper()}: Connected and ready")
            else:
                logger.error(f"[FAIL] {db_name.upper()}: Connection failed ({conn_result.get('error', 'unknown error')})")
        
        return {
            "cleanup_results": self.cleanup_results,
            "connectivity_results": connectivity_results,
            "cleanup_time": cleanup_time,
            "success": all(r.get("status") in ["success", "skipped"] for r in self.cleanup_results.values())
        }


async def main():
    """Main cleanup execution"""
    parser = argparse.ArgumentParser(description="Clean all Kotaemon databases")
    parser.add_argument("--confirm", action="store_true", help="Skip confirmation prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if not args.confirm:
        print("WARNING: This will delete ALL data from ALL databases")
        print("Databases that will be cleaned:")
        print("  - Neo4j (all nodes and relationships)")
        print("  - ChromaDB (all collections and documents)")
        print("  - Qdrant (all collections and points)")
        print("  - Weaviate (all classes and objects)")
        print("  - MinIO (all buckets and objects)")
        print()
        
        response = input("Are you sure you want to continue? (type 'yes' to confirm): ")
        if response.lower() != 'yes':
            print("Cleanup cancelled")
            return 1
    
    cleaner = DatabaseCleaner(verbose=args.verbose)
    result = await cleaner.run_cleanup()
    
    if result["success"]:
        logger.info("🎉 Database cleanup completed successfully!")
        return 0
    else:
        logger.error("[WARN] Some cleanup operations failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)