# GraphRAG Backend Pipeline

A comprehensive GraphRAG (Graph Retrieval-Augmented Generation) pipeline that processes documents through a 12-step workflow to build knowledge graphs and store them in Neo4j.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.12+
- Git

### 1. Build and Start Services

```bash
# Clone the repository
git clone <repository-url>
cd kotaemon/backend

# Build and start all services
docker-compose -f docker-compose.local.yml up -d

# Check service status
docker-compose -f docker-compose.local.yml ps
```

### 2. Setup MinIO with Test Data

```bash
# Install MinIO Python client
cd scripts
pip install -r requirements.txt

# Create bucket and upload test files
python setup_minio.py
```

### 3. Setup minio test files

```bash
# Run verification script
python3 scripts/setup_minio.py
```

## 📋 Services Overview

| Service | Port | Purpose | URL |
|---------|------|---------|-----|
| **FastAPI App** | 8002 | Main API server | http://localhost:8002 |
| **MinIO** | 9000/9001 | Object storage | http://localhost:9001 |
| **Neo4j** | 7474/7687 | Graph database | http://localhost:7474 |
| **ChromaDB** | 8001 | Vector database | http://localhost:8001 |
| **Redis** | 6379 | Task queue | - |
| **Celery** | - | Background tasks | - |
| **Flower** | 5555 | Celery monitoring | http://localhost:5555 |

## 🔧 Configuration

### Environment Variables

Create a `local.env` file in the backend directory:

```env
# MinIO Configuration
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_SECURE=false

# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# Azure OpenAI (for embeddings)
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Redis Configuration
REDIS_URL=redis://:smucks@localhost:6379/0
```

## 📡 FastAPI Endpoints

### Health Check

```bash
curl http://localhost:8002/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-11T10:30:00Z",
  "services": {
    "database": "connected",
    "storage": "connected"
  }
}
```

### Process Documents (GraphRAG Pipeline)

**Endpoint:** `POST /api/v1/pipeline/process`

**Request Body:**
```json
{
  "client_id": "testclient",
  "project_id": "testproject",
  "pipeline_config": {
    "template_id": "graph_preprocessing",
    "enable_embeddings": true,
    "store_in_neo4j": true
  }
}
```

**Example using curl:**
```bash
curl -X POST "http://localhost:8002/api/v1/pipeline/process" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "testclient",
    "project_id": "testproject",
    "pipeline_config": {
      "template_id": "graph_preprocessing",
      "enable_embeddings": true,
      "store_in_neo4j": true
    }
  }'
```

**Response:**
```json
{
  "job_id": "job_1736593800_abc123",
  "status": "processing",
  "message": "Pipeline started successfully",
  "estimated_duration": "5-10 minutes",
  "steps": [
    "GetFiles",
    "parse_documents", 
    "create_base_text_units",
    "create_base_extracted_entities",
    "create_summarized_entities",
    "create_base_entity_graph",
    "create_final_entities",
    "create_final_nodes",
    "create_final_communities",
    "create_final_relationships",
    "create_final_text_units",
    "create_final_community_reports",
    "create_base_documents",
    "create_final_documents",
    "generate_entity_embeddings",
    "create_vector_index",
    "create_graph_index",
    "store_vector_embeddings",
    "store_graph_data"
  ]
}
```

### Check Job Status

**Endpoint:** `GET /api/v1/pipeline/status/{job_id}`

```bash
curl http://localhost:8002/api/v1/pipeline/status/job_1736593800_abc123
```

**Response:**
```json
{
  "job_id": "job_1736593800_abc123",
  "status": "completed",
  "progress": {
    "current_step": 19,
    "total_steps": 19,
    "percentage": 100
  },
  "results": {
    "entities_created": 477,
    "relationships_created": 113526,
    "communities_detected": 45,
    "processing_time": "8m 32s"
  },
  "neo4j_stats": {
    "nodes_stored": 477,
    "relationships_stored": 113526,
    "indexes_created": 3
  }
}
```

### Query Knowledge Graph

**Endpoint:** `POST /api/v1/graph/query`

**Request Body:**
```json
{
  "query": "MATCH (n:Entity) WHERE n.name CONTAINS 'technology' RETURN n LIMIT 10",
  "parameters": {}
}
```

**Example:**
```bash
curl -X POST "http://localhost:8002/api/v1/graph/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "MATCH (n:Entity)-[r:RELATES_TO]->(m:Entity) RETURN n.name, r.type, m.name LIMIT 5"
  }'
```

**Response:**
```json
{
  "results": [
    {
      "n.name": "Machine Learning",
      "r.type": "RELATES_TO", 
      "m.name": "Artificial Intelligence"
    },
    {
      "n.name": "Data Science",
      "r.type": "RELATES_TO",
      "m.name": "Analytics"
    }
  ],
  "count": 5,
  "execution_time": "0.023s"
}
```

### Search Entities

**Endpoint:** `GET /api/v1/entities/search`

**Query Parameters:**
- `q`: Search query
- `limit`: Number of results (default: 10)
- `type`: Entity type filter (optional)

```bash
curl "http://localhost:8002/api/v1/entities/search?q=machine%20learning&limit=5"
```

**Response:**
```json
{
  "entities": [
    {
      "id": "entity_123",
      "name": "Machine Learning",
      "type": "TECHNOLOGY",
      "description": "A subset of artificial intelligence...",
      "properties": {
        "confidence": 0.95,
        "mentions": 15
      }
    }
  ],
  "total": 1,
  "query": "machine learning"
}
```

### Get Entity Relationships

**Endpoint:** `GET /api/v1/entities/{entity_id}/relationships`

```bash
curl http://localhost:8002/api/v1/entities/entity_123/relationships
```

