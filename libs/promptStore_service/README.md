# Centralized Prompt Store Service

This module provides centralized prompt management using Langfuse, replacing the previous file-based prompt system.

## Overview

The `promptStore_service` module centralizes prompt management by:
- Fetching prompts from Langfuse instead of static `.txt` files
- Providing a unified interface for prompt retrieval and formatting
- Supporting caching and batch operations
- Maintaining backward compatibility with existing GraphRAG workflows

## Migration from File-based Prompts

The system has been migrated from static prompt files to Langfuse-based management:

### Before (File-based)
```
backend/libs/llm_service/prompts/
├── entity_extraction.txt
├── relationship_extraction.txt
├── community_report.txt
├── summarize_descriptions.txt
├── claim_extraction.txt
├── duplicate_detection.txt
└── entity_merging.txt
```

### After (Langfuse-based)
```
backend/libs/promptStore_service/
├── __init__.py
├── prompt_manager.py
└── README.md
```

## Usage

### Basic Usage
```python
from libs.promptStore_service import get_default_langfuse_prompt_manager

# Get the prompt manager
manager = get_default_langfuse_prompt_manager()

# Format a prompt with variables
formatted_prompt = manager.get_entity_extraction_prompt(
    input_text="John Smith works at Microsoft.",
    entity_types=["PERSON", "ORGANIZATION"]
)
```

### Integration with LLMGateway
The `LLMGateway` automatically uses the new prompt manager:

```python
from libs.llm_service.gateway import LLMGateway

gateway = LLMGateway()  # Uses Langfuse prompts by default

# Entity extraction
result = await gateway.entity_extraction(
    input_text="John Smith works at Microsoft.",
    entity_types=["PERSON", "ORGANIZATION"]
)
```

## Configuration

Ensure these environment variables are set in `backend/local.env`:

```env
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=http://localhost:3000
```

## Prompt Types

The following prompt types are supported:

- `entity-extraction`: Extract entities from text
- `relationship-extraction`: Extract relationships between entities
- `community-report`: Generate community summaries
- `summarize-descriptions`: Summarize entity descriptions
- `claim-extraction`: Extract claims from text
- `duplicate-detection`: Detect duplicate entities
- `entity-merging`: Merge similar entities

## Testing

Run the migration test script to verify everything is working:

```bash
python backend/scripts/migrate_to_langfuse_prompts.py
```

Run the LLMGateway integration test:

```bash
python backend/scripts/test_llm_gateway_langfuse.py
```

## Architecture

```
LLMGateway
    ↓
LangfusePromptManager
    ↓
LangfusePromptSource
    ↓
Langfuse API
```

The system provides:
- **Caching**: Prompts are cached locally to reduce API calls
- **Error handling**: Graceful fallback and error reporting
- **Batch operations**: Efficient loading of multiple prompts
- **Flexibility**: Easy to extend with new prompt sources

## Backward Compatibility

The old `GraphRAGPromptManager` is still available for existing tests and legacy code, but all new development should use the `LangfusePromptManager`.

## Troubleshooting

1. **Connection issues**: Verify Langfuse environment variables
2. **Missing prompts**: Ensure prompts exist in Langfuse with "production" label
3. **Permission errors**: Check API key permissions in Langfuse

For more details, see the migration and test scripts in `backend/scripts/`.