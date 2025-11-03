"""
Database Connection Configuration Module

Provides comprehensive database connection configuration with proper error handling,
fallbacks, and connection testing for all supported database services.
"""

import os
import sys
import time
import asyncio
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
from pathlib import Path

# Import database clients (with fallbacks for missing dependencies)
try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False

try:
    from minio import Minio
    MINIO_AVAILABLE = True
except ImportError:
    MINIO_AVAILABLE = False

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    from qdrant_client import QdrantClient
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False

try:
    import weaviate
    WEAVIATE_AVAILABLE = True
except ImportError:
    WEAVIATE_AVAILABLE = False

try:
    from arango import ArangoClient
    ARANGODB_AVAILABLE = True
except ImportError:
    ARANGODB_AVAILABLE = False


class DatabaseType(Enum):
    """Supported database types"""
    VECTOR = "vector"
    GRAPH = "graph"
    STORAGE = "storage"
    CACHE = "cache"


class ConnectionStatus(Enum):
    """Connection status enumeration"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    TIMEOUT = "timeout"
    UNAVAILABLE = "unavailable"


@dataclass
class DatabaseConfig:
    """Database configuration with connection parameters"""
    name: str
    db_type: DatabaseType
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    database: Optional[str] = None
    uri: Optional[str] = None
    api_key: Optional[str] = None
    secure: bool = False
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: int = 5
    fallback_configs: List['DatabaseConfig'] = field(default_factory=list)
    extra_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConnectionResult:
    """Result of database connection attempt"""
    config: DatabaseConfig
    status: ConnectionStatus
    message: str
    connection_time: Optional[float] = None
    error: Optional[Exception] = None
    client: Optional[Any] = None


class DatabaseConnectionManager:
    """Manages database connections with configuration, testing, and fallbacks"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.configs: Dict[str, DatabaseConfig] = {}
        self.connections: Dict[str, ConnectionResult] = {}
        self._load_configurations()
    
    def _load_configurations(self) -> None:
        """Load database configurations from environment variables"""
        self.configs = {
            # ChromaDB Configuration
            "chromadb": DatabaseConfig(
                name="chromadb",
                db_type=DatabaseType.VECTOR,
                host=os.getenv("CHROMA_HOST", "localhost"),
                port=int(os.getenv("CHROMA_PORT", "8001")),
                uri=os.getenv("CHROMADB_URL", f"http://{os.getenv('CHROMA_HOST', 'localhost')}:{os.getenv('CHROMA_PORT', '8001')}"),
                timeout=int(os.getenv("CHROMA_TIMEOUT", "30")),
                retry_attempts=int(os.getenv("CHROMA_RETRY_ATTEMPTS", "3")),
                extra_params={
                    "collection_name": os.getenv("CHROMA_COLLECTION_NAME", "kotaemon_documents")
                }
            ),
            
            # Neo4j Configuration
            "neo4j": DatabaseConfig(
                name="neo4j",
                db_type=DatabaseType.GRAPH,
                host=os.getenv("NEO4J_HOST", "localhost"),
                port=int(os.getenv("NEO4J_PORT", "7687")),
                username=os.getenv("NEO4J_USERNAME", "neo4j"),
                password=os.getenv("NEO4J_PASSWORD", "password"),
                database=os.getenv("NEO4J_DATABASE", "neo4j"),
                uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
                timeout=int(os.getenv("NEO4J_TIMEOUT", "30")),
                retry_attempts=int(os.getenv("NEO4J_RETRY_ATTEMPTS", "3"))
            ),
            
            # MinIO Configuration
            "minio": DatabaseConfig(
                name="minio",
                db_type=DatabaseType.STORAGE,
                host=os.getenv("MINIO_HOST", "localhost"),
                port=int(os.getenv("MINIO_PORT", "9000")),
                username=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
                password=os.getenv("MINIO_SECRET_KEY", "minioadmin"),
                secure=os.getenv("MINIO_SECURE", "false").lower() == "true",
                uri=os.getenv("MINIO_ENDPOINT", "localhost:9000"),
                timeout=int(os.getenv("MINIO_TIMEOUT", "30")),
                retry_attempts=int(os.getenv("MINIO_RETRY_ATTEMPTS", "3")),
                extra_params={
                    "bucket": os.getenv("MINIO_BUCKET", "kotaemon-pipeline")
                }
            ),
            
            # Redis Configuration
            "redis": DatabaseConfig(
                name="redis",
                db_type=DatabaseType.CACHE,
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", "6379")),
                password=os.getenv("REDIS_PASSWORD"),
                database=os.getenv("REDIS_DB", "0"),
                timeout=int(os.getenv("REDIS_TIMEOUT", "30")),
                retry_attempts=int(os.getenv("REDIS_RETRY_ATTEMPTS", "3"))
            ),
            
            # Qdrant Configuration
            "qdrant": DatabaseConfig(
                name="qdrant",
                db_type=DatabaseType.VECTOR,
                host=os.getenv("QDRANT_HOST", "localhost"),
                port=int(os.getenv("QDRANT_PORT", "6333")),
                api_key=os.getenv("QDRANT_API_KEY"),
                uri=os.getenv("QDRANT_URL", "http://localhost:6333"),
                timeout=int(os.getenv("QDRANT_TIMEOUT", "30")),
                retry_attempts=int(os.getenv("QDRANT_RETRY_ATTEMPTS", "3")),
                extra_params={
                    "collection_name": os.getenv("QDRANT_COLLECTION_NAME", "kotaemon_documents")
                }
            ),
            
            # Weaviate Configuration
            "weaviate": DatabaseConfig(
                name="weaviate",
                db_type=DatabaseType.VECTOR,
                host=os.getenv("WEAVIATE_HOST", "localhost"),
                port=int(os.getenv("WEAVIATE_PORT", "8080")),
                api_key=os.getenv("WEAVIATE_API_KEY"),
                uri=os.getenv("WEAVIATE_URL", "http://localhost:8080"),
                timeout=int(os.getenv("WEAVIATE_TIMEOUT", "30")),
                retry_attempts=int(os.getenv("WEAVIATE_RETRY_ATTEMPTS", "3")),
                extra_params={
                    "class_name": os.getenv("WEAVIATE_CLASS_NAME", "KotaemonDocument")
                }
            ),
            
            # ArangoDB Configuration
            "arangodb": DatabaseConfig(
                name="arangodb",
                db_type=DatabaseType.GRAPH,
                host=os.getenv("ARANGODB_HOST", "localhost"),
                port=int(os.getenv("ARANGODB_PORT", "8529")),
                username=os.getenv("ARANGODB_USERNAME", "root"),
                password=os.getenv("ARANGODB_PASSWORD", "password"),
                database=os.getenv("ARANGODB_DATABASE", "kotaemon"),
                uri=os.getenv("ARANGODB_URL", "http://localhost:8529"),
                timeout=int(os.getenv("ARANGODB_TIMEOUT", "30")),
                retry_attempts=int(os.getenv("ARANGODB_RETRY_ATTEMPTS", "3"))
            )
        }
        
        # Set up fallback configurations
        self._setup_fallbacks()
    
    def _setup_fallbacks(self) -> None:
        """Set up fallback configurations for database services"""
        # Vector database fallbacks: ChromaDB -> Qdrant -> Weaviate
        if "chromadb" in self.configs and "qdrant" in self.configs:
            self.configs["chromadb"].fallback_configs.append(self.configs["qdrant"])
        if "chromadb" in self.configs and "weaviate" in self.configs:
            self.configs["chromadb"].fallback_configs.append(self.configs["weaviate"])
        
        # Graph database fallbacks: Neo4j -> ArangoDB
        if "neo4j" in self.configs and "arangodb" in self.configs:
            self.configs["neo4j"].fallback_configs.append(self.configs["arangodb"])
    
    def test_connection(self, config: DatabaseConfig) -> ConnectionResult:
        """Test connection to a specific database"""
        start_time = time.time()
        
        try:
            if config.name == "chromadb":
                return self._test_chromadb_connection(config, start_time)
            elif config.name == "neo4j":
                return self._test_neo4j_connection(config, start_time)
            elif config.name == "minio":
                return self._test_minio_connection(config, start_time)
            elif config.name == "redis":
                return self._test_redis_connection(config, start_time)
            elif config.name == "qdrant":
                return self._test_qdrant_connection(config, start_time)
            elif config.name == "weaviate":
                return self._test_weaviate_connection(config, start_time)
            elif config.name == "arangodb":
                return self._test_arangodb_connection(config, start_time)
            else:
                return ConnectionResult(
                    config=config,
                    status=ConnectionStatus.ERROR,
                    message=f"Unknown database type: {config.name}",
                    connection_time=time.time() - start_time
                )
        
        except Exception as e:
            return ConnectionResult(
                config=config,
                status=ConnectionStatus.ERROR,
                message=f"Connection test failed: {str(e)}",
                connection_time=time.time() - start_time,
                error=e
            )
    
    def _test_chromadb_connection(self, config: DatabaseConfig, start_time: float) -> ConnectionResult:
        """Test ChromaDB connection"""
        if not CHROMADB_AVAILABLE:
            return ConnectionResult(
                config=config,
                status=ConnectionStatus.UNAVAILABLE,
                message="ChromaDB client not available. Install with: pip install chromadb",
                connection_time=time.time() - start_time
            )
        
        try:
            # Create ChromaDB client
            client = chromadb.HttpClient(
                host=config.host,
                port=config.port,
                settings=ChromaSettings(
                    chroma_client_auth_provider="chromadb.auth.basic.BasicAuthClientProvider",
                    chroma_client_auth_credentials=f"{config.username}:{config.password}" if config.username else None
                )
            )
            
            # Test connection by listing collections
            collections = client.list_collections()
            
            return ConnectionResult(
                config=config,
                status=ConnectionStatus.CONNECTED,
                message=f"Connected successfully. Found {len(collections)} collections.",
                connection_time=time.time() - start_time,
                client=client
            )
        
        except Exception as e:
            return ConnectionResult(
                config=config,
                status=ConnectionStatus.ERROR,
                message=f"ChromaDB connection failed: {str(e)}",
                connection_time=time.time() - start_time,
                error=e
            )
    
    def _test_neo4j_connection(self, config: DatabaseConfig, start_time: float) -> ConnectionResult:
        """Test Neo4j connection"""
        if not NEO4J_AVAILABLE:
            return ConnectionResult(
                config=config,
                status=ConnectionStatus.UNAVAILABLE,
                message="Neo4j driver not available. Install with: pip install neo4j",
                connection_time=time.time() - start_time
            )
        
        try:
            # Create Neo4j driver
            driver = GraphDatabase.driver(
                config.uri,
                auth=(config.username, config.password),
                connection_timeout=config.timeout
            )
            
            # Test connection
            with driver.session(database=config.database) as session:
                result = session.run("RETURN 1 as test")
                test_value = result.single()["test"]
                
                if test_value == 1:
                    return ConnectionResult(
                        config=config,
                        status=ConnectionStatus.CONNECTED,
                        message="Connected successfully. Database is responsive.",
                        connection_time=time.time() - start_time,
                        client=driver
                    )
        
        except Exception as e:
            return ConnectionResult(
                config=config,
                status=ConnectionStatus.ERROR,
                message=f"Neo4j connection failed: {str(e)}",
                connection_time=time.time() - start_time,
                error=e
            )
    
    def _test_minio_connection(self, config: DatabaseConfig, start_time: float) -> ConnectionResult:
        """Test MinIO connection"""
        if not MINIO_AVAILABLE:
            return ConnectionResult(
                config=config,
                status=ConnectionStatus.UNAVAILABLE,
                message="MinIO client not available. Install with: pip install minio",
                connection_time=time.time() - start_time
            )
        
        try:
            # Create MinIO client
            client = Minio(
                config.uri,
                access_key=config.username,
                secret_key=config.password,
                secure=config.secure
            )
            
            # Test connection by listing buckets
            buckets = list(client.list_buckets())
            
            return ConnectionResult(
                config=config,
                status=ConnectionStatus.CONNECTED,
                message=f"Connected successfully. Found {len(buckets)} buckets.",
                connection_time=time.time() - start_time,
                client=client
            )
        
        except Exception as e:
            return ConnectionResult(
                config=config,
                status=ConnectionStatus.ERROR,
                message=f"MinIO connection failed: {str(e)}",
                connection_time=time.time() - start_time,
                error=e
            )
    
    def _test_redis_connection(self, config: DatabaseConfig, start_time: float) -> ConnectionResult:
        """Test Redis connection"""
        if not REDIS_AVAILABLE:
            return ConnectionResult(
                config=config,
                status=ConnectionStatus.UNAVAILABLE,
                message="Redis client not available. Install with: pip install redis",
                connection_time=time.time() - start_time
            )
        
        try:
            # Create Redis client
            client = redis.Redis(
                host=config.host,
                port=config.port,
                password=config.password,
                db=int(config.database) if config.database else 0,
                socket_timeout=config.timeout,
                socket_connect_timeout=config.timeout
            )
            
            # Test connection
            response = client.ping()
            
            if response:
                return ConnectionResult(
                    config=config,
                    status=ConnectionStatus.CONNECTED,
                    message="Connected successfully. Redis is responsive.",
                    connection_time=time.time() - start_time,
                    client=client
                )
        
        except Exception as e:
            return ConnectionResult(
                config=config,
                status=ConnectionStatus.ERROR,
                message=f"Redis connection failed: {str(e)}",
                connection_time=time.time() - start_time,
                error=e
            )
    
    def _test_qdrant_connection(self, config: DatabaseConfig, start_time: float) -> ConnectionResult:
        """Test Qdrant connection"""
        if not QDRANT_AVAILABLE:
            return ConnectionResult(
                config=config,
                status=ConnectionStatus.UNAVAILABLE,
                message="Qdrant client not available. Install with: pip install qdrant-client",
                connection_time=time.time() - start_time
            )
        
        try:
            # Create Qdrant client
            client = QdrantClient(
                host=config.host,
                port=config.port,
                api_key=config.api_key,
                timeout=config.timeout
            )
            
            # Test connection by getting cluster info
            info = client.get_cluster_info()
            
            return ConnectionResult(
                config=config,
                status=ConnectionStatus.CONNECTED,
                message=f"Connected successfully. Cluster status: {info.status}",
                connection_time=time.time() - start_time,
                client=client
            )
        
        except Exception as e:
            return ConnectionResult(
                config=config,
                status=ConnectionStatus.ERROR,
                message=f"Qdrant connection failed: {str(e)}",
                connection_time=time.time() - start_time,
                error=e
            )
    
    def _test_weaviate_connection(self, config: DatabaseConfig, start_time: float) -> ConnectionResult:
        """Test Weaviate connection"""
        if not WEAVIATE_AVAILABLE:
            return ConnectionResult(
                config=config,
                status=ConnectionStatus.UNAVAILABLE,
                message="Weaviate client not available. Install with: pip install weaviate-client",
                connection_time=time.time() - start_time
            )
        
        try:
            # Create Weaviate client
            client = weaviate.Client(
                url=config.uri,
                auth_client_secret=weaviate.AuthApiKey(api_key=config.api_key) if config.api_key else None,
                timeout_config=(config.timeout, config.timeout)
            )
            
            # Test connection
            if client.is_ready():
                return ConnectionResult(
                    config=config,
                    status=ConnectionStatus.CONNECTED,
                    message="Connected successfully. Weaviate is ready.",
                    connection_time=time.time() - start_time,
                    client=client
                )
            else:
                return ConnectionResult(
                    config=config,
                    status=ConnectionStatus.ERROR,
                    message="Weaviate is not ready",
                    connection_time=time.time() - start_time
                )
        
        except Exception as e:
            return ConnectionResult(
                config=config,
                status=ConnectionStatus.ERROR,
                message=f"Weaviate connection failed: {str(e)}",
                connection_time=time.time() - start_time,
                error=e
            )
    
    def _test_arangodb_connection(self, config: DatabaseConfig, start_time: float) -> ConnectionResult:
        """Test ArangoDB connection"""
        if not ARANGODB_AVAILABLE:
            return ConnectionResult(
                config=config,
                status=ConnectionStatus.UNAVAILABLE,
                message="ArangoDB client not available. Install with: pip install python-arango",
                connection_time=time.time() - start_time
            )
        
        try:
            # Create ArangoDB client
            client = ArangoClient(hosts=config.uri)
            
            # Test connection
            db = client.db(config.database, username=config.username, password=config.password)
            version = db.version()
            
            return ConnectionResult(
                config=config,
                status=ConnectionStatus.CONNECTED,
                message=f"Connected successfully. ArangoDB version: {version}",
                connection_time=time.time() - start_time,
                client=client
            )
        
        except Exception as e:
            return ConnectionResult(
                config=config,
                status=ConnectionStatus.ERROR,
                message=f"ArangoDB connection failed: {str(e)}",
                connection_time=time.time() - start_time,
                error=e
            )
    
    def test_all_connections(self) -> Dict[str, ConnectionResult]:
        """Test connections to all configured databases"""
        results = {}
        
        for name, config in self.configs.items():
            self.logger.info(f"Testing connection to {name}...")
            result = self.test_connection(config)
            results[name] = result
            self.connections[name] = result
        
        return results
    
    def test_connections_with_fallbacks(self, database_names: Optional[List[str]] = None) -> Dict[str, ConnectionResult]:
        """Test connections with fallback support"""
        if database_names is None:
            database_names = list(self.configs.keys())
        
        results = {}
        
        for name in database_names:
            if name not in self.configs:
                continue
            
            config = self.configs[name]
            result = self.test_connection(config)
            
            # If primary connection fails, try fallbacks
            if result.status != ConnectionStatus.CONNECTED and config.fallback_configs:
                self.logger.warning(f"Primary connection to {name} failed, trying fallbacks...")
                
                for fallback_config in config.fallback_configs:
                    fallback_result = self.test_connection(fallback_config)
                    if fallback_result.status == ConnectionStatus.CONNECTED:
                        self.logger.info(f"Fallback connection to {fallback_config.name} succeeded")
                        result = fallback_result
                        break
            
            results[name] = result
            self.connections[name] = result
        
        return results
    
    def get_connection_summary(self) -> Dict[str, Any]:
        """Get summary of all connection test results"""
        if not self.connections:
            self.test_all_connections()
        
        summary = {
            "total": len(self.connections),
            "connected": len([r for r in self.connections.values() if r.status == ConnectionStatus.CONNECTED]),
            "failed": len([r for r in self.connections.values() if r.status == ConnectionStatus.ERROR]),
            "unavailable": len([r for r in self.connections.values() if r.status == ConnectionStatus.UNAVAILABLE]),
            "by_type": {},
            "details": {}
        }
        
        # Group by database type
        for result in self.connections.values():
            db_type = result.config.db_type.value
            if db_type not in summary["by_type"]:
                summary["by_type"][db_type] = {"total": 0, "connected": 0, "failed": 0}
            
            summary["by_type"][db_type]["total"] += 1
            if result.status == ConnectionStatus.CONNECTED:
                summary["by_type"][db_type]["connected"] += 1
            elif result.status == ConnectionStatus.ERROR:
                summary["by_type"][db_type]["failed"] += 1
        
        # Add detailed results
        for name, result in self.connections.items():
            summary["details"][name] = {
                "status": result.status.value,
                "message": result.message,
                "connection_time": result.connection_time,
                "type": result.config.db_type.value
            }
        
        return summary
    
    def print_connection_results(self, show_details: bool = True) -> None:
        """Print connection test results in a formatted way"""
        if not self.connections:
            print("No connection tests have been run yet.")
            return
        
        print("🔗 Database Connection Test Results")
        print("=" * 50)
        
        # Print results by type
        for db_type in DatabaseType:
            type_results = [r for r in self.connections.values() if r.config.db_type == db_type]
            if not type_results:
                continue
            
            print(f"\n📊 {db_type.value.title()} Databases:")
            print("-" * 30)
            
            for result in type_results:
                status_icon = {
                    ConnectionStatus.CONNECTED: "✅",
                    ConnectionStatus.ERROR: "❌",
                    ConnectionStatus.UNAVAILABLE: "⚠️",
                    ConnectionStatus.TIMEOUT: "⏰",
                    ConnectionStatus.DISCONNECTED: "🔌"
                }.get(result.status, "❓")
                
                connection_time = f" ({result.connection_time:.2f}s)" if result.connection_time else ""
                print(f"{status_icon} {result.config.name}: {result.message}{connection_time}")
                
                if show_details and result.status == ConnectionStatus.CONNECTED:
                    print(f"   📍 {result.config.uri or f'{result.config.host}:{result.config.port}'}")
        
        # Print summary
        summary = self.get_connection_summary()
        print(f"\n📈 Summary: {summary['connected']}/{summary['total']} databases connected")
        
        if summary['failed'] > 0:
            print(f"❌ {summary['failed']} connections failed")
        if summary['unavailable'] > 0:
            print(f"⚠️  {summary['unavailable']} clients unavailable")
    
    def get_working_databases(self, db_type: Optional[DatabaseType] = None) -> List[ConnectionResult]:
        """Get list of working database connections"""
        working = [r for r in self.connections.values() if r.status == ConnectionStatus.CONNECTED]
        
        if db_type:
            working = [r for r in working if r.config.db_type == db_type]
        
        return working
    
    def get_primary_database(self, db_type: DatabaseType) -> Optional[ConnectionResult]:
        """Get the primary working database of a specific type"""
        working = self.get_working_databases(db_type)
        return working[0] if working else None
    
    def reload_configurations(self) -> None:
        """Reload database configurations from environment variables"""
        self._load_configurations()
        self.connections.clear()


