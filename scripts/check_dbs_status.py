#!/usr/bin/env python3
"""
Check Databases Status (Neo4j + Vector DB)
=========================================

This script checks the current status of Neo4j and the default vector DB (Chroma).
"""

import logging
from neo4j import GraphDatabase
import json

def check_vector_db_status():
    """Check current vector DB (Chroma) status: collections and a sample of docs."""
    try:
        import chromadb
        host = os.getenv("CHROMADB_HOST", "localhost")
        port = int(os.getenv("CHROMADB_PORT", "8001"))
        client = chromadb.HttpClient(host=host, port=port)
        collections = client.list_collections()
        print(f"\n🔍 ChromaDB at {host}:{port}")
        print(f"📊 Collections: {[c.name for c in collections]}")

        file_key = os.getenv("GRAPHRAG_FILE_KEY", "unknown")
        coll_name = f"entities-{file_key}"
        try:
            coll = client.get_collection(coll_name)
            count = coll.count()
            print(f"📦 Collection '{coll_name}': {count} items")
            if count:
                res = coll.get(limit=3, include=["ids","metadatas"]) or {}
                print("📋 Sample IDs:", res.get("ids", [])[:3])
                print("📋 Sample metadatas:", json.dumps(res.get("metadatas", [])[:3], indent=2))
        except Exception as e:
            print(f"ℹ️ Collection '{coll_name}' not found or empty: {e}")
    except Exception as e:
        print(f"❌ Error checking ChromaDB status: {e}")
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv("local_dev.env")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_neo4j_status():
    """Check current Neo4j database status."""
    
    try:
        # Connect to Neo4j
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        username = os.getenv("NEO4J_USERNAME", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password")
        
        print(f"🔍 Connecting to Neo4j at {uri}")
        
        with GraphDatabase.driver(uri, auth=(username, password)) as driver:
            with driver.session() as session:
                # Count all nodes
                result = session.run("MATCH (n) RETURN count(n) as node_count")
                node_count = result.single()["node_count"]
                print(f"📊 Total nodes: {node_count}")
                
                # Count all relationships
                result = session.run("MATCH ()-[r]->() RETURN count(r) as rel_count")
                rel_count = result.single()["rel_count"]
                print(f"📊 Total relationships: {rel_count}")
                
                # Get all labels
                result = session.run("CALL db.labels()")
                labels = [record["label"] for record in result]
                print(f"📊 Node labels: {labels}")
                
                # Get all relationship types
                result = session.run("CALL db.relationshipTypes()")
                rel_types = [record["relationshipType"] for record in result]
                print(f"📊 Relationship types: {rel_types}")
                
                # If there are nodes, show them
                if node_count > 0:
                    print("\n📋 Sample nodes:")
                    result = session.run("MATCH (n) RETURN n, labels(n) as labels LIMIT 10")
                    for i, record in enumerate(result):
                        node = record["n"]
                        labels = record["labels"]
                        print(f"  {i+1}: {dict(node)} (Labels: {labels})")

                # Show sample with embedding flags
                print("\n📋 Nodes with has_embedding property (sample):")
                result = session.run("MATCH (n) WHERE n.has_embedding IS NOT NULL RETURN n.name as name, n.has_embedding as has_embedding, n.embedding_dimension as dim, labels(n) as labels LIMIT 10")
                for r in result:
                    print(f"  - {r['name']} (labels={r['labels']}) has_embedding={r['has_embedding']} dim={r['dim']}")
                
                # If there are relationships, show them
                if rel_count > 0:
                    print("\n📋 Sample relationships:")
                    result = session.run("MATCH (a)-[r]->(b) RETURN a, r, b, type(r) as rel_type LIMIT 5")
                    for i, record in enumerate(result):
                        a = record["a"]
                        r = record["r"]
                        b = record["b"]
                        rel_type = record["rel_type"]
                        print(f"  {i+1}: {dict(a)} -[{rel_type}]-> {dict(b)}")
                        print(f"      Relationship: {dict(r)}")
                
                # Check for specific problematic labels
                for label in ["Node", "Relationship"]:
                    result = session.run(f"MATCH (n:{label}) RETURN count(n) as count")
                    count = result.single()["count"]
                    if count > 0:
                        print(f"⚠️ Found {count} nodes with label '{label}'")
                        
                        # Show these nodes
                        result = session.run(f"MATCH (n:{label}) RETURN n LIMIT 5")
                        for i, record in enumerate(result):
                            node = record["n"]
                            print(f"    {i+1}: {dict(node)}")
                    else:
                        print(f"✅ No nodes with label '{label}'")
                
                print(f"\n{'='*50}")
                if node_count == 0 and rel_count == 0:
                    print("✅ Neo4j database is completely empty")
                else:
                    print(f"⚠️ Neo4j database contains {node_count} nodes and {rel_count} relationships")
                print(f"{'='*50}")
                
    except Exception as e:
        print(f"❌ Error checking Neo4j status: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_neo4j_status()
    check_vector_db_status()