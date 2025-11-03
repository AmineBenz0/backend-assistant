"""
General-purpose domain configuration for Graph Builder.

This module provides generic, domain-agnostic defaults suitable for
general document analysis and knowledge graph construction.
"""

from typing import Dict, Any

# General-purpose domain configuration
GENERAL_DOMAIN_CONFIG: Dict[str, Dict[str, Any]] = {
    "extract-entities": {
        "entity_types": "PERSON, ORGANIZATION, LOCATION, CONCEPT, EVENT, TECHNOLOGY, DOCUMENT, TOPIC",
        "normalization_rules": """General entity normalization rules:
- Use consistent capitalization for entity names
- Prefer full official names over abbreviations when possible
- Group similar concepts under canonical forms
- Use specific entity types rather than generic ones when applicable
- Maintain consistency in naming conventions across the document
- Standardize organization names to their official forms
- Use proper nouns for specific locations, concepts, and technologies
- Distinguish between general concepts and specific implementations""",
        "examples": """General Entity Extraction Examples:

Example 1 - Research and Policy Document:
Text: "The World Health Organization published a comprehensive report on climate change impacts in 2023. Dr. Sarah Chen from Stanford University contributed to the research on renewable energy technologies, focusing on solar panel efficiency improvements. The European Union has implemented new regulations based on these findings."
Output:
("entity"|World Health Organization|ORGANIZATION|International health agency under the United Nations)
("entity"|climate change|CONCEPT|Long-term shifts in global temperatures and weather patterns)
("entity"|Dr. Sarah Chen|PERSON|Researcher at Stanford University specializing in renewable energy)
("entity"|Stanford University|ORGANIZATION|Private research university in California)
("entity"|renewable energy|CONCEPT|Energy from sources that are naturally replenishing)
("entity"|solar panel|TECHNOLOGY|Device that converts sunlight into electricity)
("entity"|European Union|ORGANIZATION|Political and economic union of European countries)
("entity"|2023|EVENT|Year when the WHO report was published)
("relationship"|World Health Organization|climate change|WHO published comprehensive report on climate change impacts|0.9)
("relationship"|Dr. Sarah Chen|Stanford University|Dr. Sarah Chen is affiliated with Stanford University as researcher|0.9)
("relationship"|Dr. Sarah Chen|renewable energy|Dr. Sarah Chen conducts research on renewable energy technologies|0.8)
("relationship"|Dr. Sarah Chen|solar panel|Dr. Sarah Chen focuses on solar panel efficiency improvements|0.8)
("relationship"|European Union|climate change|EU implemented regulations based on climate change research|0.7)

Example 2 - Technology and Business Document:
Text: "Microsoft Corporation announced a partnership with OpenAI to integrate artificial intelligence capabilities into Microsoft Office suite. The collaboration aims to enhance productivity tools using large language models like GPT-4. This initiative is part of Microsoft's broader digital transformation strategy for enterprise customers."
Output:
("entity"|Microsoft Corporation|ORGANIZATION|American multinational technology corporation)
("entity"|OpenAI|ORGANIZATION|AI research and deployment company)
("entity"|artificial intelligence|CONCEPT|Machine intelligence and automated reasoning)
("entity"|Microsoft Office|TECHNOLOGY|Suite of productivity applications)
("entity"|large language models|CONCEPT|AI models trained on vast amounts of text data)
("entity"|GPT-4|TECHNOLOGY|Generative pre-trained transformer language model)
("entity"|digital transformation|CONCEPT|Integration of digital technology into business operations)
("entity"|enterprise customers|CONCEPT|Large business and organizational clients)
("relationship"|Microsoft Corporation|OpenAI|Microsoft announced partnership with OpenAI|0.9)
("relationship"|Microsoft Corporation|artificial intelligence|Microsoft integrates AI capabilities into products|0.8)
("relationship"|OpenAI|artificial intelligence|OpenAI develops artificial intelligence technologies|0.9)
("relationship"|Microsoft Office|artificial intelligence|AI capabilities integrated into Office suite|0.8)
("relationship"|GPT-4|large language models|GPT-4 is an example of large language models|0.9)
("relationship"|Microsoft Corporation|digital transformation|Microsoft pursues digital transformation strategy|0.7)"""
    },
    "relationship-extraction": {
        "entity_types": "PERSON, ORGANIZATION, LOCATION, CONCEPT, EVENT, TECHNOLOGY, DOCUMENT, TOPIC",
        "relationship_types": "AFFILIATED_WITH, LOCATED_IN, RELATED_TO, PART_OF, CREATED_BY, PUBLISHED_BY, RESEARCHES, COLLABORATES_WITH, INFLUENCES, CONTAINS, IMPLEMENTS, DEVELOPS, ANNOUNCES, FOCUSES_ON, BASED_ON",
        "normalization_rules": """General relationship normalization rules:
- Use specific relationship types when the connection is clear and well-defined
- Prefer RELATED_TO only when no more specific relationship applies
- Ensure relationships capture the directionality when relevant
- Use consistent relationship types across similar contexts
- Consider temporal aspects of relationships when mentioned""",
        "relationship_guidelines": """General relationship guidelines:
- AFFILIATED_WITH: Professional, organizational, or institutional relationships
- LOCATED_IN: Geographic, spatial, or containment relationships
- RELATED_TO: General conceptual or thematic relationships when no specific type applies
- PART_OF: Hierarchical, compositional, or membership relationships
- CREATED_BY/PUBLISHED_BY: Authorship, creation, or publication relationships
- RESEARCHES/FOCUSES_ON: Academic, research, or specialization relationships
- COLLABORATES_WITH: Partnership, cooperation, or joint effort relationships
- INFLUENCES: Causal, impact, or effect relationships
- CONTAINS: Content, inclusion, or composition relationships
- IMPLEMENTS: Policy, strategy, or system implementation relationships
- DEVELOPS: Creation, innovation, or development relationships
- ANNOUNCES: Communication, declaration, or announcement relationships
- BASED_ON: Foundation, derivation, or source relationships""",
        "examples": """General Relationship Extraction Examples:

Example 1 - Policy and Regulation Document:
Text: "The European Union implemented comprehensive regulations on artificial intelligence in 2024, following recommendations from the AI Ethics Committee. The policy framework was developed by a joint committee including experts from Germany, France, and the Netherlands. These regulations influence how technology companies like Google and Microsoft develop AI systems."
Output:
("entity"|European Union|ORGANIZATION|Political and economic union of 27 European countries)
("entity"|artificial intelligence|CONCEPT|Machine intelligence and automated decision-making systems)
("entity"|AI Ethics Committee|ORGANIZATION|Advisory body for AI governance and ethics)
("entity"|policy framework|DOCUMENT|Structured set of regulations and guidelines)
("entity"|joint committee|ORGANIZATION|Multi-national expert advisory group)
("entity"|Germany|LOCATION|European country and EU member state)
("entity"|France|LOCATION|European country and EU member state)
("entity"|Netherlands|LOCATION|European country and EU member state)
("entity"|Google|ORGANIZATION|American multinational technology corporation)
("entity"|Microsoft|ORGANIZATION|American multinational technology corporation)
("entity"|2024|EVENT|Year when AI regulations were implemented)
("relationship"|European Union|artificial intelligence|IMPLEMENTS|EU implemented comprehensive AI regulations|0.9)
("relationship"|AI Ethics Committee|European Union|AFFILIATED_WITH|AI Ethics Committee provides recommendations to EU|0.8)
("relationship"|joint committee|policy framework|CREATED_BY|Joint committee developed the policy framework|0.9)
("relationship"|Germany|joint committee|PART_OF|Germany provided experts to joint committee|0.8)
("relationship"|France|joint committee|PART_OF|France provided experts to joint committee|0.8)
("relationship"|Netherlands|joint committee|PART_OF|Netherlands provided experts to joint committee|0.8)
("relationship"|artificial intelligence|Google|INFLUENCES|AI regulations influence how Google develops AI systems|0.7)
("relationship"|artificial intelligence|Microsoft|INFLUENCES|AI regulations influence how Microsoft develops AI systems|0.7)

Example 2 - Research and Innovation Document:
Text: "Stanford University's AI Research Lab, led by Dr. Jennifer Martinez, announced breakthrough developments in quantum machine learning. The research, published in Nature, demonstrates how quantum computing can accelerate neural network training. This work builds on previous studies from MIT and collaborates with IBM's quantum computing division."
Output:
("entity"|Stanford University|ORGANIZATION|Private research university in California)
("entity"|AI Research Lab|ORGANIZATION|Artificial intelligence research division at Stanford)
("entity"|Dr. Jennifer Martinez|PERSON|Research scientist and lab director)
("entity"|quantum machine learning|CONCEPT|Intersection of quantum computing and machine learning)
("entity"|Nature|ORGANIZATION|International scientific journal)
("entity"|quantum computing|TECHNOLOGY|Computing technology using quantum mechanical phenomena)
("entity"|neural network training|CONCEPT|Process of teaching artificial neural networks)
("entity"|MIT|ORGANIZATION|Massachusetts Institute of Technology)
("entity"|IBM|ORGANIZATION|International technology and consulting corporation)
("relationship"|AI Research Lab|Stanford University|PART_OF|AI Research Lab is part of Stanford University|0.9)
("relationship"|Dr. Jennifer Martinez|AI Research Lab|AFFILIATED_WITH|Dr. Martinez leads the AI Research Lab|0.9)
("relationship"|Dr. Jennifer Martinez|quantum machine learning|RESEARCHES|Dr. Martinez conducts research in quantum machine learning|0.8)
("relationship"|Dr. Jennifer Martinez|Nature|PUBLISHED_BY|Research was published in Nature journal|0.8)
("relationship"|quantum computing|neural network training|INFLUENCES|Quantum computing can accelerate neural network training|0.8)
("relationship"|Stanford University|MIT|COLLABORATES_WITH|Stanford research builds on previous MIT studies|0.7)
("relationship"|Stanford University|IBM|COLLABORATES_WITH|Stanford collaborates with IBM's quantum division|0.8)"""
    },
    "claim-extraction": {
        "entity_specs": "PERSON, ORGANIZATION, CONCEPT, EVENT, TECHNOLOGY, DOCUMENT, LOCATION",
        "claim_description": """General claims to extract from documents:
- Factual statements and assertions about entities
- Research findings and scientific discoveries
- Policy decisions and regulatory announcements
- Business developments and strategic initiatives
- Technological innovations and breakthroughs
- Performance metrics and statistical data
- Causal relationships and impact assessments
- Future predictions and trend analyses
- Expert opinions and professional assessments
- Historical events and timeline information"""
    },
    "entity-merging": {
        "allowed_entity_types": "PERSON, ORGANIZATION, LOCATION, CONCEPT, EVENT, TECHNOLOGY, DOCUMENT, TOPIC",
        "entity_type_mappings": """General entity type mappings:
- COMPANY/CORPORATION/ENTERPRISE/FIRM → ORGANIZATION
- CITY/COUNTRY/REGION/STATE/PROVINCE → LOCATION  
- IDEA/THEORY/PRINCIPLE/METHODOLOGY → CONCEPT
- SOFTWARE/HARDWARE/SYSTEM/PLATFORM/TOOL → TECHNOLOGY
- REPORT/STUDY/PAPER/PUBLICATION/ARTICLE → DOCUMENT
- CONFERENCE/MEETING/SUMMIT/WORKSHOP → EVENT
- FIELD/DOMAIN/DISCIPLINE/AREA → TOPIC""",
        "key_attributes": """General key attributes to preserve:
- Names, titles, and official designations
- Geographic locations and addresses
- Temporal information (dates, durations, timelines)
- Quantitative data (metrics, statistics, measurements)
- Qualitative descriptions and characteristics
- Relationships and affiliations
- Roles and responsibilities
- Status and classifications
- Performance indicators and outcomes
- Sources and references"""
    }
}

def configure_general_domain(gateway):
    """Configure the LLMGateway for general-purpose document analysis."""
    gateway.configure_domain_defaults(GENERAL_DOMAIN_CONFIG)
    return gateway