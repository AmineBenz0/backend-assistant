"""
Legal documents domain configuration for Graph Builder.

This module provides domain-specific defaults for legal documents,
contracts, court cases, and regulatory texts.
"""

from typing import Dict, Any

# Legal documents domain configuration
LEGAL_DOMAIN_CONFIG: Dict[str, Dict[str, Any]] = {
    "extract-entities": {
        "entity_types": "PERSON, ORGANIZATION, LOCATION, LEGAL_DOCUMENT, STATUTE, REGULATION, COURT, CASE, CONTRACT, LEGAL_CONCEPT, DATE, MONETARY_AMOUNT",
        "normalization_rules": """Legal entity normalization rules:
- Use full legal names for persons and entities (e.g., "John Smith, Plaintiff" not "John Smith")
- Use official court names and jurisdictions
- Use proper case citations and legal document titles
- Standardize legal concepts to established terminology
- Use full statute and regulation citations
- Normalize monetary amounts to standard currency format
- Use proper legal entity designations (LLC, Corp, Inc, etc.)""",
        "examples": """Legal Entity Extraction Examples:

Example 1 - Contract Dispute Case:
Text: "In the matter of TechCorp LLC v. DataSystems Inc., filed in the Superior Court of California, County of Santa Clara, Case No. 2023-CV-001234, the plaintiff alleges breach of the Software License Agreement dated January 15, 2022. The contract specified payment of $500,000 for exclusive licensing rights under California Civil Code Section 1549."
Output:
("entity"|TechCorp LLC|ORGANIZATION|Technology company serving as plaintiff in contract dispute)
("entity"|DataSystems Inc.|ORGANIZATION|Data services company serving as defendant)
("entity"|Superior Court of California|COURT|State trial court with general jurisdiction)
("entity"|Santa Clara County|LOCATION|County jurisdiction in California)
("entity"|Case No. 2023-CV-001234|CASE|Civil case number for contract dispute)
("entity"|Software License Agreement|CONTRACT|Legal agreement for software licensing rights)
("entity"|January 15, 2022|DATE|Contract execution date)
("entity"|$500,000|MONETARY_AMOUNT|Contract value for licensing rights)
("entity"|California Civil Code Section 1549|STATUTE|State law governing contract interpretation)
("entity"|breach of contract|LEGAL_CONCEPT|Legal claim for contract violation)
("relationship"|TechCorp LLC|DataSystems Inc.|SUES|TechCorp LLC filed lawsuit against DataSystems Inc.|0.9)
("relationship"|TechCorp LLC|Superior Court of California|FILED_IN|Lawsuit filed in Superior Court of California|0.8)
("relationship"|Software License Agreement|January 15, 2022|EXECUTED_ON|Contract was executed on January 15, 2022|0.9)
("relationship"|Software License Agreement|$500,000|VALUED_AT|Contract specifies payment of $500,000|0.8)

Example 2 - Regulatory Compliance Document:
Text: "The Securities and Exchange Commission (SEC) issued Regulation S-K Item 303 requiring public companies to provide Management's Discussion and Analysis (MD&A) in their Form 10-K filings. Companies must disclose material changes in financial condition under 17 CFR 229.303, with violations subject to penalties under Securities Exchange Act Section 21C."
Output:
("entity"|Securities and Exchange Commission|ORGANIZATION|Federal agency regulating securities markets)
("entity"|Regulation S-K Item 303|REGULATION|SEC regulation requiring MD&A disclosure)
("entity"|Management's Discussion and Analysis|LEGAL_CONCEPT|Required disclosure section in SEC filings)
("entity"|Form 10-K|LEGAL_DOCUMENT|Annual report required for public companies)
("entity"|17 CFR 229.303|REGULATION|Code of Federal Regulations section on MD&A requirements)
("entity"|Securities Exchange Act Section 21C|STATUTE|Federal law authorizing SEC enforcement actions)
("relationship"|Securities and Exchange Commission|Regulation S-K Item 303|ISSUED|SEC issued regulation requiring MD&A disclosure|0.9)
("relationship"|Regulation S-K Item 303|Form 10-K|APPLIES_TO|Regulation applies to Form 10-K filings|0.8)
("relationship"|17 CFR 229.303|Management's Discussion and Analysis|GOVERNS|CFR section governs MD&A disclosure requirements|0.8)"""
    },
    "relationship-extraction": {
        "entity_types": "PERSON, ORGANIZATION, LOCATION, LEGAL_DOCUMENT, STATUTE, REGULATION, COURT, CASE, CONTRACT, LEGAL_CONCEPT, DATE, MONETARY_AMOUNT",
        "relationship_types": "SUES, REPRESENTS, GOVERNS, APPLIES_TO, VIOLATES, COMPLIES_WITH, CITES, OVERRULES, AMENDS, EXECUTED_ON, FILED_IN, DECIDED_BY, APPEALS_TO, VALUED_AT, PENALIZED_UNDER",
        "normalization_rules": """Legal relationship normalization:
- Use precise legal relationship types that reflect legal procedures
- Distinguish between different types of legal actions (sues, appeals, etc.)
- Use GOVERNS for regulatory and statutory authority relationships
- Use CITES for legal precedent and authority references
- Use COMPLIES_WITH or VIOLATES for regulatory compliance relationships""",
        "relationship_guidelines": """Legal relationship guidelines:
- SUES: Litigation relationships between parties
- REPRESENTS: Attorney-client relationships
- GOVERNS: Regulatory or statutory authority over entities or activities
- APPLIES_TO: Legal rule or regulation applicability
- VIOLATES/COMPLIES_WITH: Regulatory compliance relationships
- CITES: Legal precedent and authority references
- OVERRULES/AMENDS: Legal hierarchy and modification relationships
- EXECUTED_ON: Contract and agreement timing
- FILED_IN/DECIDED_BY: Court jurisdiction and decision relationships
- APPEALS_TO: Appellate court relationships
- VALUED_AT: Monetary value relationships
- PENALIZED_UNDER: Enforcement and penalty relationships""",
        "examples": """Legal Relationship Extraction Examples:

Example 1 - Corporate Litigation:
Text: "In Smith v. MegaCorp Inc., the plaintiff, represented by Johnson & Associates LLP, filed suit in the U.S. District Court for the Southern District of New York alleging violations of the Fair Labor Standards Act. The case was decided on March 15, 2023, with the court awarding $2.5 million in damages."
Output:
("entity"|Smith|PERSON|Plaintiff in employment law case)
("entity"|MegaCorp Inc.|ORGANIZATION|Defendant corporation in labor dispute)
("entity"|Johnson & Associates LLP|ORGANIZATION|Law firm representing plaintiff)
("entity"|U.S. District Court for the Southern District of New York|COURT|Federal trial court)
("entity"|Fair Labor Standards Act|STATUTE|Federal employment law)
("entity"|March 15, 2023|DATE|Court decision date)
("entity"|$2.5 million|MONETARY_AMOUNT|Damages awarded by court)
("relationship"|Smith|MegaCorp Inc.|SUES|Smith filed lawsuit against MegaCorp Inc.|0.9)
("relationship"|Johnson & Associates LLP|Smith|REPRESENTS|Law firm represents Smith in litigation|0.9)
("relationship"|Smith|U.S. District Court for the Southern District of New York|FILED_IN|Lawsuit filed in federal district court|0.8)
("relationship"|MegaCorp Inc.|Fair Labor Standards Act|VIOLATES|MegaCorp allegedly violated FLSA|0.8)
("relationship"|U.S. District Court for the Southern District of New York|March 15, 2023|DECIDED_ON|Court issued decision on March 15, 2023|0.8)
("relationship"|Smith|$2.5 million|AWARDED|Court awarded $2.5 million in damages to Smith|0.9)"""
    },
    "claim-extraction": {
        "entity_specs": "PERSON, ORGANIZATION, LEGAL_DOCUMENT, STATUTE, REGULATION, COURT, CASE, CONTRACT",
        "claim_description": """Legal claims to extract:
- Allegations and legal claims made by parties
- Court findings and legal determinations
- Regulatory violations and compliance issues
- Contract terms and obligations
- Legal precedents and case law citations
- Statutory and regulatory requirements
- Penalties and enforcement actions
- Settlement terms and agreements
- Legal rights and obligations
- Jurisdictional and procedural determinations"""
    },
    "entity-merging": {
        "allowed_entity_types": "PERSON, ORGANIZATION, LOCATION, LEGAL_DOCUMENT, STATUTE, REGULATION, COURT, CASE, CONTRACT, LEGAL_CONCEPT, DATE, MONETARY_AMOUNT",
        "entity_type_mappings": """Legal entity type mappings:
- LAW/ACT/CODE/TITLE → STATUTE
- RULE/POLICY/DIRECTIVE/ORDER → REGULATION
- AGREEMENT/TREATY/MEMORANDUM → CONTRACT
- LAWSUIT/LITIGATION/PROCEEDING → CASE
- TRIBUNAL/BENCH/PANEL → COURT
- FILING/BRIEF/MOTION/PLEADING → LEGAL_DOCUMENT
- PRINCIPLE/DOCTRINE/STANDARD → LEGAL_CONCEPT""",
        "key_attributes": """Legal key attributes to preserve:
- Full legal names and titles
- Case numbers and citations
- Court jurisdictions and levels
- Statute and regulation citations
- Contract dates and terms
- Monetary amounts and penalties
- Legal procedural status
- Attorney and representation information
- Jurisdictional boundaries
- Legal precedent and authority levels"""
    }
}

def configure_legal_domain(gateway):
    """Configure the LLMGateway for legal document analysis."""
    gateway.configure_domain_defaults(LEGAL_DOMAIN_CONFIG)
    return gateway