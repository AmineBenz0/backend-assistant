"""
Base default configurations for the LLM Gateway.

This module contains the core default values that are used when no domain-specific
configuration is provided. These are minimal, generic defaults.
"""

from typing import Dict, Any

# Base minimal defaults - domain-agnostic
BASE_DEFAULTS_MAP: Dict[str, Dict[str, Any]] = {
    "extract-entities": {
        "entity_types": "PERSON, ORGANIZATION, LOCATION, CONCEPT, EVENT, TECHNOLOGY",
        "max_entities": "20",
        "language": "English",
        "tuple_delimiter": "|",
        "record_delimiter": "##",
        "completion_delimiter": "<|COMPLETE|>",
        "normalization_rules": "- Use consistent capitalization for entity names\n- Prefer full official names over abbreviations\n- Group similar entities under canonical forms",
        "examples": "Example 1:\nText: \"The research team at Stanford University published a paper on artificial intelligence in Nature journal.\"\nOutput:\n(\"entity\"|Stanford University|ORGANIZATION|Academic research institution)\n(\"entity\"|artificial intelligence|CONCEPT|Field of computer science)\n(\"entity\"|Nature journal|ORGANIZATION|Scientific publication)\n(\"relationship\"|Stanford University|artificial intelligence|RESEARCHES|Stanford University conducts research in artificial intelligence|0.8)"
    },
    "relationship-extraction": {
        "entity_types": "PERSON, ORGANIZATION, LOCATION, CONCEPT, EVENT, TECHNOLOGY",
        "relationship_types": "RELATED_TO, LOCATED_IN, CREATES, PART_OF, COLLABORATES_WITH, OWNS, FOUNDED, ACQUIRED, PARTNERED_WITH, COMPETED_WITH, INVESTED_IN, PUBLISHED, CONTRIBUTED_TO, MEMBER_OF, AFFILIATED_WITH, ASSOCIATED_WITH, CONNECTED_TO, INFLUENCES, SUPPORTS, OPPOSES",
        "language": "English",
        "tuple_delimiter": "|",
        "record_delimiter": "##",
        "completion_delimiter": "<|COMPLETE|>",
        "normalization_rules": "- Use consistent relationship types from the allowed list\n- Ensure relationships capture the full context\n- Prefer specific relationship types over generic RELATED_TO\n- Create multiple relationships for complex connections\n- Include both direct and indirect relationships\n- Consider temporal aspects of relationships",
        "relationship_guidelines": "- Extract meaningful relationships between entities\n- Focus on clear, factual connections\n- Avoid speculative or implied relationships\n- Include organizational and geographical relationships\n- Capture collaboration and partnership relationships\n- Consider both current and historical relationships",
        "examples": "Example 1:\nText: \"Microsoft Corporation, founded by Bill Gates, is headquartered in Redmond, Washington. The company collaborates with OpenAI on artificial intelligence research and has invested in renewable energy projects.\"\nOutput:\n(\"entity\"|Microsoft Corporation|ORGANIZATION|Technology company)\n(\"entity\"|Bill Gates|PERSON|Co-founder of Microsoft)\n(\"entity\"|Redmond|LOCATION|City in Washington state)\n(\"entity\"|Washington|LOCATION|US state)\n(\"entity\"|OpenAI|ORGANIZATION|AI research company)\n(\"entity\"|artificial intelligence|CONCEPT|Field of computer science)\n(\"entity\"|renewable energy|CONCEPT|Sustainable energy sources)\n(\"relationship\"|Bill Gates|Microsoft Corporation|FOUNDED|Bill Gates co-founded Microsoft Corporation|0.9)\n(\"relationship\"|Microsoft Corporation|Redmond|LOCATED_IN|Microsoft is headquartered in Redmond|0.9)\n(\"relationship\"|Redmond|Washington|LOCATED_IN|Redmond is located in Washington state|0.9)\n(\"relationship\"|Microsoft Corporation|OpenAI|COLLABORATES_WITH|Microsoft collaborates with OpenAI|0.8)\n(\"relationship\"|Microsoft Corporation|artificial intelligence|RESEARCHES|Microsoft conducts AI research through OpenAI partnership|0.7)\n(\"relationship\"|Microsoft Corporation|renewable energy|INVESTED_IN|Microsoft has invested in renewable energy projects|0.8)"
    },
    "community-report": {
        "language": "English"
    },
    "summarize-descriptions": {
        "language": "English"
    },
    "claim-extraction": {
        "language": "English",
        "entity_specs": "PERSON, ORGANIZATION, LOCATION, TECHNOLOGY, CONCEPT",
        "claim_description": "Any factual statement, assertion, or claim made about the specified entities"
    },
    "duplicate-detection": {
        "confidence_threshold": "0.8"
    },
    "entity-merging": {
        "language": "English",
        "allowed_entity_types": "PERSON, ORGANIZATION, LOCATION, TECHNOLOGY, CONCEPT, EVENT",
        "entity_type_mappings": "Use appropriate mappings based on context",
        "key_attributes": "names, locations, descriptions, types, affiliations"
    },
    "entity-normalization": {
        "entity_types": "PERSON, ORGANIZATION, LOCATION, TECHNOLOGY, CONCEPT, EVENT",
        "normalization_rules": """Generic entity normalization rules:
- Use full official names over abbreviations
- Maintain consistent capitalization and formatting
- Preserve important distinguishing information
- Group similar entities under canonical forms
- Use standard naming conventions for each entity type""",
        "language": "English",
        "entities": "[]",
        "relationships": "[]"
    },
    "nl2cypher": { 
        "schema": """
            (PERSON)-[:WORKS_FOR]->(ORGANIZATION)
            (PERSON)-[:CERTIFIED_BY]->(ORGANIZATION)
            (PERSON)-[:CREATES]->(TECHNOLOGY)
            (TECHNOLOGY)-[:USES]->(TECHNOLOGY)
            (ORGANIZATION)-[:LOCATED_IN]->(ORGANIZATION)
            (ORGANIZATION)-[:LOCATED_IN]->(LOCATION)
            (PERSON)-[:STUDIED_AT]->(ORGANIZATION)
            (PERSON)-[:LEADS]->(ORGANIZATION)
        """, 
        "example": """
            {
                "input_text": "where did Zakaria Hamane work ?",
                "cypher": "MATCH (p:PERSON {{name: 'Zakaria Hamane'}})-[:WORKS_FOR]->(o:ORGANIZATION)\nRETURN apoc.map.removeKey(properties(o), 'description_embedding') AS organization",
                "explanation": "This query finds the organizations where 'Zakaria Hamane' has worked and returns all attributes of the organization except the 'description_embedding' property. The APOC function `apoc.map.removeKey` is used to filter out that specific property from the result.",
                "confidence_score": 0.98
            }
        """
    }
}