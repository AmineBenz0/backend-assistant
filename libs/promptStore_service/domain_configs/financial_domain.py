"""
Financial and business domain configuration for Graph Builder.

This module provides domain-specific defaults for financial reports,
business documents, earnings calls, and market analysis.
"""

from typing import Dict, Any

# Financial and business domain configuration
FINANCIAL_DOMAIN_CONFIG: Dict[str, Dict[str, Any]] = {
    "extract-entities": {
        "entity_types": "PERSON, ORGANIZATION, LOCATION, FINANCIAL_INSTRUMENT, METRIC, CURRENCY, MARKET, SECTOR, PRODUCT, SERVICE, FINANCIAL_STATEMENT, REGULATION",
        "normalization_rules": """Financial entity normalization rules:
- Use official company names and stock ticker symbols
- Standardize financial metrics to common terminology (e.g., "EBITDA" not "earnings before interest")
- Use proper currency codes (USD, EUR, GBP) and amounts
- Normalize market and sector names to standard classifications
- Use official financial statement names (10-K, 10-Q, 8-K)
- Standardize executive titles and roles
- Use proper financial instrument names (bonds, equities, derivatives)""",
        "examples": """Financial Entity Extraction Examples:

Example 1 - Earnings Report Analysis:
Text: "Apple Inc. (AAPL) reported Q4 2023 revenue of $89.5 billion, up 8% year-over-year, driven by strong iPhone sales in the Americas and China markets. CEO Tim Cook highlighted services revenue growth of 16% to $22.3 billion. The company's gross margin improved to 45.2%, exceeding analyst expectations. Apple's cash position remains strong at $162 billion."
Output:
("entity"|Apple Inc.|ORGANIZATION|Multinational technology corporation)
("entity"|AAPL|FINANCIAL_INSTRUMENT|Stock ticker symbol for Apple Inc.)
("entity"|Q4 2023|METRIC|Fourth quarter of fiscal year 2023)
("entity"|$89.5 billion|CURRENCY|Quarterly revenue amount in US dollars)
("entity"|iPhone|PRODUCT|Apple's flagship smartphone product line)
("entity"|Americas|MARKET|Geographic market region including North and South America)
("entity"|China|MARKET|Chinese market for Apple products)
("entity"|Tim Cook|PERSON|Chief Executive Officer of Apple Inc.)
("entity"|services revenue|METRIC|Revenue from Apple's services business segment)
("entity"|$22.3 billion|CURRENCY|Services revenue amount in US dollars)
("entity"|gross margin|METRIC|Financial profitability measure)
("entity"|45.2%|METRIC|Gross margin percentage for the quarter)
("entity"|cash position|METRIC|Company's available cash and cash equivalents)
("entity"|$162 billion|CURRENCY|Total cash holdings in US dollars)
("relationship"|Apple Inc.|AAPL|TRADES_AS|Apple Inc. trades under ticker symbol AAPL|0.9)
("relationship"|Apple Inc.|$89.5 billion|REPORTED|Apple reported Q4 revenue of $89.5 billion|0.9)
("relationship"|iPhone|Americas|SOLD_IN|iPhone sales were strong in Americas market|0.8)
("relationship"|iPhone|China|SOLD_IN|iPhone sales were strong in China market|0.8)
("relationship"|Tim Cook|Apple Inc.|CEO_OF|Tim Cook is CEO of Apple Inc.|0.9)
("relationship"|Apple Inc.|services revenue|GENERATES|Apple generates revenue from services business|0.8)

Example 2 - Market Analysis Report:
Text: "Goldman Sachs (GS) upgraded Tesla Inc. (TSLA) to Buy from Neutral, raising the price target to $248 from $185. The investment bank cited improving fundamentals in the electric vehicle sector and Tesla's expanding market share in China and Europe. Analyst John Martinez noted Tesla's strong free cash flow generation and reduced capital expenditure requirements."
Output:
("entity"|Goldman Sachs|ORGANIZATION|Investment banking and financial services company)
("entity"|GS|FINANCIAL_INSTRUMENT|Stock ticker symbol for Goldman Sachs)
("entity"|Tesla Inc.|ORGANIZATION|Electric vehicle and clean energy company)
("entity"|TSLA|FINANCIAL_INSTRUMENT|Stock ticker symbol for Tesla Inc.)
("entity"|Buy rating|METRIC|Investment recommendation to purchase stock)
("entity"|Neutral rating|METRIC|Previous neutral investment recommendation)
("entity"|$248|CURRENCY|New price target in US dollars)
("entity"|$185|CURRENCY|Previous price target in US dollars)
("entity"|electric vehicle sector|SECTOR|Automotive industry segment focused on EVs)
("entity"|market share|METRIC|Company's portion of total market sales)
("entity"|China|MARKET|Chinese automotive market)
("entity"|Europe|MARKET|European automotive market)
("entity"|John Martinez|PERSON|Financial analyst at Goldman Sachs)
("entity"|free cash flow|METRIC|Cash generated from operations minus capital expenditures)
("relationship"|Goldman Sachs|Tesla Inc.|UPGRADED|Goldman Sachs upgraded Tesla stock rating|0.9)
("relationship"|Goldman Sachs|Buy rating|ASSIGNED|Goldman Sachs assigned Buy rating to Tesla|0.8)
("relationship"|Goldman Sachs|$248|SET_TARGET|Goldman Sachs set price target at $248|0.8)
("relationship"|Tesla Inc.|electric vehicle sector|OPERATES_IN|Tesla operates in electric vehicle sector|0.8)
("relationship"|Tesla Inc.|China|HAS_SHARE_IN|Tesla has expanding market share in China|0.8)
("relationship"|John Martinez|Goldman Sachs|ANALYST_AT|John Martinez is analyst at Goldman Sachs|0.9)"""
    },
    "relationship-extraction": {
        "entity_types": "PERSON, ORGANIZATION, LOCATION, FINANCIAL_INSTRUMENT, METRIC, CURRENCY, MARKET, SECTOR, PRODUCT, SERVICE, FINANCIAL_STATEMENT, REGULATION",
        "relationship_types": "TRADES_AS, REPORTED, UPGRADED, DOWNGRADED, ACQUIRED, MERGED_WITH, COMPETES_WITH, OPERATES_IN, SELLS_IN, GENERATES, INVESTS_IN, OWNS, MANAGES, REGULATES, COMPLIES_WITH",
        "normalization_rules": """Financial relationship normalization:
- Use specific financial relationship types for market actions
- Distinguish between different types of corporate actions (mergers, acquisitions)
- Use TRADES_AS for ticker symbol relationships
- Use OPERATES_IN for business sector relationships
- Use GENERATES for revenue and income relationships
- Use REGULATES for regulatory oversight relationships""",
        "relationship_guidelines": """Financial relationship guidelines:
- TRADES_AS: Stock ticker and trading symbol relationships
- REPORTED: Financial results and earnings relationships
- UPGRADED/DOWNGRADED: Analyst rating changes
- ACQUIRED/MERGED_WITH: Corporate transaction relationships
- COMPETES_WITH: Competitive market relationships
- OPERATES_IN: Business sector and market participation
- SELLS_IN/GENERATES: Revenue and market relationships
- INVESTS_IN/OWNS: Investment and ownership relationships
- MANAGES: Asset management and fund relationships
- REGULATES/COMPLIES_WITH: Regulatory oversight relationships""",
        "examples": """Financial Relationship Extraction Examples:

Example 1 - Corporate Transaction:
Text: "Microsoft Corporation (MSFT) announced the acquisition of Activision Blizzard Inc. (ATVI) for $68.7 billion, pending regulatory approval from the Federal Trade Commission. The deal will strengthen Microsoft's position in the gaming sector, competing directly with Sony and Nintendo in the console market."
Output:
("entity"|Microsoft Corporation|ORGANIZATION|Technology corporation and software company)
("entity"|MSFT|FINANCIAL_INSTRUMENT|Stock ticker for Microsoft Corporation)
("entity"|Activision Blizzard Inc.|ORGANIZATION|Video game holding company)
("entity"|ATVI|FINANCIAL_INSTRUMENT|Stock ticker for Activision Blizzard)
("entity"|$68.7 billion|CURRENCY|Acquisition price in US dollars)
("entity"|Federal Trade Commission|ORGANIZATION|US antitrust regulatory agency)
("entity"|gaming sector|SECTOR|Video game industry segment)
("entity"|Sony|ORGANIZATION|Japanese technology and entertainment company)
("entity"|Nintendo|ORGANIZATION|Japanese video game company)
("entity"|console market|MARKET|Video game console hardware market)
("relationship"|Microsoft Corporation|MSFT|TRADES_AS|Microsoft trades under ticker MSFT|0.9)
("relationship"|Activision Blizzard Inc.|ATVI|TRADES_AS|Activision Blizzard trades under ticker ATVI|0.9)
("relationship"|Microsoft Corporation|Activision Blizzard Inc.|ACQUIRED|Microsoft announced acquisition of Activision Blizzard|0.9)
("relationship"|Microsoft Corporation|$68.7 billion|PAYING|Microsoft paying $68.7 billion for acquisition|0.8)
("relationship"|Federal Trade Commission|Microsoft Corporation|REGULATES|FTC provides regulatory approval for Microsoft deals|0.7)
("relationship"|Microsoft Corporation|gaming sector|OPERATES_IN|Microsoft operates in gaming sector|0.8)
("relationship"|Microsoft Corporation|Sony|COMPETES_WITH|Microsoft competes with Sony in console market|0.8)
("relationship"|Microsoft Corporation|Nintendo|COMPETES_WITH|Microsoft competes with Nintendo in console market|0.8)"""
    },
    "claim-extraction": {
        "entity_specs": "ORGANIZATION, FINANCIAL_INSTRUMENT, METRIC, CURRENCY, MARKET, SECTOR, PRODUCT",
        "claim_description": """Financial claims to extract:
- Financial performance metrics and results
- Revenue and profitability statements
- Market share and competitive position claims
- Growth projections and guidance
- Investment recommendations and ratings
- Regulatory compliance and violations
- Corporate transaction terms and conditions
- Risk factors and market conditions
- Analyst estimates and forecasts
- Executive compensation and governance issues"""
    },
    "entity-merging": {
        "allowed_entity_types": "PERSON, ORGANIZATION, LOCATION, FINANCIAL_INSTRUMENT, METRIC, CURRENCY, MARKET, SECTOR, PRODUCT, SERVICE, FINANCIAL_STATEMENT, REGULATION",
        "entity_type_mappings": """Financial entity type mappings:
- STOCK/EQUITY/SHARE/TICKER → FINANCIAL_INSTRUMENT
- BOND/DEBT/SECURITY/DERIVATIVE → FINANCIAL_INSTRUMENT
- REVENUE/INCOME/EARNINGS/PROFIT → METRIC
- DOLLAR/EURO/YEN/POUND → CURRENCY
- INDUSTRY/BUSINESS/VERTICAL → SECTOR
- REGION/COUNTRY/TERRITORY → MARKET
- OFFERING/SOLUTION/PLATFORM → PRODUCT or SERVICE""",
        "key_attributes": """Financial key attributes to preserve:
- Company names and ticker symbols
- Financial amounts and currencies
- Percentage changes and growth rates
- Market capitalizations and valuations
- Executive names and titles
- Analyst names and firms
- Regulatory bodies and compliance status
- Geographic markets and regions
- Business segments and product lines
- Financial statement periods and dates"""
    }
}

def configure_financial_domain(gateway):
    """Configure the LLMGateway for financial and business document analysis."""
    gateway.configure_domain_defaults(FINANCIAL_DOMAIN_CONFIG)
    return gateway