**Response:**
```json
{
  "entity": {
    "id": "entity_123",
    "name": "Machine Learning"
  },
  "relationships": [
    {
      "target_entity": {
        "id": "entity_456", 
        "name": "Artificial Intelligence"
      },
      "relationship_type": "IS_PART_OF",
      "strength": 0.89,
      "description": "Machine Learning is a subset of AI"
    }
  ],
  "total": 15
}
```

## 🧪 Testing the Pipeline

### 1. Upload Test Document

```bash
# Place your PDF in raw_files directory
cp /path/to/your/document.pdf raw_files/

# Run MinIO setup to upload it
cd scripts
python setup_minio.py
```

### 2. Process the Document

```bash
curl -X POST "http://localhost:8002/api/v1/pipeline/process" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "testclient",
    "project_id": "testproject"
  }'
```

### 3. Monitor Progress

```bash
# Get job ID from previous response, then:
curl http://localhost:8002/api/v1/pipeline/status/YOUR_JOB_ID

# Or check Celery Flower dashboard
open http://localhost:5555
```

### 4. Query Results

```bash
# Search for entities
curl "http://localhost:8002/api/v1/entities/search?q=your_search_term"

# Query Neo4j directly
curl -X POST "http://localhost:8002/api/v1/graph/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "MATCH (n:Entity) RETURN count(n) as total_entities"
  }'
```

## 🔍 Monitoring and Debugging

### Service Logs

```bash
# View all service logs
docker-compose -f docker-compose.local.yml logs

# View specific service logs
docker-compose -f docker-compose.local.yml logs app
docker-compose -f docker-compose.local.yml logs celery_app
docker-compose -f docker-compose.local.yml logs minio
```

### Database Access

**Neo4j Browser:**
- URL: http://localhost:7474
- Username: `neo4j`
- Password: `password`

**MinIO Console:**
- URL: http://localhost:9001  
- Username: `minioadmin`
- Password: `minioadmin`

**Celery Flower:**
- URL: http://localhost:5555

### Health Checks

```bash
# Check all services
curl http://localhost:8002/health

# Check MinIO
curl http://localhost:9000/minio/health/live

# Check Neo4j
curl -u neo4j:password http://localhost:7474/db/data/

# Check ChromaDB
curl http://localhost:8001/api/v1/heartbeat
```

## 🛠️ Development

### Running in Development Mode

```bash
# Start only infrastructure services
docker-compose -f docker-compose.local.yml up -d minio neo4j chromadb redis

# Run FastAPI app locally
cd app
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Adding New Pipeline Steps

1. Create new pipeline class in `app/pipelines/pipelines_app.py`
2. Add to `pipeline_operations` mapping
3. Update YAML template in `app/templates/`
4. Test with sample data

### Custom Document Processing

```python
# Example: Add new document parser
from libs.preprocessing_service.document_parsers import register_parser

@register_parser("docx")
class DocxParser:
    def parse_document(self, file_path):
        # Your parsing logic
        pass
```

## 📊 Pipeline Architecture

The pipeline processes documents through these stages:

1. **Document Retrieval** (`GetFiles`) - Fetch from MinIO
2. **Document Parsing** (`ParseDocuments`) - Extract text content  
3. **Text Processing** (`create_base_text_units`) - Chunk into units
4. **Entity Extraction** (`create_base_extracted_entities`) - LLM entity recognition
5. **Entity Summarization** (`create_summarized_entities`) - Deduplicate entities
6. **Graph Construction** (`create_base_entity_graph`) - Build entity graph
7. **Entity Finalization** (`create_final_entities`) - Finalize entity data
8. **Node Creation** (`create_final_nodes`) - Prepare graph nodes
9. **Community Detection** (`create_final_communities`) - Find entity clusters
10. **Relationship Building** (`create_final_relationships`) - Create entity connections
11. **Text Unit Linking** (`create_final_text_units`) - Link text to entities
12. **Community Reports** (`create_final_community_reports`) - Generate summaries
13. **Document Processing** (`create_base_documents`, `create_final_documents`) - Process document metadata
14. **Embedding Generation** (`generate_entity_embeddings`) - Create vector embeddings
15. **Index Creation** (`create_vector_index`, `create_graph_index`) - Setup database indexes
16. **Data Storage** (`store_vector_embeddings`, `store_graph_data`) - Persist to databases

## 🚨 Troubleshooting

### Common Issues

**Services won't start:**
```bash
# Check Docker resources
docker system df
docker system prune

# Restart services
docker-compose -f docker-compose.local.yml down
docker-compose -f docker-compose.local.yml up -d
```

**MinIO connection errors:**
```bash
# Verify MinIO is running
curl http://localhost:9000/minio/health/live

# Check credentials in local.env
cat local.env | grep MINIO
```

**Neo4j connection errors:**
```bash
# Check Neo4j status
docker-compose -f docker-compose.local.yml logs neo4j

# Test connection
curl -u neo4j:password http://localhost:7474/db/data/
```

**Pipeline processing errors:**
```bash
# Check Celery worker logs
docker-compose -f docker-compose.local.yml logs celery_app

# Check task status in Flower
open http://localhost:5555
```

### Performance Tuning

**For large documents:**
- Increase Celery worker memory limits
- Adjust text chunking parameters
- Use batch processing for embeddings

**For better Neo4j performance:**
- Increase Neo4j memory allocation
- Create additional indexes
- Use batch inserts for large graphs

## 📚 Additional Resources

- [Neo4j Cypher Query Language](https://neo4j.com/docs/cypher-manual/current/)
- [MinIO Python SDK](https://min.io/docs/minio/linux/developers/python/minio-py.html)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Celery Documentation](https://docs.celeryproject.org/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.