def test_database_connections(database_names: Optional[List[str]] = None, use_fallbacks: bool = True) -> bool:
    """
    Test database connections and return True if at least one database of each required type is available
    
    Args:
        database_names: List of specific databases to test (None for all)
        use_fallbacks: Whether to use fallback configurations
    
    Returns:
        True if minimum required databases are available, False otherwise
    """
    print("🔍 Testing Database Connections")
    print("=" * 50)
    
    manager = DatabaseConnectionManager()
    
    if use_fallbacks:
        results = manager.test_connections_with_fallbacks(database_names)
    else:
        results = manager.test_all_connections()
    
    manager.print_connection_results()
    
    # Check if we have at least one working database of each required type
    required_types = [DatabaseType.VECTOR, DatabaseType.GRAPH, DatabaseType.STORAGE]
    available_types = []
    
    for db_type in required_types:
        working = manager.get_working_databases(db_type)
        if working:
            available_types.append(db_type)
    
    success = len(available_types) == len(required_types)
    
    if success:
        print("\n✅ Database connection tests passed!")
        print("All required database types are available.")
    else:
        missing_types = [t.value for t in required_types if t not in available_types]
        print(f"\n❌ Database connection tests failed!")
        print(f"Missing required database types: {', '.join(missing_types)}")
    
    return success


def main():
    """Main function for running database connection tests as a script"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test database connections")
    parser.add_argument("--databases", nargs="+", help="Specific databases to test")
    parser.add_argument("--no-fallbacks", action="store_true", help="Don't use fallback configurations")
    parser.add_argument("--details", action="store_true", help="Show detailed connection information")
    
    args = parser.parse_args()
    
    success = test_database_connections(
        database_names=args.databases,
        use_fallbacks=not args.no_fallbacks
    )
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())