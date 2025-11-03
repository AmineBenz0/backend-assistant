#!/usr/bin/env python3
"""
Configuration Manager for GraphRAG Pipeline
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    """Configuration manager for loading and managing application settings"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "config.yml"
        self._config = {}
        self.config = {}
        self.load_config()
    
    def load_config(self):
        """Load configuration from YAML file"""
        config_file = Path(self.config_path)
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    self._config = yaml.safe_load(f) or {}
                    self.config = self._config.copy()
            except Exception as e:
                print(f"Warning: Could not load {self.config_path}: {e}")
                self._config = self._get_default_config()
                self.config = self._config.copy()
        else:
            # Try to load from environment file as fallback
            env_file = Path("local_dev.env")
            if env_file.exists():
                self._load_env_file(env_file)
            else:
                self._config = self._get_default_config()
                self.config = self._config.copy()
    
    def _load_env_file(self, env_file: Path):
        """Load configuration from environment file"""
        env_config = {}
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_config[key.strip()] = value.strip()
        
        # Convert flat env config to nested structure
        self._config = {
            "database": {
                "neo4j": {
                    "uri": env_config.get("NEO4J_URI", "bolt://localhost:7687"),
                    "username": env_config.get("NEO4J_USERNAME", "neo4j"),
                    "password": env_config.get("NEO4J_PASSWORD", "password")
                },
                "chromadb": {
                    "host": env_config.get("CHROMADB_HOST", "localhost"),
                    "port": int(env_config.get("CHROMADB_PORT", "8001"))
                },
                "minio": {
                    "endpoint": env_config.get("MINIO_ENDPOINT", "localhost:9000"),
                    "access_key": env_config.get("MINIO_ACCESS_KEY", "minioadmin"),
                    "secret_key": env_config.get("MINIO_SECRET_KEY", "minioadmin")
                }
            },
            "environment": env_config.get("ENVIRONMENT", "development")
        }
        self.config = self._config.copy()
    
    def _get_default_config(self):
        """Get default configuration"""
        return {
            "database": {
                "neo4j": {
                    "uri": "bolt://localhost:7687",
                    "username": "neo4j",
                    "password": "password"
                },
                "chromadb": {
                    "host": "localhost",
                    "port": 8001
                },
                "minio": {
                    "endpoint": "localhost:9000",
                    "access_key": "minioadmin",
                    "secret_key": "minioadmin"
                }
            },
            "pipeline": {
                "chunk_size": 1000,
                "chunk_overlap": 200,
                "max_workers": 4
            },
            "models": {
                "llm": {
                    "provider": "openai",
                    "model": "gpt-4"
                },
                "embeddings": {
                    "provider": "openai",
                    "model": "text-embedding-ada-002"
                }
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },
            "llm_service": {
                "provider": "openai",
                "model": "gpt-4",
                "api_key": "your-api-key-here",
                "temperature": 0.7,
                "max_tokens": 2000
            },
            "embeddings": {
                "provider": "openai",
                "model": "text-embedding-ada-002",
                "api_key": "your-api-key-here",
                "dimensions": 1536
            },
            "graph_builder": {
                "max_entities_per_chunk": 50,
                "relationship_threshold": 0.7,
                "entity_extraction_model": "gpt-4",
                "relationship_extraction_model": "gpt-4"
            },
            "preprocessing": {
                "chunk_size": 1000,
                "chunk_overlap": 200,
                "supported_formats": ["pdf", "txt", "docx", "md"],
                "max_file_size_mb": 100
            },
            "environment": "test"
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation"""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return os.getenv(key.upper().replace('.', '_'), default)
        
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self.config = self._config.copy()
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate configuration and return status"""
        errors = []
        warnings = []
        
        # Check required sections
        required_sections = ["database"]
        for section in required_sections:
            if section not in self._config:
                errors.append(f"Missing required section: {section}")
        
        # Check database configuration
        if "database" in self._config:
            db_config = self._config["database"]
            if "neo4j" not in db_config and "chromadb" not in db_config:
                warnings.append("No database connections configured")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def is_loaded(self) -> bool:
        """Check if configuration is loaded"""
        return len(self._config) > 0


# Global config manager instance
config_manager = ConfigManager()


def get_config(key: str, default: Any = None) -> Any:
    """Get configuration value"""
    return config_manager.get(key, default)


def validate_environment() -> bool:
    """Validate environment configuration"""
    result = config_manager.validate_config()
    return result["valid"]


if __name__ == "__main__":
    print("Configuration Manager Test")
    print("=" * 40)
    print(f"Config file: {config_manager.config_path}")
    print(f"Loaded config sections: {list(config_manager._config.keys())}")
    
    validation = config_manager.validate_config()
    print(f"Valid: {validation['valid']}")
    if validation['warnings']:
        print(f"Warnings: {validation['warnings']}")
    if validation['errors']:
        print(f"Errors: {validation['errors']}")