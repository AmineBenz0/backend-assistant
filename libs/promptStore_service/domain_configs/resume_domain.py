"""
Resume domain configuration for Graph Builder.

This module provides domain-specific defaults for resume/CV parsing.
Use this as an example of how to configure the LLMGateway for specific domains.
"""

from typing import Dict, Any

# Resume-specific domain configuration
RESUME_DOMAIN_CONFIG: Dict[str, Dict[str, Any]] = {
    "extract-entities": {
        "entity_types": "PERSON, ORGANIZATION, LOCATION, TECHNOLOGY, SKILL, CERTIFICATION, EDUCATION, PROJECT",
        "normalization_rules": """Resume-specific entity normalization rules:
- Use consistent capitalization for entity names
- Prefer full official names over abbreviations
- Group similar technologies under canonical forms (e.g., "JavaScript" not "JS")
- Standardize company names (e.g., "Microsoft Corporation" not "MSFT")
- Use official certification names (e.g., "AWS Certified Solutions Architect")
- Normalize job titles to standard forms (e.g., "Software Engineer" not "SWE")
- Use full university names (e.g., "Stanford University" not "Stanford")
- Standardize technology names (e.g., "React.js" not "ReactJS")""",
        "examples": """Resume Entity Extraction Examples:

Example 1 - Software Engineer Resume:
Text: "John Smith is a Senior Software Engineer at Google with 5 years of experience in Python, React, and AWS. He holds a Computer Science degree from Stanford University and is AWS Certified Solutions Architect. Previously worked at Microsoft building cloud applications."
Output:
("entity"|John Smith|PERSON|Senior Software Engineer with 5 years experience in cloud technologies and web development)
("entity"|Google|ORGANIZATION|Technology company specializing in internet services)
("entity"|Microsoft|ORGANIZATION|Technology corporation)
("entity"|Python|TECHNOLOGY|High-level programming language)
("entity"|React|TECHNOLOGY|JavaScript library for building user interfaces)
("entity"|AWS|TECHNOLOGY|Amazon Web Services cloud computing platform)
("entity"|Stanford University|EDUCATION|Private research university in California)
("entity"|Computer Science|SKILL|Academic field and professional discipline)
("entity"|AWS Certified Solutions Architect|CERTIFICATION|Professional cloud architecture certification)
("relationship"|John Smith|Google|WORKS_FOR|John Smith works as Senior Software Engineer at Google|0.9)
("relationship"|John Smith|Microsoft|EMPLOYED_BY|John Smith previously worked at Microsoft|0.8)
("relationship"|John Smith|Python|SKILLED_IN|John Smith has expertise in Python programming|0.8)
("relationship"|John Smith|React|SKILLED_IN|John Smith is skilled in React development|0.8)
("relationship"|John Smith|AWS|USES|John Smith uses AWS cloud services professionally|0.8)
("relationship"|John Smith|Stanford University|GRADUATED_FROM|John Smith graduated from Stanford University|0.9)
("relationship"|John Smith|AWS Certified Solutions Architect|CERTIFIED_BY|John Smith holds AWS certification|0.9)

Example 2 - Data Scientist Resume:
Text: "Dr. Sarah Chen, PhD in Machine Learning from MIT, currently works as Senior Data Scientist at Netflix. She specializes in deep learning using TensorFlow and PyTorch, and has published research on computer vision. Certified in Google Cloud Professional Data Engineer."
Output:
("entity"|Dr. Sarah Chen|PERSON|Senior Data Scientist with PhD in Machine Learning, specializes in deep learning and computer vision)
("entity"|Netflix|ORGANIZATION|Streaming entertainment company)
("entity"|MIT|EDUCATION|Massachusetts Institute of Technology)
("entity"|Machine Learning|SKILL|Artificial intelligence and data science field)
("entity"|TensorFlow|TECHNOLOGY|Open-source machine learning framework)
("entity"|PyTorch|TECHNOLOGY|Machine learning library for Python)
("entity"|computer vision|SKILL|Field of AI focused on visual data processing)
("entity"|Google Cloud Professional Data Engineer|CERTIFICATION|Cloud data engineering certification)
("relationship"|Dr. Sarah Chen|Netflix|WORKS_FOR|Dr. Sarah Chen works as Senior Data Scientist at Netflix|0.9)
("relationship"|Dr. Sarah Chen|MIT|GRADUATED_FROM|Dr. Sarah Chen earned PhD from MIT|0.9)
("relationship"|Dr. Sarah Chen|TensorFlow|USES|Dr. Sarah Chen uses TensorFlow for deep learning|0.8)
("relationship"|Dr. Sarah Chen|PyTorch|USES|Dr. Sarah Chen uses PyTorch for machine learning|0.8)
("relationship"|Dr. Sarah Chen|Google Cloud Professional Data Engineer|CERTIFIED_BY|Dr. Sarah Chen is certified in Google Cloud|0.9)

Example 3 - Project Manager Resume:
Text: "Maria Rodriguez manages software development projects at TechCorp, leading a team of 12 developers. She has PMP certification and 8 years of experience with Agile methodologies. Maria built an e-commerce platform using React and Node.js deployed on AWS."
Output:
("entity"|Maria Rodriguez|PERSON|Project manager with PMP certification leading software development teams)
("entity"|TechCorp|ORGANIZATION|Technology company)
("entity"|software development team|PROJECT|Team of 12 developers managed by Maria)
("entity"|PMP certification|CERTIFICATION|Project Management Professional certification)
("entity"|Agile methodologies|SKILL|Software development methodology)
("entity"|e-commerce platform|PROJECT|Online retail system developed by Maria)
("entity"|React|TECHNOLOGY|JavaScript library for building user interfaces)
("entity"|Node.js|TECHNOLOGY|JavaScript runtime for server-side development)
("entity"|AWS|TECHNOLOGY|Amazon Web Services cloud platform)
("relationship"|Maria Rodriguez|TechCorp|WORKS_FOR|Maria Rodriguez manages projects at TechCorp|0.9)
("relationship"|Maria Rodriguez|software development team|MANAGES|Maria Rodriguez leads a team of 12 developers|0.9)
("relationship"|Maria Rodriguez|PMP certification|CERTIFIED_BY|Maria Rodriguez holds PMP certification|0.9)
("relationship"|Maria Rodriguez|Agile methodologies|EXPERIENCED_IN|Maria Rodriguez has 8 years experience with Agile|0.8)
("relationship"|Maria Rodriguez|e-commerce platform|BUILT|Maria Rodriguez built an e-commerce platform|0.8)
("relationship"|e-commerce platform|React|BUILT_WITH|e-commerce platform was built using React|0.8)
("relationship"|e-commerce platform|Node.js|BUILT_WITH|e-commerce platform was built using Node.js|0.8)
("relationship"|e-commerce platform|AWS|DEPLOYED_ON|e-commerce platform is deployed on AWS|0.8)"""
    },
    "relationship-extraction": {
        "entity_types": "PERSON, ORGANIZATION, LOCATION, TECHNOLOGY, SKILL, CERTIFICATION, EDUCATION, PROJECT",
        "relationship_types": "WORKS_FOR, STUDIED_AT, CERTIFIED_BY, SKILLED_IN, BUILT, USES, GRADUATED_FROM, EMPLOYED_BY, DEVELOPED, MANAGED, LEADS, SPECIALIZES_IN, EXPERIENCED_IN, HOLDS_DEGREE_IN, BUILT_WITH, DEPLOYED_ON, INTEGRATES_WITH, LEVERAGES, COMPOSED_OF",
        "normalization_rules": """Resume-specific relationship normalization:
- Use consistent relationship types from the allowed list
- Prefer specific relationship types over generic RELATED_TO
- Map employment history to WORKS_FOR or EMPLOYED_BY
- Map educational background to STUDIED_AT or GRADUATED_FROM
- Map certifications to CERTIFIED_BY or holds certification relationships
- Map technical skills to SKILLED_IN, USES, or EXPERIENCED_IN
- Map project work to BUILT, DEVELOPED, or MANAGED""",
        "relationship_guidelines": """Resume-specific relationship guidelines:
- WORKS_FOR/EMPLOYED_BY: Current or past employment relationships, include job titles and duration when available
- STUDIED_AT/GRADUATED_FROM: Educational institution relationships, distinguish between current study and completed degrees
- CERTIFIED_BY: Professional certification relationships, include certification dates when available
- SKILLED_IN/EXPERIENCED_IN: Technology or skill proficiency relationships, indicate experience level when mentioned
- BUILT/DEVELOPED: Project or product creation relationships, include role and technologies used
- USES: Technology usage in professional context, indicate proficiency level
- MANAGED/LEADS: Leadership or management relationships, include team size and scope when available
- SPECIALIZES_IN: Areas of expertise or specialization
- HOLDS_DEGREE_IN: Academic degree relationships
- BUILT_WITH: Projects built using specific technologies or frameworks
- DEPLOYED_ON: Projects deployed on specific platforms or cloud services
- INTEGRATES_WITH: Systems or projects that integrate with other technologies
- LEVERAGES: Projects that leverage or utilize specific technologies or methodologies

Important: Create direct relationships between projects and technologies, not just person-to-technology relationships. For example:
- Person → DEVELOPED → Project
- Project → USES → Technology
- Project → DEPLOYED_ON → Platform""",
        "examples": """Resume Relationship Extraction Examples:

Example 1 - Software Engineer Career Path:
Text: "Alice Johnson is a Senior Software Engineer at TechCorp with 8 years of experience. She previously worked as a Software Developer at StartupXYZ for 3 years, where she built microservices using Java and Spring Boot. Alice graduated from MIT with a Master's degree in Computer Science and is certified as AWS Solutions Architect and Scrum Master. She specializes in distributed systems and cloud architecture."
Output:
("entity"|Alice Johnson|PERSON|Senior Software Engineer with 8 years experience, specializes in distributed systems and cloud architecture)
("entity"|TechCorp|ORGANIZATION|Technology company)
("entity"|StartupXYZ|ORGANIZATION|Technology startup company)
("entity"|Java|TECHNOLOGY|Object-oriented programming language)
("entity"|Spring Boot|TECHNOLOGY|Java-based application framework)
("entity"|MIT|EDUCATION|Massachusetts Institute of Technology)
("entity"|Computer Science|SKILL|Academic field and professional discipline)
("entity"|AWS Solutions Architect|CERTIFICATION|Cloud architecture certification)
("entity"|Scrum Master|CERTIFICATION|Agile project management certification)
("entity"|distributed systems|SKILL|Software architecture specialization)
("entity"|cloud architecture|SKILL|Cloud computing design specialization)
("relationship"|Alice Johnson|TechCorp|WORKS_FOR|Alice Johnson currently works as Senior Software Engineer at TechCorp|0.9)
("relationship"|Alice Johnson|StartupXYZ|EMPLOYED_BY|Alice Johnson previously worked as Software Developer at StartupXYZ for 3 years|0.8)
("relationship"|Alice Johnson|Java|USES|Alice Johnson uses Java for building microservices|0.8)
("relationship"|Alice Johnson|Spring Boot|USES|Alice Johnson uses Spring Boot framework for development|0.8)
("relationship"|Alice Johnson|MIT|GRADUATED_FROM|Alice Johnson graduated from MIT with Master's degree|0.9)
("relationship"|Alice Johnson|Computer Science|HOLDS_DEGREE_IN|Alice Johnson holds Master's degree in Computer Science|0.9)
("relationship"|Alice Johnson|AWS Solutions Architect|CERTIFIED_BY|Alice Johnson is certified as AWS Solutions Architect|0.9)
("relationship"|Alice Johnson|Scrum Master|CERTIFIED_BY|Alice Johnson is certified as Scrum Master|0.9)
("relationship"|Alice Johnson|distributed systems|SPECIALIZES_IN|Alice Johnson specializes in distributed systems|0.8)
("relationship"|Alice Johnson|cloud architecture|SPECIALIZES_IN|Alice Johnson specializes in cloud architecture|0.8)

Example 2 - Data Science Career with Project-Technology Relationships:
Text: "Dr. Michael Rodriguez leads the Data Science team at FinanceCorpAI, managing 12 data scientists and ML engineers. He earned his PhD in Statistics from Stanford University and has 10 years of experience in machine learning. Michael developed TalkerAI, an AI-powered voice assistant that uses GPT-4, Deepgram for speech-to-text, and ElevenLabs for text-to-speech. The system is built with FastAPI and deployed on AWS using Docker containers. He also created a fraud detection system that leverages TensorFlow and PyTorch for deep learning models."
Output:
("entity"|Dr. Michael Rodriguez|PERSON|Data Science team lead with PhD in Statistics, 10 years ML experience, manages 12 team members)
("entity"|FinanceCorpAI|ORGANIZATION|Financial technology company with AI focus)
("entity"|Stanford University|EDUCATION|Private research university in California)
("entity"|Statistics|SKILL|Mathematical field focused on data analysis)
("entity"|TalkerAI|PROJECT|AI-powered voice assistant for sales with real-time conversation capabilities)
("entity"|GPT-4|TECHNOLOGY|Large language model developed by OpenAI)
("entity"|Deepgram|TECHNOLOGY|Speech-to-text platform for transcription and voice recognition)
("entity"|ElevenLabs|TECHNOLOGY|Text-to-speech platform for generating natural-sounding voices)
("entity"|FastAPI|TECHNOLOGY|Web framework for building APIs with Python)
("entity"|AWS|TECHNOLOGY|Amazon Web Services cloud computing platform)
("entity"|Docker|TECHNOLOGY|Platform for developing, shipping, and running applications in containers)
("entity"|fraud detection system|PROJECT|ML system for detecting fraudulent transactions)
("entity"|TensorFlow|TECHNOLOGY|Open-source machine learning framework)
("entity"|PyTorch|TECHNOLOGY|Machine learning library for Python)
("relationship"|Dr. Michael Rodriguez|FinanceCorpAI|WORKS_FOR|Dr. Michael Rodriguez leads Data Science team at FinanceCorpAI|0.9)
("relationship"|Dr. Michael Rodriguez|Stanford University|GRADUATED_FROM|Dr. Michael Rodriguez earned PhD from Stanford University|0.9)
("relationship"|Dr. Michael Rodriguez|Statistics|HOLDS_DEGREE_IN|Dr. Michael Rodriguez holds PhD in Statistics|0.9)
("relationship"|Dr. Michael Rodriguez|TalkerAI|DEVELOPED|Dr. Michael Rodriguez developed TalkerAI voice assistant|0.9)
("relationship"|Dr. Michael Rodriguez|fraud detection system|DEVELOPED|Dr. Michael Rodriguez created fraud detection system|0.9)
("relationship"|TalkerAI|GPT-4|USES|TalkerAI uses GPT-4 for natural language processing|0.8)
("relationship"|TalkerAI|Deepgram|USES|TalkerAI uses Deepgram for speech-to-text processing|0.8)
("relationship"|TalkerAI|ElevenLabs|USES|TalkerAI uses ElevenLabs for text-to-speech processing|0.8)
("relationship"|TalkerAI|FastAPI|BUILT_WITH|TalkerAI is built with FastAPI web framework|0.8)
("relationship"|TalkerAI|AWS|DEPLOYED_ON|TalkerAI is deployed on AWS cloud platform|0.8)
("relationship"|TalkerAI|Docker|USES|TalkerAI uses Docker for containerization|0.8)
("relationship"|fraud detection system|TensorFlow|USES|fraud detection system leverages TensorFlow for deep learning|0.8)
("relationship"|fraud detection system|PyTorch|USES|fraud detection system leverages PyTorch for ML models|0.8)

Example 3 - Complex Project Architecture:
Text: "Sarah Kim developed a comprehensive e-commerce platform at RetailTech Inc. The platform consists of multiple microservices: a user authentication service built with Node.js and MongoDB, a product catalog service using Python and PostgreSQL, and a payment processing service integrating with Stripe API. The entire system is containerized with Docker and orchestrated using Kubernetes on Google Cloud Platform. The frontend is built with React and Redux, while the backend APIs use GraphQL for efficient data fetching."
Output:
("entity"|Sarah Kim|PERSON|Software engineer who developed comprehensive e-commerce platform with microservices architecture)
("entity"|RetailTech Inc|ORGANIZATION|Retail technology company)
("entity"|e-commerce platform|PROJECT|Comprehensive online retail platform with microservices architecture)
("entity"|user authentication service|PROJECT|Microservice handling user login and authentication)
("entity"|product catalog service|PROJECT|Microservice managing product information and inventory)
("entity"|payment processing service|PROJECT|Microservice handling payment transactions)
("entity"|Node.js|TECHNOLOGY|JavaScript runtime for server-side development)
("entity"|MongoDB|TECHNOLOGY|NoSQL document database)
("entity"|Python|TECHNOLOGY|High-level programming language)
("entity"|PostgreSQL|TECHNOLOGY|Open-source relational database)
("entity"|Stripe API|TECHNOLOGY|Payment processing API service)
("entity"|Docker|TECHNOLOGY|Platform for developing, shipping, and running applications in containers)
("entity"|Kubernetes|TECHNOLOGY|Container orchestration platform)
("entity"|Google Cloud Platform|TECHNOLOGY|Cloud computing services by Google)
("entity"|React|TECHNOLOGY|JavaScript library for building user interfaces)
("entity"|Redux|TECHNOLOGY|State management library for JavaScript applications)
("entity"|GraphQL|TECHNOLOGY|Query language and runtime for APIs)
("relationship"|Sarah Kim|RetailTech Inc|WORKS_FOR|Sarah Kim works as software engineer at RetailTech Inc|0.9)
("relationship"|Sarah Kim|e-commerce platform|DEVELOPED|Sarah Kim developed comprehensive e-commerce platform|0.9)
("relationship"|e-commerce platform|user authentication service|COMPOSED_OF|e-commerce platform consists of user authentication service|0.9)
("relationship"|e-commerce platform|product catalog service|COMPOSED_OF|e-commerce platform consists of product catalog service|0.9)
("relationship"|e-commerce platform|payment processing service|COMPOSED_OF|e-commerce platform consists of payment processing service|0.9)
("relationship"|user authentication service|Node.js|BUILT_WITH|user authentication service is built with Node.js|0.8)
("relationship"|user authentication service|MongoDB|USES|user authentication service uses MongoDB for data storage|0.8)
("relationship"|product catalog service|Python|BUILT_WITH|product catalog service is built with Python|0.8)
("relationship"|product catalog service|PostgreSQL|USES|product catalog service uses PostgreSQL database|0.8)
("relationship"|payment processing service|Stripe API|INTEGRATES_WITH|payment processing service integrates with Stripe API|0.8)
("relationship"|e-commerce platform|Docker|USES|e-commerce platform is containerized with Docker|0.8)
("relationship"|e-commerce platform|Kubernetes|DEPLOYED_ON|e-commerce platform is orchestrated using Kubernetes|0.8)
("relationship"|e-commerce platform|Google Cloud Platform|DEPLOYED_ON|e-commerce platform runs on Google Cloud Platform|0.8)
("relationship"|e-commerce platform|React|BUILT_WITH|e-commerce platform frontend is built with React|0.8)
("relationship"|e-commerce platform|Redux|USES|e-commerce platform uses Redux for state management|0.8)
("relationship"|e-commerce platform|GraphQL|USES|e-commerce platform backend APIs use GraphQL|0.8)"""
    },
    "claim-extraction": {
        "entity_specs": "PERSON, ORGANIZATION, TECHNOLOGY, SKILL, CERTIFICATION, PROJECT, EDUCATION",
        "claim_description": """Resume-specific claims to extract:
- Professional achievements and accomplishments
- Work experience and employment history
- Educational background and degrees earned
- Professional certifications and licenses
- Technical skills and proficiency levels
- Project contributions and leadership roles
- Years of experience in specific technologies or domains
- Team management and leadership experience
- Publications, patents, or research contributions
- Awards, recognitions, or performance metrics"""
    },
    "entity-merging": {
        "allowed_entity_types": "PERSON, ORGANIZATION, LOCATION, TECHNOLOGY, SKILL, CERTIFICATION, EDUCATION, PROJECT",
        "entity_type_mappings": """Resume-specific entity type mappings:
- UNIVERSITY/COLLEGE/SCHOOL/INSTITUTE → EDUCATION
- COMPANY/CORPORATION/STARTUP/FIRM/AGENCY → ORGANIZATION  
- PROGRAMMING_LANGUAGE/FRAMEWORK/LIBRARY/TOOL/PLATFORM → TECHNOLOGY
- CITY/STATE/COUNTRY/REGION → LOCATION
- DEGREE/MAJOR/FIELD_OF_STUDY → SKILL or EDUCATION
- CERTIFICATE/LICENSE/CREDENTIAL → CERTIFICATION
- APPLICATION/SYSTEM/PRODUCT/SOLUTION → PROJECT""",
        "key_attributes": """Resume-specific key attributes to preserve:
- Job titles and roles
- Years of experience and employment duration
- Skill levels and proficiency ratings
- Certification dates and validity periods
- Education degrees and graduation dates
- Project descriptions and technologies used
- Team sizes managed and leadership scope
- Geographic locations of work or education
- Industry sectors and company sizes
- Performance metrics and achievements"""
    },
    "entity-normalization": {
        "entity_types": "PERSON, ORGANIZATION, LOCATION, TECHNOLOGY, SKILL, CERTIFICATION, EDUCATION, PROJECT",
        "normalization_rules": """Resume-specific entity normalization rules:
- Use full official company names (e.g., "Microsoft Corporation" not "MSFT" or "MS")
- Use complete university names (e.g., "Stanford University" not "Stanford")
- Standardize technology names to canonical forms (e.g., "JavaScript" not "JS")
- Use official certification names (e.g., "AWS Certified Solutions Architect")
- Normalize job titles to standard forms (e.g., "Software Engineer" not "SWE")
- Preserve degree levels and specializations (e.g., "Master's in Computer Science")
- Use consistent project naming with descriptive titles
- Maintain skill categories and proficiency levels
- Standardize location names (e.g., "San Francisco, California" not "SF, CA")""",
        "language": "English",
        "entities": "[]",
        "relationships": "[]",
        "entity_mappings": {
            "Hassan University": "Hassan University 1st",
            "CDG-DXC": "CDG",
            "Faculty of Sciences Dhar El Mahraz": "Faculty of Sciences and Techniques, Mohammed IA",
            "Apache Spark": "Spark",
            "LLMs": "Machine Learning",
            "IRIS Dataset Classification": "Statistical Analysis",
            "MIT": "Massachusetts Institute of Technology",
            "Stanford": "Stanford University",
            "Google": "Google LLC",
            "Microsoft": "Microsoft Corporation",
            "AWS": "Amazon Web Services",
            "JS": "JavaScript",
            "React": "React.js",
            "Node": "Node.js",
            "ML": "Machine Learning",
            "AI": "Artificial Intelligence",
            "CS": "Computer Science",
            "SWE": "Software Engineer",
            "PM": "Project Manager",
            "CEO": "Chief Executive Officer",
            "CTO": "Chief Technology Officer"
        }
    }
}

def configure_resume_domain(gateway):
    """Configure the LLMGateway for resume/CV parsing domain."""
    gateway.configure_domain_defaults(RESUME_DOMAIN_CONFIG)
    return gateway