# VectorRAG Backend Pipeline

A comprehensive VectorRAG (Vector Retrieval-Augmented Generation) pipeline that processes documents and enables vector-based search and inference.

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

### Process Documents (Vector Preprocessing Pipeline)

**Endpoint:** `POST /api/workflow/vector_preprocessing`

**Request Body:**
```json
{
  "workflow_id": "preprocessing_001",
  "input": {
    "client_id": "testclient",
    "project_id": "testproject",
    "language": "en",
    "embedding_model": "text-embedding-3-large",
    "embedding_provider": "azure_openai",
    "embedding_batch_size": 100
  }
}
```

**Example using curl:**
```bash
curl -X POST "http://localhost:8002/api/workflow/vector_preprocessing" \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_id": "preprocessing_001",
    "input": {
      "client_id": "testclient",
      "project_id": "testproject",
      "language": "en",
      "embedding_model": "text-embedding-3-large",
      "embedding_provider": "azure_openai",
      "embedding_batch_size": 100
    }
  }'
```

**Response:**
```json
{
  "workflow_id": "preprocessing_001",
  "tasks": [
    {
      "step_name": "GetFiles",
      "pipeline_key": "GetFiles",
      "task_id": "abc123...",
      "queue": "localAPI_queue",
      "status": "PENDING"
    },
    {
      "step_name": "parse_documents",
      "pipeline_key": "ParseDocuments",
      "task_id": "def456...",
      "queue": "localAPI_queue",
      "status": "PENDING"
    },
    {
      "step_name": "chunk_documents",
      "pipeline_key": "chunk_documents",
      "task_id": "ghi789...",
      "queue": "localAPI_queue",
      "status": "PENDING"
    },
    {
      "step_name": "generate_embeddings",
      "pipeline_key": "GenerateChunkEmbeddings",
      "task_id": "jkl012...",
      "queue": "localAPI_queue",
      "status": "PENDING"
    },
    {
      "step_name": "store_chunks_in_vector_db",
      "pipeline_key": "StoreChunksInVectorDB",
      "task_id": "mno345...",
      "queue": "localAPI_queue",
      "status": "PENDING"
    },
    {
      "step_name": "save_mapping_to_document_db",
      "pipeline_key": "save_mapping_to_document_db",
      "task_id": "pqr678...",
      "queue": "localAPI_queue",
      "status": "PENDING"
    }
  ]
}
```

### Chat Workflow (Vector Inference Pipeline)

**Endpoint:** `POST /api/chat/vector_inference`

**Request Body:**
```json
{
  "workflow_id": "inference_001",
  "input": {
    "client_id": "testclient",
    "project_id": "testproject",
    "session_id": "session123",
    "user_id": "user456",
    "input_text": "What is the main topic?",
    "top_k": 5,
    "limit": 10,
    "language": "en"
  }
}
```

**Example using curl:**
```bash
curl -X POST "http://localhost:8002/api/chat/vector_inference" \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_id": "inference_001",
    "input": {
      "client_id": "testclient",
      "project_id": "testproject",
      "session_id": "session123",
      "user_id": "user456",
      "input_text": "What is the main topic?",
      "top_k": 5,
      "limit": 10,
      "language": "en"
    }
  }'
```

### Check Job Status

**Endpoint:** `GET /api/results/{task_id}`

```bash
curl http://localhost:8002/api/results/YOUR_TASK_ID
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
curl -X POST "http://localhost:8002/api/workflow/vector_preprocessing" \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_id": "preprocessing_001",
    "input": {
      "client_id": "testclient",
      "project_id": "testproject",
      "language": "en"
    }
  }'
```

### 3. Monitor Progress

```bash
# Get task ID from previous response, then:
curl http://localhost:8002/api/results/YOUR_TASK_ID

# Or check Celery Flower dashboard
open http://localhost:5555
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

# Check ChromaDB
curl http://localhost:8001/api/v1/heartbeat
```

## 🛠️ Development

### Running in Development Mode

```bash
# Start only infrastructure services
docker-compose -f docker-compose.local.yml up -d minio chromadb redis

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

The vector preprocessing pipeline processes documents through these stages:

1. **Document Retrieval** (`GetFiles`) - Fetch from MinIO
2. **Document Parsing** (`ParseDocuments`) - Extract text content  
3. **Document Chunking** (`chunk_documents`) - Split documents into chunks
4. **Embedding Generation** (`GenerateChunkEmbeddings`) - Create vector embeddings
5. **Vector Storage** (`StoreChunksInVectorDB`) - Store chunks in ChromaDB
6. **Document Mapping** (`save_mapping_to_document_db`) - Save metadata to Elasticsearch

The vector inference pipeline handles queries through these stages:

1. **User Message** (`save_user_message`) - Save user input
2. **User Facts** (`fetch_user_facts`, `extract_user_facts`) - Extract user context
3. **Vector Search** (`search_relevant_chunks`) - Find relevant chunks
4. **Vector References** (`GetVectorReference`) - Get reference metadata
5. **Chat History** (`fetch_chat_history`) - Retrieve conversation context
6. **RAG Generation** (`run-vector-rag`) - Generate response using LLM
7. **Response Combination** (`combine_vector_response_and_references`) - Combine results
8. **Message Storage** (`save_vector_llm_message`) - Save LLM response

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

## 📚 Additional Resources

- [MinIO Python SDK](https://min.io/docs/minio/linux/developers/python/minio-py.html)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [ChromaDB Documentation](https://docs.trychroma.com/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
