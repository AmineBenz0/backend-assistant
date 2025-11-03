"""
News and media domain configuration for Graph Builder.

This module provides domain-specific defaults for news articles,
press releases, media reports, and journalistic content.
"""

from typing import Dict, Any

# News and media domain configuration
NEWS_DOMAIN_CONFIG: Dict[str, Dict[str, Any]] = {
    "extract-entities": {
        "entity_types": "PERSON, ORGANIZATION, LOCATION, EVENT, TOPIC, MEDIA_OUTLET, PUBLICATION, QUOTE, STATISTIC, POLICY, INCIDENT",
        "normalization_rules": """News entity normalization rules:
- Use full names for public figures and officials
- Use official organization and institution names
- Standardize location names to proper geographic designations
- Use specific event names and dates when available
- Normalize media outlet names to their official brands
- Use proper titles and roles for quoted individuals
- Standardize policy and legislation names
- Use specific incident classifications when applicable""",
        "examples": """News Entity Extraction Examples:

Example 1 - Political News Article:
Text: "President Joe Biden announced new climate policies during a speech at the White House on Tuesday, targeting a 50% reduction in carbon emissions by 2030. Environmental groups like the Sierra Club praised the initiative, while Republican Senator Ted Cruz criticized the plan as 'economically damaging.' The announcement comes ahead of the UN Climate Summit in Glasgow."
Output:
("entity"|Joe Biden|PERSON|46th President of the United States)
("entity"|President|PERSON|Official title and role)
("entity"|White House|LOCATION|Official residence and workplace of US President)
("entity"|Tuesday|EVENT|Day of the week when announcement was made)
("entity"|climate policies|POLICY|Environmental regulations and initiatives)
("entity"|50% reduction|STATISTIC|Target percentage for carbon emissions reduction)
("entity"|carbon emissions|TOPIC|Greenhouse gas emissions from human activities)
("entity"|2030|EVENT|Target year for emissions reduction goal)
("entity"|Sierra Club|ORGANIZATION|Environmental advocacy organization)
("entity"|Ted Cruz|PERSON|Republican Senator from Texas)
("entity"|Republican Senator|PERSON|Political party and role designation)
("entity"|UN Climate Summit|EVENT|International climate change conference)
("entity"|Glasgow|LOCATION|City in Scotland hosting climate summit)
("relationship"|Joe Biden|President|HOLDS_TITLE|Joe Biden holds the title of President|0.9)
("relationship"|Joe Biden|White House|ANNOUNCED_AT|Biden announced policies at White House|0.9)
("relationship"|Joe Biden|climate policies|ANNOUNCED|Biden announced new climate policies|0.9)
("relationship"|climate policies|50% reduction|TARGETS|Climate policies target 50% emissions reduction|0.8)
("relationship"|Sierra Club|climate policies|PRAISED|Sierra Club praised the climate initiative|0.8)
("relationship"|Ted Cruz|climate policies|CRITICIZED|Ted Cruz criticized the climate plan|0.8)
("relationship"|UN Climate Summit|Glasgow|LOCATED_IN|Climate summit is taking place in Glasgow|0.8)

Example 2 - Business News Report:
Text: "Tesla CEO Elon Musk sold $5 billion worth of Tesla stock this week, according to SEC filings reported by Reuters. The sale comes after Musk's Twitter poll where 57.9% of respondents voted for him to sell 10% of his holdings. Tesla shares dropped 12% in after-hours trading following the news."
Output:
("entity"|Tesla|ORGANIZATION|Electric vehicle and clean energy company)
("entity"|Elon Musk|PERSON|Chief Executive Officer of Tesla)
("entity"|CEO|PERSON|Executive title and role)
("entity"|$5 billion|STATISTIC|Dollar value of stock sale)
("entity"|Tesla stock|TOPIC|Publicly traded shares of Tesla Inc.)
("entity"|SEC filings|PUBLICATION|Securities and Exchange Commission regulatory documents)
("entity"|Reuters|MEDIA_OUTLET|International news agency)
("entity"|Twitter poll|EVENT|Social media survey conducted by Musk)
("entity"|57.9%|STATISTIC|Percentage of poll respondents favoring stock sale)
("entity"|10%|STATISTIC|Percentage of holdings considered for sale)
("entity"|Tesla shares|TOPIC|Tesla stock price and trading)
("entity"|12%|STATISTIC|Percentage drop in Tesla share price)
("entity"|after-hours trading|EVENT|Stock trading outside regular market hours)
("relationship"|Elon Musk|Tesla|CEO_OF|Elon Musk is CEO of Tesla|0.9)
("relationship"|Elon Musk|$5 billion|SOLD|Musk sold $5 billion worth of Tesla stock|0.9)
("relationship"|Elon Musk|SEC filings|DISCLOSED_IN|Stock sale disclosed in SEC filings|0.8)
("relationship"|Reuters|SEC filings|REPORTED|Reuters reported on SEC filings|0.8)
("relationship"|Elon Musk|Twitter poll|CONDUCTED|Musk conducted Twitter poll about stock sale|0.8)
("relationship"|Tesla shares|12%|DROPPED|Tesla shares dropped 12% after news|0.8)"""
    },
    "relationship-extraction": {
        "entity_types": "PERSON, ORGANIZATION, LOCATION, EVENT, TOPIC, MEDIA_OUTLET, PUBLICATION, QUOTE, STATISTIC, POLICY, INCIDENT",
        "relationship_types": "ANNOUNCED, REPORTED, QUOTED, CRITICIZED, PRAISED, ATTENDED, OCCURRED_IN, CAUSED, RESULTED_IN, DISCLOSED, INVESTIGATED, CONFIRMED, DENIED",
        "normalization_rules": """News relationship normalization:
- Use specific action verbs for news events and statements
- Distinguish between direct quotes and paraphrased statements
- Use REPORTED for media coverage relationships
- Use OCCURRED_IN for event location relationships
- Use CAUSED/RESULTED_IN for causal news relationships
- Use CONFIRMED/DENIED for official responses""",
        "relationship_guidelines": """News relationship guidelines:
- ANNOUNCED: Official statements and declarations
- REPORTED: Media coverage and journalistic reporting
- QUOTED: Direct quotations and attributed statements
- CRITICIZED/PRAISED: Opinion and reaction relationships
- ATTENDED: Event participation relationships
- OCCURRED_IN: Event location and timing relationships
- CAUSED/RESULTED_IN: Causal relationships in news events
- DISCLOSED: Information revelation relationships
- INVESTIGATED: Inquiry and examination relationships
- CONFIRMED/DENIED: Official verification or refutation""",
        "examples": """News Relationship Extraction Examples:

Example 1 - Breaking News Coverage:
Text: "The New York Times reported that FBI agents raided the offices of Mayor John Thompson in downtown Chicago on Wednesday morning. The investigation, confirmed by the Department of Justice, relates to alleged corruption charges. Thompson denied any wrongdoing in a statement to CNN, calling the allegations 'baseless and politically motivated.'"
Output:
("entity"|The New York Times|MEDIA_OUTLET|American daily newspaper)
("entity"|FBI agents|ORGANIZATION|Federal Bureau of Investigation personnel)
("entity"|Mayor John Thompson|PERSON|Elected official serving as city mayor)
("entity"|downtown Chicago|LOCATION|Central business district of Chicago)
("entity"|Wednesday morning|EVENT|Time when raid occurred)
("entity"|Department of Justice|ORGANIZATION|US federal executive department)
("entity"|corruption charges|TOPIC|Criminal allegations of official misconduct)
("entity"|CNN|MEDIA_OUTLET|Cable news network)
("entity"|statement|QUOTE|Official response or declaration)
("relationship"|The New York Times|FBI agents|REPORTED|NYT reported on FBI raid|0.9)
("relationship"|FBI agents|Mayor John Thompson|RAIDED|FBI raided mayor's offices|0.9)
("relationship"|FBI agents|downtown Chicago|OCCURRED_IN|Raid occurred in downtown Chicago|0.8)
("relationship"|Department of Justice|FBI agents|CONFIRMED|DOJ confirmed the investigation|0.8)
("relationship"|Mayor John Thompson|corruption charges|DENIED|Thompson denied corruption allegations|0.8)
("relationship"|Mayor John Thompson|CNN|QUOTED_BY|Thompson's statement quoted by CNN|0.8)"""
    },
    "claim-extraction": {
        "entity_specs": "PERSON, ORGANIZATION, EVENT, POLICY, INCIDENT, STATISTIC",
        "claim_description": """News claims to extract:
- Official statements and declarations by public figures
- Statistical data and factual assertions
- Event descriptions and incident reports
- Policy announcements and government actions
- Expert opinions and analysis
- Eyewitness accounts and testimonies
- Corporate announcements and business developments
- Legal proceedings and court decisions
- Scientific findings and research results
- Social and cultural trend observations"""
    },
    "entity-merging": {
        "allowed_entity_types": "PERSON, ORGANIZATION, LOCATION, EVENT, TOPIC, MEDIA_OUTLET, PUBLICATION, QUOTE, STATISTIC, POLICY, INCIDENT",
        "entity_type_mappings": """News entity type mappings:
- NEWSPAPER/MAGAZINE/JOURNAL/BLOG → MEDIA_OUTLET
- ARTICLE/REPORT/STORY/PIECE → PUBLICATION
- ACCIDENT/CRISIS/DISASTER/SCANDAL → INCIDENT
- LAW/REGULATION/BILL/LEGISLATION → POLICY
- STATEMENT/COMMENT/REMARK/DECLARATION → QUOTE
- PERCENTAGE/NUMBER/FIGURE/DATA → STATISTIC
- SUBJECT/ISSUE/MATTER/THEME → TOPIC""",
        "key_attributes": """News key attributes to preserve:
- Full names and official titles
- Geographic locations and jurisdictions
- Dates and timestamps of events
- Media outlet names and credibility
- Direct quotations and attributions
- Statistical data and measurements
- Policy names and legislative details
- Incident classifications and severity
- Source credibility and verification status
- Publication dates and update times"""
    }
}

def configure_news_domain(gateway):
    """Configure the LLMGateway for news and media content analysis."""
    gateway.configure_domain_defaults(NEWS_DOMAIN_CONFIG)
    return gateway