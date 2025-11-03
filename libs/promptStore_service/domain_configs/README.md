# Domain Configurations for LLM Gateway

This directory contains domain-specific configurations for the Graph Builder's LLM Gateway. These configurations allow you to customize prompts, entity types, relationship types, and examples for different use cases.

## Overview

The Graph Builder uses a flexible configuration system that allows you to:

1. **Use base defaults** - Generic, domain-agnostic settings suitable for general document analysis
2. **Apply domain-specific configs** - Specialized settings for specific domains like resumes, scientific papers, etc.
3. **Create custom configurations** - Define your own domain-specific rules and examples

## Available Configurations

### Base Defaults (`base_defaults.py`)
- **Purpose**: Minimal, generic defaults used when no domain-specific configuration is applied
- **Entity Types**: PERSON, ORGANIZATION, LOCATION, CONCEPT, EVENT, TECHNOLOGY
- **Use Case**: General document analysis, fallback configuration

### Resume Domain (`resume_domain.py`)
- **Purpose**: Optimized for parsing resumes, CVs, and professional profiles
- **Entity Types**: PERSON, ORGANIZATION, LOCATION, TECHNOLOGY, SKILL, CERTIFICATION, EDUCATION, PROJECT
- **Relationship Types**: WORKS_FOR, STUDIED_AT, CERTIFIED_BY, SKILLED_IN, BUILT, USES, etc.
- **Use Case**: HR systems, talent management, professional networking

### General Domain (`general_domain.py`)
- **Purpose**: Comprehensive configuration for general document analysis
- **Entity Types**: PERSON, ORGANIZATION, LOCATION, CONCEPT, EVENT, TECHNOLOGY, DOCUMENT, TOPIC
- **Relationship Types**: AFFILIATED_WITH, LOCATED_IN, COLLABORATES_WITH, INFLUENCES, etc.
- **Use Case**: Research documents, news articles, policy papers, business reports

### Scientific Domain (`scientific_domain.py`)
- **Purpose**: Specialized for scientific papers, research documents, and academic publications
- **Entity Types**: PERSON, ORGANIZATION, CONCEPT, METHOD, DATASET, METRIC, PUBLICATION, EXPERIMENT, HYPOTHESIS, THEORY
- **Relationship Types**: AUTHORED_BY, PUBLISHED_IN, EVALUATED_ON, COMPARED_WITH, BASED_ON, VALIDATES, REFUTES, etc.
- **Use Case**: Academic research, literature reviews, scientific analysis

### Legal Domain (`legal_domain.py`)
- **Purpose**: Optimized for legal documents, contracts, court cases, and regulatory texts
- **Entity Types**: PERSON, ORGANIZATION, LOCATION, LEGAL_DOCUMENT, STATUTE, REGULATION, COURT, CASE, CONTRACT, LEGAL_CONCEPT
- **Relationship Types**: SUES, REPRESENTS, GOVERNS, APPLIES_TO, VIOLATES, COMPLIES_WITH, CITES, etc.
- **Use Case**: Legal research, contract analysis, regulatory compliance

### Financial Domain (`financial_domain.py`)
- **Purpose**: Specialized for financial reports, business documents, and market analysis
- **Entity Types**: PERSON, ORGANIZATION, FINANCIAL_INSTRUMENT, METRIC, CURRENCY, MARKET, SECTOR, PRODUCT, SERVICE
- **Relationship Types**: TRADES_AS, REPORTED, UPGRADED, ACQUIRED, COMPETES_WITH, OPERATES_IN, etc.
- **Use Case**: Financial analysis, market research, business intelligence

### News Domain (`news_domain.py`)
- **Purpose**: Optimized for news articles, press releases, and media reports
- **Entity Types**: PERSON, ORGANIZATION, LOCATION, EVENT, TOPIC, MEDIA_OUTLET, PUBLICATION, QUOTE, STATISTIC, POLICY
- **Relationship Types**: ANNOUNCED, REPORTED, QUOTED, CRITICIZED, PRAISED, OCCURRED_IN, CAUSED, etc.
- **Use Case**: News analysis, media monitoring, event tracking

## Usage Examples

### 1. Using Pre-configured Domains

```python
from backend.libs.llm_service.gateway import LLMGateway
from backend.libs.promptStore_service.domain_configs import configure_resume_domain, configure_general_domain

# Configure for resume parsing
gateway = LLMGateway()
gateway = configure_resume_domain(gateway)

# Configure for general document analysis
gateway = LLMGateway()
gateway = configure_general_domain(gateway)
```

### 2. Manual Configuration

```python
from backend.libs.llm_service.gateway import LLMGateway
from backend.libs.promptStore_service.domain_configs import RESUME_DOMAIN_CONFIG

gateway = LLMGateway()
gateway.configure_domain_defaults(RESUME_DOMAIN_CONFIG)
```

### 3. Creating Custom Domain Configuration

