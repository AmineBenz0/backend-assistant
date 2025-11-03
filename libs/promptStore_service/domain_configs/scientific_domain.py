"""
Scientific research domain configuration for Graph Builder.

This module provides domain-specific defaults for scientific papers,
research documents, and academic publications.
"""

from typing import Dict, Any

# Scientific research domain configuration
SCIENTIFIC_DOMAIN_CONFIG: Dict[str, Dict[str, Any]] = {
    "extract-entities": {
        "entity_types": "PERSON, ORGANIZATION, CONCEPT, METHOD, DATASET, METRIC, PUBLICATION, EXPERIMENT, HYPOTHESIS, THEORY",
        "normalization_rules": """Scientific entity normalization rules:
- Use standard scientific naming conventions and terminology
- Prefer full method names over abbreviations (e.g., "Convolutional Neural Network" not "CNN")
- Use consistent dataset naming with version numbers when available
- Standardize metric names (e.g., "F1-score" not "F1", "Mean Squared Error" not "MSE")
- Use official publication titles and author names
- Normalize institution names to their official forms
- Use standard hypothesis and theory naming conventions""",
        "examples": """Scientific Entity Extraction Examples:

Example 1 - Machine Learning Research Paper:
Text: "Dr. Sarah Chen and her team at Stanford AI Lab evaluated BERT on the GLUE benchmark, achieving 85.2% accuracy and 0.91 F1-score. The study, published in Nature Machine Intelligence, compared their approach with GPT-3 and RoBERTa models. The research builds on transformer architecture theory and uses the Common Crawl dataset."
Output:
("entity"|Dr. Sarah Chen|PERSON|Research scientist specializing in natural language processing)
("entity"|Stanford AI Lab|ORGANIZATION|Artificial intelligence research laboratory at Stanford University)
("entity"|BERT|METHOD|Bidirectional Encoder Representations from Transformers language model)
("entity"|GLUE|DATASET|General Language Understanding Evaluation benchmark suite)
("entity"|accuracy|METRIC|Classification performance measurement)
("entity"|F1-score|METRIC|Harmonic mean of precision and recall)
("entity"|Nature Machine Intelligence|PUBLICATION|Scientific journal focusing on machine intelligence)
("entity"|GPT-3|METHOD|Generative Pre-trained Transformer 3 language model)
("entity"|RoBERTa|METHOD|Robustly Optimized BERT Pretraining Approach)
("entity"|transformer architecture|THEORY|Neural network architecture for sequence modeling)
("entity"|Common Crawl|DATASET|Web crawl data corpus for language modeling)
("relationship"|Dr. Sarah Chen|Stanford AI Lab|AFFILIATED_WITH|Dr. Chen leads research team at Stanford AI Lab|0.9)
("relationship"|Dr. Sarah Chen|BERT|EVALUATED|Dr. Chen's team evaluated BERT model performance|0.9)
("relationship"|BERT|GLUE|TESTED_ON|BERT was evaluated on GLUE benchmark|0.9)
("relationship"|Dr. Sarah Chen|Nature Machine Intelligence|PUBLISHED_IN|Research was published in Nature Machine Intelligence|0.8)
("relationship"|BERT|GPT-3|COMPARED_WITH|BERT performance was compared with GPT-3|0.8)
("relationship"|BERT|transformer architecture|BASED_ON|BERT is based on transformer architecture theory|0.8)

Example 2 - Medical Research Study:
Text: "The clinical trial conducted by Dr. Michael Rodriguez at Johns Hopkins Medical Center tested the efficacy of Drug-X in treating Alzheimer's disease. The randomized controlled trial involved 500 patients over 24 months, measuring cognitive decline using the MMSE scale. Results showed 23% improvement compared to placebo group, with p-value < 0.001."
Output:
("entity"|Dr. Michael Rodriguez|PERSON|Clinical researcher specializing in neurodegenerative diseases)
("entity"|Johns Hopkins Medical Center|ORGANIZATION|Academic medical center and research institution)
("entity"|Drug-X|METHOD|Experimental pharmaceutical treatment for Alzheimer's disease)
("entity"|Alzheimer's disease|CONCEPT|Progressive neurodegenerative disorder affecting memory and cognition)
("entity"|randomized controlled trial|METHOD|Gold standard experimental design for clinical research)
("entity"|MMSE scale|METRIC|Mini-Mental State Examination for cognitive assessment)
("entity"|cognitive decline|CONCEPT|Progressive deterioration of mental functions)
("entity"|p-value|METRIC|Statistical measure of evidence against null hypothesis)
("relationship"|Dr. Michael Rodriguez|Johns Hopkins Medical Center|AFFILIATED_WITH|Dr. Rodriguez conducts research at Johns Hopkins|0.9)
("relationship"|Dr. Michael Rodriguez|Drug-X|TESTED|Dr. Rodriguez conducted clinical trial testing Drug-X|0.9)
("relationship"|Drug-X|Alzheimer's disease|TREATS|Drug-X is being tested as treatment for Alzheimer's disease|0.8)
("relationship"|randomized controlled trial|Drug-X|EVALUATES|RCT methodology used to evaluate Drug-X efficacy|0.8)
("relationship"|MMSE scale|cognitive decline|MEASURES|MMSE scale used to measure cognitive decline|0.8)"""
    },
    "relationship-extraction": {
        "entity_types": "PERSON, ORGANIZATION, CONCEPT, METHOD, DATASET, METRIC, PUBLICATION, EXPERIMENT, HYPOTHESIS, THEORY",
        "relationship_types": "AUTHORED_BY, PUBLISHED_IN, EVALUATED_ON, COMPARED_WITH, BASED_ON, TESTED_ON, MEASURES, TREATS, CAUSES, CORRELATES_WITH, VALIDATES, REFUTES, EXTENDS, CITES",
        "normalization_rules": """Scientific relationship normalization:
- Use precise relationship types that reflect scientific methodology
- Distinguish between correlation and causation relationships
- Use BASED_ON for theoretical foundations and prior work
- Use EXTENDS for research that builds upon previous studies
- Use VALIDATES or REFUTES for hypothesis testing outcomes
- Use CITES for reference relationships between publications""",
        "relationship_guidelines": """Scientific relationship guidelines:
- AUTHORED_BY: Authorship relationships for publications and research
- PUBLISHED_IN: Publication venue relationships (journals, conferences)
- EVALUATED_ON/TESTED_ON: Experimental evaluation relationships
- COMPARED_WITH: Comparative analysis relationships between methods
- BASED_ON: Theoretical or methodological foundation relationships
- MEASURES: Metric or assessment tool relationships
- TREATS/CAUSES: Medical or causal relationships
- CORRELATES_WITH: Statistical correlation relationships
- VALIDATES/REFUTES: Hypothesis testing outcome relationships
- EXTENDS: Research continuation or improvement relationships
- CITES: Reference and citation relationships""",
        "examples": """Scientific Relationship Extraction Examples:

Example 1 - Research Methodology Paper:
Text: "The study by Dr. Lisa Wang at MIT, published in Science, introduces a novel deep learning method called NeuroNet-X. The approach extends previous work on convolutional neural networks and was evaluated on ImageNet dataset. Results validate the hypothesis that attention mechanisms improve image classification accuracy by 15%."
Output:
("entity"|Dr. Lisa Wang|PERSON|Computer vision researcher at MIT)
("entity"|MIT|ORGANIZATION|Massachusetts Institute of Technology)
("entity"|Science|PUBLICATION|Prestigious scientific journal)
("entity"|NeuroNet-X|METHOD|Novel deep learning architecture for image classification)
("entity"|convolutional neural networks|METHOD|Deep learning architecture for image processing)
("entity"|ImageNet|DATASET|Large-scale image recognition dataset)
("entity"|attention mechanisms|CONCEPT|Neural network component for selective focus)
("entity"|image classification|CONCEPT|Computer vision task for categorizing images)
("relationship"|Dr. Lisa Wang|MIT|AFFILIATED_WITH|Dr. Wang conducts research at MIT|0.9)
("relationship"|Dr. Lisa Wang|Science|PUBLISHED_IN|Dr. Wang published research in Science journal|0.9)
("relationship"|Dr. Lisa Wang|NeuroNet-X|AUTHORED_BY|NeuroNet-X method was developed by Dr. Wang|0.9)
("relationship"|NeuroNet-X|convolutional neural networks|EXTENDS|NeuroNet-X extends previous CNN work|0.8)
("relationship"|NeuroNet-X|ImageNet|EVALUATED_ON|NeuroNet-X was evaluated on ImageNet dataset|0.8)
("relationship"|attention mechanisms|image classification|VALIDATES|Study validates that attention mechanisms improve classification|0.8)"""
    },
    "claim-extraction": {
        "entity_specs": "PERSON, ORGANIZATION, METHOD, DATASET, METRIC, PUBLICATION, EXPERIMENT, HYPOTHESIS",
        "claim_description": """Scientific claims to extract:
- Research findings and experimental results
- Statistical significance and performance metrics
- Hypothesis validation or refutation statements
- Comparative performance claims between methods
- Causal relationships and mechanisms
- Theoretical contributions and novel insights
- Reproducibility and replication results
- Clinical efficacy and safety outcomes
- Dataset characteristics and limitations
- Future research directions and implications"""
    },
    "entity-merging": {
        "allowed_entity_types": "PERSON, ORGANIZATION, CONCEPT, METHOD, DATASET, METRIC, PUBLICATION, EXPERIMENT, HYPOTHESIS, THEORY",
        "entity_type_mappings": """Scientific entity type mappings:
- ALGORITHM/MODEL/APPROACH/TECHNIQUE → METHOD
- JOURNAL/CONFERENCE/PROCEEDINGS → PUBLICATION
- UNIVERSITY/INSTITUTE/LAB/CENTER → ORGANIZATION
- STUDY/TRIAL/EXPERIMENT/TEST → EXPERIMENT
- BENCHMARK/CORPUS/DATABASE → DATASET
- SCORE/MEASURE/INDICATOR/RATING → METRIC
- PRINCIPLE/LAW/FRAMEWORK → THEORY""",
        "key_attributes": """Scientific key attributes to preserve:
- Author names and institutional affiliations
- Publication venues and dates
- Experimental parameters and conditions
- Statistical measures and confidence intervals
- Dataset sizes and characteristics
- Method performance metrics
- Theoretical foundations and assumptions
- Replication and validation status
- Peer review and citation information
- Research funding and grant information"""
    }
}

def configure_scientific_domain(gateway):
    """Configure the LLMGateway for scientific research document analysis."""
    gateway.configure_domain_defaults(SCIENTIFIC_DOMAIN_CONFIG)
    return gateway