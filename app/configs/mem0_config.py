import os


POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "postgres")
POSTGRES_PORT = os.environ.get("POSTGRES_PORT", "5432")
POSTGRES_DB = os.environ.get("POSTGRES_DB", "postgres")
POSTGRES_USER = os.environ.get("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "postgres")
POSTGRES_COLLECTION_NAME = os.environ.get("POSTGRES_COLLECTION_NAME", "memories")

MEMGRAPH_URI = os.environ.get("MEMGRAPH_URI", "bolt://localhost:7687")
MEMGRAPH_USERNAME = os.environ.get("MEMGRAPH_USERNAME", "memgraph")
MEMGRAPH_PASSWORD = os.environ.get("MEMGRAPH_PASSWORD", "mem0graph")

HISTORY_DB_PATH = os.environ.get("HISTORY_DB_PATH", "/app/history/history.db")



mem0_config = {
    "version": "v1.1",
    "vector_store": {
        "provider": "pgvector",
        "config": {
            "host": POSTGRES_HOST,
            "port": int(POSTGRES_PORT),
            "dbname": POSTGRES_DB,
            "user": POSTGRES_USER,
            "password": POSTGRES_PASSWORD,
            "collection_name": POSTGRES_COLLECTION_NAME,
        },
    },
    "llm": {
        "provider": "azure_openai",
        "config": {
            "model": os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT"],
            "temperature": 0.2,
            "max_tokens": 1000,
            "azure_kwargs": {
                "azure_deployment": os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT"],
                "azure_endpoint": os.environ["AZURE_OPENAI_ENDPOINT"],
                "api_version": os.environ["AZURE_OPENAI_API_VERSION"],
                "api_key": os.environ["AZURE_OPENAI_API_KEY"],
            },
        },
    },
    "embedder": {
        "provider": "azure_openai",
        "config": {
            "model":  os.environ["AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT"],
            "embedding_dims": os.environ["EMBEDDING_MODEL_DIM"],
            "azure_kwargs": {
                "azure_deployment":  os.environ["AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT"],
                "azure_endpoint": os.environ["AZURE_OPENAI_ENDPOINT"],
                "api_version": os.environ["AZURE_OPENAI_API_VERSION"],
                "api_key": os.environ["AZURE_OPENAI_API_KEY"],
            },
        },
    },
    "history_db_path": HISTORY_DB_PATH,
}

# import json
# print(json.dumps(mem0_config, indent=4))