```python
# Define custom configuration for scientific papers
scientific_config = {
    "extract-entities": {
        "entity_types": "PERSON, ORGANIZATION, CONCEPT, METHOD, DATASET, METRIC, PUBLICATION",
        "normalization_rules": "Use standard scientific naming conventions...",
        "examples": "Example scientific entity extraction..."
    },
    "relationship-extraction": {
        "relationship_types": "AUTHORED_BY, EVALUATED_ON, COMPARED_WITH, BASED_ON",
        "relationship_guidelines": "Scientific relationship guidelines..."
    }
}

gateway = LLMGateway()
gateway.configure_domain_defaults(scientific_config)
```

### 4. Runtime Domain Switching

```python
def get_domain_gateway(document_type: str) -> LLMGateway:
    gateway = LLMGateway()
    
    if document_type == "resume":
        return configure_resume_domain(gateway)
    elif document_type == "research_paper":
        return configure_scientific_domain(gateway)  # Custom function
    else:
        return configure_general_domain(gateway)

# Usage
resume_gateway = get_domain_gateway("resume")
research_gateway = get_domain_gateway("research_paper")
```

## Configuration Structure

Each domain configuration is a dictionary with the following structure:

```python
DOMAIN_CONFIG = {
    "extract-entities": {
        "entity_types": "Comma-separated list of entity types",
        "normalization_rules": "Rules for normalizing entity names",
        "examples": "Detailed examples of entity extraction"
    },
    "relationship-extraction": {
        "entity_types": "Entity types for relationship extraction",
        "relationship_types": "Comma-separated list of relationship types",
        "normalization_rules": "Rules for normalizing relationships",
        "relationship_guidelines": "Guidelines for specific relationship types",
        "examples": "Detailed examples of relationship extraction"
    },
    "claim-extraction": {
        "entity_specs": "Entity types for claim extraction",
        "claim_description": "Description of what claims to extract"
    },
    "entity-merging": {
        "allowed_entity_types": "Types allowed after merging",
        "entity_type_mappings": "Rules for mapping entity types",
        "key_attributes": "Important attributes to preserve"
    }
}
```

## Best Practices

1. **Start with existing domains** - Use `resume_domain.py` or `general_domain.py` as templates
2. **Provide comprehensive examples** - Include detailed, realistic examples in your configurations
3. **Use specific entity types** - Prefer specific types over generic ones (e.g., "CERTIFICATION" vs "CONCEPT")
4. **Define clear relationship guidelines** - Explain when to use each relationship type
5. **Test your configurations** - Validate that your domain config produces expected results
6. **Document your domains** - Add comments explaining the purpose and use cases

## Adding New Domains

To add a new domain configuration:

1. Create a new file: `your_domain.py`
2. Define your configuration dictionary: `YOUR_DOMAIN_CONFIG`
3. Create a convenience function: `configure_your_domain(gateway)`
4. Update `__init__.py` to export your new domain
5. Add usage examples to the examples directory
6. Update this README with your domain information

## API Integration

### Using Domain Configuration via REST API

You can optionally specify the domain when starting a workflow via the REST API:

```bash
# With domain-specific processing
curl -X POST "http://localhost:8002/api/workflow/graph_preprocessing" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "client_id": "testclient",
      "project_id": "testproject", 
      "workflow_id": "graph_preprocessing_001",
      "domain_id": "resume"
    }
  }'

# Without domain (uses base defaults)
curl -X POST "http://localhost:8002/api/workflow/graph_preprocessing" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "client_id": "testclient",
      "project_id": "testproject", 
      "workflow_id": "graph_preprocessing_001"
    }
  }'
```

**Available domain_id values (optional):**
- `"resume"` - Resume/CV parsing
- `"general"` - General document analysis  
- `"scientific"` - Scientific papers and research
- `"legal"` - Legal documents and contracts
- `"financial"` - Financial reports and business docs
- `"news"` - News articles and media content

**If no `domain_id` is specified, the system uses base defaults only.**

### Domain-Specific Processing

When you specify a `domain_id`, the system will:

1. **Configure entity types** - Use domain-specific entity categories
2. **Apply relationship rules** - Use specialized relationship types and guidelines  
3. **Inject examples** - Provide domain-relevant examples to the LLM
4. **Apply normalization** - Use domain-specific naming and formatting rules

For example, with `"domain_id": "resume"`:
- Extracts entities like SKILL, CERTIFICATION, EDUCATION
- Uses relationships like WORKS_FOR, CERTIFIED_BY, SKILLED_IN
- Applies resume-specific normalization rules
- Provides resume parsing examples to guide the LLM

## Integration with Langfuse

After updating domain configurations, run the ingest script to update prompts in Langfuse:

```bash
python backend/scripts/ingest_langfuse_prompts.py
```

This ensures that your domain-specific examples and rules are available in the prompt management system.