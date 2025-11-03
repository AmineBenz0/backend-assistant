Scripts for Backend Ops
=======================

This folder contains operational scripts for the backend. Run commands from the repository root unless noted otherwise.

Prerequisites
-------------
- Python 3.10+
- Install dependencies:

```powershell
# PowerShell (repo root)
python -m pip install -r backend/requirements.txt
python -m pip install -r backend/scripts/requirements.txt
```

```bash
# Bash/WSL (repo root)
python3 -m pip install -r backend/requirements.txt
python3 -m pip install -r backend/scripts/requirements.txt
```

- Environment: copy and fill `backend/local.env`. You can also pass flags/inline env vars.


ingest_langfuse_prompts.py
--------------------------
Ingests text prompts from `backend/libs/llm_service/prompts/*.txt` into Langfuse Prompt Management.

Required env (project-scoped keys):
- `LANGFUSE_PUBLIC_KEY`
- `LANGFUSE_SECRET_KEY`
- `LANGFUSE_HOST` (e.g., `http://localhost:3000`)

Optional env:
- `LANGFUSE_ORGANIZATION_NAME` (for logs)
- `LANGFUSE_PROJECT_NAME` (for logs)

Usage:

```powershell
# Dry run
python backend/scripts/ingest_langfuse_prompts.py --dry-run --organization dxc --project d.pac

# Real ingestion (explicit creds)
python backend/scripts/ingest_langfuse_prompts.py --label production ^
  --organization dxc --project d.pac ^
  --host http://localhost:3000 ^
  --public-key pk-... ^
  --secret-key sk-...
```

```bash
# Dry run
python3 backend/scripts/ingest_langfuse_prompts.py --dry-run --organization dxc --project d.pac

# Real ingestion
python3 backend/scripts/ingest_langfuse_prompts.py --label production \
  --organization dxc --project d.pac \
  --host http://localhost:3000 \
  --public-key pk-... \
  --secret-key sk-...
```

Notes:
- Project selection is determined by the API keys; org/project flags are informational for logs.
- Defaults: model `gpt-4o`, temperature `0` (override with `--model` and `--temperature`).


check_dbs_status.py
-------------------
Quick status for Neo4j and ChromaDB.

```powershell
python backend/scripts/check_dbs_status.py
```

Reads env for connection params (e.g., `NEO4J_URI`, `CHROMADB_HOST`, `CHROMADB_PORT`).


cleanup_databases.py
--------------------
Deletes data from Neo4j, ChromaDB, Qdrant, Weaviate, and MinIO. Use with caution.

```powershell
python backend/scripts/cleanup_databases.py --confirm
```

Optional:
- `--verbose` for detailed logs

Env variables used include: `NEO4J_*`, `CHROMADB_*`, `QDRANT_*`, `WEAVIATE_*`, `MINIO_*`.


setup_minio.py
--------------
Creates a demo bucket/folder and uploads a sample file to MinIO.

```powershell
python backend/scripts/setup_minio.py
```

Defaults:
- Endpoint: `localhost:9000`, access/secret: `minioadmin`
- Bucket: `testclient`, Folder: `testproject`
- Uploads `backend/raw_files/CV Zakaria Hamane EN.pdf`


Tips
----
- PowerShell does not support piping to `cat`; run scripts without `| cat`.
- If running from `backend/`, drop the leading `backend/` path segment in commands.
- Docker services in `backend/docker-compose.local.yml` expose defaults matching the env in `backend/local.env`.


