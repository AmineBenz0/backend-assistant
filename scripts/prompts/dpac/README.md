# Language-Based Prompt Management for D.PaC

This directory contains language-specific prompts for the D.PaC (Digitalizzazione Patrimonio Culturale) project.

## Directory Structure

```
scripts/prompts/dpac/
├── en/          # English prompts
│   ├── run_graph_rag.txt
│   ├── out_of_context_detection.txt
│   ├── nl2cypher.txt
│   └── ...
└── it/          # Italian prompts
    ├── run_graph_rag.txt
    ├── out_of_context_detection.txt
    ├── nl2cypher.txt
    └── ...
```

## How It Works

### 1. Prompt Organization

- **English prompts**: Located in `scripts/prompts/dpac/en/`
- **Italian prompts**: Located in `scripts/prompts/dpac/it/`

Each language directory contains the same set of prompt files, translated to the respective language.

### 2. Ingesting Prompts to Langfuse

Use the `ingest_langfuse_prompts.py` script with the `--language` flag:

```bash
# Ingest English prompts
python scripts/ingest_langfuse_prompts.py --language en

# Ingest Italian prompts
python scripts/ingest_langfuse_prompts.py --language it
```

This will:
- Load prompts from the respective language directory
- Add a language suffix to the prompt name (e.g., `run-graph-rag-en`, `run-graph-rag-it`)
- Tag the prompt with the language in the config metadata

### 3. Automatic Language Routing

The `LangfusePromptManager` in `libs/promptStore_service/prompt_manager.py` automatically routes to the correct language-specific prompt based on the `language` variable:

```python
# Example: Automatic routing to Italian prompt
prompt_manager.get_formatted_prompt("run-graph-rag", {
    "input_text": "Cos'è D.PaC?",
    "language": "it",  # This triggers routing to "run-graph-rag-it"
    "references": "...",
    "user_facts": "..."
})
```

**Language Detection:**
- The system checks the `language` variable in the prompt variables
- Supported values: `"en"`, `"english"`, `"it"`, `"italian"`, `"italiano"`
- If a language-specific prompt exists (e.g., `run-graph-rag-it`), it will be used
- If not found, falls back to the default prompt without language suffix

### 4. Domain Configuration Integration

The language routing works seamlessly with domain configurations:

```python
# Domain configs can specify language
domain_id = "it_dpac"  # Italian D.PaC domain

# The prompt manager will use Italian prompts automatically
prompt = prompt_manager.get_formatted_prompt(
    "out-of-context-detection",
    {
        "input_text": "Domanda in italiano",
        "language": "it",
        "topics": ["..."]
    },
    domain_id=domain_id
)
```

## Adding New Language-Specific Prompts

### Step 1: Create the Prompt Files

1. Add your prompt to both language directories:
   - `scripts/prompts/dpac/en/my_new_prompt.txt`
   - `scripts/prompts/dpac/it/my_new_prompt.txt`

2. Ensure both versions have the same structure and variables

### Step 2: Ingest to Langfuse

```bash
# Ingest English version
python scripts/ingest_langfuse_prompts.py --language en

# Ingest Italian version
python scripts/ingest_langfuse_prompts.py --language it
```

### Step 3: Use in Code

```python
# The prompt manager will automatically route based on language
prompt = prompt_manager.get_formatted_prompt("my-new-prompt", {
    "variable1": "value1",
    "language": "it"  # Routes to "my-new-prompt-it"
})
```

## Key Prompts Translated

The following critical prompts have been translated to Italian:

- `run_graph_rag.txt` - Main RAG inference prompt
- `out_of_context_detection.txt` - Topic classification
- `sensitive_topics_detection.txt` - Sensitive topic detection
- `nl2cypher.txt` - Natural language to Cypher translation
- `query_rewriting.txt` - Query rewriting
- `query_expansion.txt` - Query expansion

## Benefits

1. **Automatic Routing**: No need to manually specify which prompt to use
2. **Fallback Support**: If a language-specific prompt doesn't exist, falls back to default
3. **Consistent Interface**: Same API for all languages
4. **Easy Maintenance**: Add new languages by creating new directories
5. **Domain Integration**: Works seamlessly with existing domain configurations

## Migration Notes

### Before (Old Approach)
```python
# Language was injected into the prompt template
prompt = template.format(language="Italian")
# Result: "Always answer in language Italian"
```

### After (New Approach)
```python
# Language routes to Italian-specific prompt
prompt = manager.get_formatted_prompt("run-graph-rag", {
    "language": "it",
    # ... other variables
})
# Result: Uses "run-graph-rag-it" which is already in Italian
```

## Troubleshooting

### Prompt Not Found Error

If you get an error like `Prompt 'run-graph-rag-it' not found`:

1. Check that you've ingested the Italian prompts:
   ```bash
   python scripts/ingest_langfuse_prompts.py --language it
   ```

2. Verify the prompt file exists:
   ```bash
   ls scripts/prompts/dpac/it/run_graph_rag.txt
   ```

3. Check Langfuse UI to confirm the prompt was created with the correct name

### Fallback to English

If Italian prompts aren't found, the system will automatically fall back to English prompts. Check the logs for warnings like:
```
[WARNING] Language-specific prompt 'prompt-name-it' not found, falling back to default
```

## Future Enhancements

- Add support for more languages (e.g., French, Spanish)
- Implement language detection from user input
- Add language-specific domain configurations
- Create automated translation workflows
