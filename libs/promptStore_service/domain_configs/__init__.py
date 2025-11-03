"""
Domain-specific configurations for the LLM Gateway.

This package contains domain-specific prompt configurations that can be used
to customize the Graph Builder for different use cases.
"""

from .base_defaults import BASE_DEFAULTS_MAP
from .resume_domain import RESUME_DOMAIN_CONFIG, configure_resume_domain
from .general_domain import GENERAL_DOMAIN_CONFIG, configure_general_domain
from .scientific_domain import SCIENTIFIC_DOMAIN_CONFIG, configure_scientific_domain
from .legal_domain import LEGAL_DOMAIN_CONFIG, configure_legal_domain
from .financial_domain import FINANCIAL_DOMAIN_CONFIG, configure_financial_domain
from .news_domain import NEWS_DOMAIN_CONFIG, configure_news_domain
from .dpac_domain import DPAC_DOMAIN_CONFIG, configure_dpac_domain

__all__ = [
    'BASE_DEFAULTS_MAP',
    'RESUME_DOMAIN_CONFIG', 'configure_resume_domain',
    'GENERAL_DOMAIN_CONFIG', 'configure_general_domain',
    'SCIENTIFIC_DOMAIN_CONFIG', 'configure_scientific_domain',
    'LEGAL_DOMAIN_CONFIG', 'configure_legal_domain',
    'FINANCIAL_DOMAIN_CONFIG', 'configure_financial_domain',
    'NEWS_DOMAIN_CONFIG', 'configure_news_domain'
    'DPAC_DOMAIN_CONFIG', 'configure_dpac_domain'
]