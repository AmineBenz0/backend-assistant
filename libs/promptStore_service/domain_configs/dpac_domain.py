"""
DPaC domain configuration for Graph Builder.

This module provides domain-specific defaults for DPaC 
(Digitalizzazione Patrimonio Culturale - Digitization of Cultural Heritage) project documents.
It defines entities, relationships, and rules specific to the DPaC platform and its operational workflows.
"""

from typing import Dict, Any

# DPaC-specific domain configuration
DPAC_DOMAIN_CONFIG: Dict[str, Dict[str, Any]] = {
    "out-of-context-detection": {
        "topics": [
            "DPaC Platform Operations & Governance: How to use the platform, its modules, user roles (PM, BM, RI, ROP), and project structure.",
            "Digitization Project Lifecycle & Workflow: The phases, administrative procedures, documentation (Workplan di Cantiere, Verbale di Inizio Lavori), and assets involved in a DPaC project.",
            "Technical Specifications & Quality Control: Requirements for files, metadata, image quality, and the testing (collaudo) process including METS validation.",
            "User Support & System Interaction: Helpdesk procedures, communication protocols, and integration with I.PaC platform.",
            "DPaC System Modules: Modulo di Pianificazione, Modulo di Collaudo, Modulo di Gestione Documentale and their functionalities.",
            "PNRR Digitization Project: Italian National Recovery and Resilience Plan's cultural heritage digitalization initiative.",
            "Cultural Heritage Institutions: Museums, archives, libraries, and cultural sites involved in digitization projects including archaeological museums, historical sites, and heritage preservation institutions.",
            "Italian Cultural Heritage Organizations: Questions about MiC (Ministero della Cultura), ICDP (Istituto Centrale per la Digitalizzazione del Patrimonio Culturale), Digital Library, and other cultural heritage institutions and organizations.",
            "DPaC Project Stakeholders: Information about implementing bodies (Soggetti Attuatori), contractors, regional authorities, and all organizations involved in the digitization project.",
            "Cultural Heritage Digitization: Questions about digitization processes, cultural assets, museums, archives, libraries, archaeological sites, and heritage preservation.",
            "Italian Museums and Cultural Sites: Questions about specific museums like Museo Archeologico Nazionale, cultural institutions, and heritage sites in Italy."
        ]
    },
    "sensitive-topics-detection": {
        "topics": [
            "Technical Digitization Process: XML file structure, metadata creation, image quality requirements, METS validation, file formats (TIFF with LZW compression)",
            "Administrative Procedures: Tender documentation, documentazione di gara, project manuals, pre-DPaC procedures, Framework Agreements (Accordi Quadro), Activation Orders (OdA)",
            "External Systems Integration: ReGiS system, I.PaC platform integration, M2M (Machine-to-Machine) and H2W (Human-to-Widget) interaction models",
            "Regional Support and Coordination: Supporto regioni, regional authority interactions, FAQs from regions (Lombardy, Sardinia, Tuscany), SAL mensili meetings",
            "PNRR Digitization Project: Italian National Recovery and Resilience Plan's cultural heritage digitalization initiative (Mission 1, Component 3, Investment 1.1.5)",
            "Project Governance and Roles: RUP (Single Person Responsible), PM, BM, RI, ROP roles and responsibilities, Implementing Bodies (Soggetti Attuatori), Digital Library operations",
            "Contractual Procedures: Specific Contracts (Contratti Specifici), work progress reporting (SAL), DUVRI (Single Document for Risk Assessment)",
            "Digitization Technical Specifications: Profilo applicativo METS ECO-MIC, procedures for archival documents, photographs, museum objects, microfilm digitization",
            "Cultural Assets Scope: Specific cultural assets from National Archaeological Museum of Florence, National Museum of San Matteo in Pisa, General Cadastre of Tuscany",
            "DPaC System Operations: Modulo di Pianificazione, Modulo di Collaudo, Modulo di Gestione Documentale, platform maintenance and notifications"
        ]
    },
    "nl2cypher": {
        "schema": """
Node Types:
- ROLE: PM, BM, RI, ROP, OP, DIR, PO (Project roles)
- SYSTEM: DPaC (main platform)
- SYSTEM_MODULE: Modulo di Pianificazione, Modulo di Collaudo, Modulo di Gestione Documentale
- DOCUMENT: Workplan di Cantiere, Verbale di Inizio Lavori, Checklist di Collaudo, Report Scartati
- PROCESS: Digitalizzazione, Validazione METS, Collaudo
- CONCEPT: Cantiere, Pacchetto Digitale, Lotto di Prototipazione, Disservizio
- ORGANIZATION: MiC, ICDP, Servizio di supporto DPaC, Museums, Archives
- PERSON: Individual users with specific roles
- PLAN: PNRR, PND

Relationship Types:
- CREATES, USES, MANAGES, APPROVES, VERIFIES, SIGNS, PERFORMS, COORDINATES
- MONITORS, SUPPORTS, IS_PART_OF, HAS_MODULE, SENDS_NOTIFICATION
- ANALYZES, REPORTS_ERRORS_OF, UNDERGOES, RELATED_TO

Node Properties (exclude "description_embedding"):
- id, name, type, description, role_acronym, full_name, status, created_at, updated_at

Important: To exclude the description_embedding property, use one of these patterns:
- RETURN org {.name, .type, .description} (explicit properties)
- RETURN apoc.map.removeKey(properties(org), 'description_embedding') AS org (using APOC function)
- RETURN org (and filter out description_embedding in post-processing)
        """,
        "example": """
{
  "cypher": "MATCH (org:ORGANIZATION) WHERE org.name = 'ICDP' RETURN apoc.map.removeKey(properties(org), 'description_embedding') AS organization",
  "explanation": "Find organization named ICDP and return all properties except description_embedding",
  "confidence_score": 0.95
}
        """
    },
    "extract-entities": {
        "entity_types": "ROLE, SYSTEM, SYSTEM_MODULE, DOCUMENT, PROCESS, CONCEPT, ORGANIZATION, PERSON, PLAN",
        "normalization_rules": """DPaC-specific entity normalization rules:
- Use acronyms for roles (e.g., PM, BM, RI, PO, DIR, ROP, OP).
- Use full Italian names for documents (e.g., "Workplan di Cantiere", "Verbale di Inizio Lavori").
- Standardize system module names as "Modulo di [Name]" (e.g., "Modulo di Pianificazione").
- Use official acronyms for plans and organizations (e.g., PNRR, PND, MiC, ICDP).
- The primary system should be referred to as "DPaC".""",
        "examples": """DPaC Entity Extraction Examples:

Example 1 - Project Planning Workflow:
Text: "Il Project Manager (PM) redige il Workplan di Cantiere nel Modulo di Gestione Documentale. Successivamente, il Business Manager (BM) valuta il Workplan. Una volta approvato dal Responsabile Istituto (RI), il PM firma digitalmente il documento. La piattaforma DPaC notifica al PM l'avvio della fase di preparazione, che include la redazione del Verbale di Inizio Lavori. Il ROP è responsabile per l'operatività della piattaforma."
Output:
("entity"|PM|ROLE|Project Manager, responsible for operational coordination and document creation)
("entity"|BM|ROLE|Business Manager, responsible for monitoring and validation)
("entity"|RI|ROLE|Responsabile Istituto, institutional representative with decision-making responsibility)
("entity"|ROP|ROLE|Responsabile dell'Operatività della Piattaforma, responsible for platform operations and support)
("entity"|Workplan di Cantiere|DOCUMENT|Detailed plan of the activities foreseen at the digitization site)
("entity"|Verbale di Inizio Lavori|DOCUMENT|Official record marking the start of work at the site)
("entity"|Modulo di Gestione Documentale|SYSTEM_MODULE|DPaC module for creating and archiving project documents)
("entity"|DPaC|SYSTEM|Platform for the Digitization of Cultural Heritage)
("relationship"|PM|Workplan di Cantiere|CREATES|The PM is responsible for creating the Workplan di Cantiere|0.9)
("relationship"|PM|Modulo di Gestione Documentale|USES|The PM uses the Document Management Module to create the Workplan|0.8)
("relationship"|BM|Workplan di Cantiere|VERIFIES|The BM evaluates the Workplan created by the PM|0.8)
("relationship"|RI|Workplan di Cantiere|APPROVES|The RI approves the Workplan|0.9)
("relationship"|PM|Workplan di Cantiere|SIGNS|The PM digitally signs the approved Workplan|0.9)
("relationship"|ROP|DPaC|MANAGES|The ROP is responsible for the operationality of the DPaC platform|0.9)
("relationship"|DPaC|PM|SENDS_NOTIFICATION|The DPaC platform notifies the PM about the start of the preparation phase|0.8)

Example 2 - Validation and Testing Process:
Text: "Nel Modulo di Collaudo, il BM verifica i pacchetti digitali scartati, analizzando il Report Scartati per errori di validazione METS. Ogni lotto di prototipazione deve essere collaudato con esito positivo prima di procedere con la digitalizzazione su larga scala."
Output:
("entity"|Modulo di Collaudo|SYSTEM_MODULE|DPaC module dedicated to quality control of digitized products)
("entity"|BM|ROLE|Business Manager, responsible for monitoring and validation)
("entity"|Pacchetto Digitale|CONCEPT|A package of digital content to be validated)
("entity"|Report Scartati|DOCUMENT|Report detailing packages that failed antivirus or METS validation checks)
("entity"|Validazione METS|PROCESS|A technical check to validate the structure of METS files in a package)
("entity"|Lotto di Prototipazione|CONCEPT|A prototype batch used to test the digitization process)
("relationship"|BM|Modulo di Collaudo|USES|The BM uses the Validation Module to check digital packages|0.9)
("relationship"|BM|Report Scartati|ANALYZES|The BM analyzes the Discarded Report to identify errors|0.8)
("relationship"|Report Scartati|Validazione METS|REPORTS_ERRORS_OF|The Discarded Report details errors from METS validation|0.9)
("relationship"|Lotto di Prototipazione|Collaudo|UNDERGOES|The prototype batch must undergo and pass the validation process|0.9)
"""
    },
    "relationship-extraction": {
        "entity_types": "ROLE, SYSTEM, SYSTEM_MODULE, DOCUMENT, PROCESS, CONCEPT, ORGANIZATION, PERSON, PLAN",
        "relationship_types": "USES, MANAGES, CREATES, APPROVES, VERIFIES, SIGNS, PERFORMS, COORDINATES, MONITORS, SUPPORTS, IS_PART_OF, HAS_MODULE, SENDS_NOTIFICATION, ANALYZES, REPORTS_ERRORS_OF, UNDERGOES",
        "normalization_rules": """DPaC-specific relationship normalization:
- Use consistent relationship types from the allowed list.
- Map operational tasks to specific verbs: PM `CREATES` documents, BM `VERIFIES` quality, RI `APPROVES` plans.
- A system module `IS_PART_OF` the DPaC system.
- A Role `USES` a System or System Module to `PERFORM` a Process.
- A Document `UNDERGOES` a Process like `VERIFIES` or `APPROVES`.""",
        "relationship_guidelines": """DPaC-specific relationship guidelines:
- `CREATES`: Used when a role is responsible for the authoring of a document (e.g., PM `CREATES` Workplan).
- `VERIFIES`: Used when a role performs a quality check or validation (e.g., BM `VERIFIES` Checklist).
- `APPROVES`: Used for formal approval steps in the workflow (e.g., RI `APPROVES` Workplan).
- `USES`: Connects a role to a system or module they operate (e.g., PM `USES` Modulo Pianificazione).
- `PERFORMS`: Connects a role to a process they execute (e.g., OP `PERFORMS` Upload).
- `IS_PART_OF`: Connects modules to the main DPaC system.
- `SENDS_NOTIFICATION`: Describes the system sending alerts or notifications to roles.""",
        "examples": """DPaC Relationship Extraction Examples:

Example 1 - Communication for Service Disruption:
Text: "Per comunicazioni di disservizio, una Notifica di Manutenzione Straordinaria viene inviata dal Servizio di supporto DPaC. La mail deve essere inviata al gruppo DPaC-Supporto, che include gli utenti DL e Helpdesk."
Output:
("entity"|Disservizio|CONCEPT|Service Disruption)
("entity"|Notifica di Manutenzione Straordinaria|DOCUMENT|Notification for extraordinary maintenance)
("entity"|Servizio di supporto DPaC|ORGANIZATION|The DPaC support service team)
("entity"|Mail|CONCEPT|Email communication)
("entity"|DPaC-Supporto|ROLE|A distribution list for support users)
("entity"|Utenti DL|ROLE|Users with the DL role)
("entity"|Helpdesk|ROLE|Users with the Helpdesk role)
("relationship"|Servizio di supporto DPaC|Notifica di Manutenzione Straordinaria|SENDS_NOTIFICATION|The DPaC support service sends maintenance notifications|0.9)
("relationship"|Notifica di Manutenzione Straordinaria|Disservizio|RELATED_TO|The notification is related to a service disruption|0.8)
("relationship"|Utenti DL|DPaC-Supporto|IS_PART_OF|DL users are part of the DPaC-Support group|0.9)
("relationship"|Helpdesk|DPaC-Supporto|IS_PART_OF|Helpdesk users are part of the DPaC-Support group|0.9)
"""
    },
    "claim-extraction": {
        "entity_specs": "ROLE, PROCESS, DOCUMENT, SYSTEM_MODULE",
        "claim_description": """DPaC-specific claims to extract:
- Responsibilities of a specific role (e.g., "The PM must create the Workplan").
- The status or outcome of a process (e.g., "The validation of the METS file failed").
- Requirements or rules for a document (e.g., "The checklist must be approved by the BM").
- State or availability of a system module (e.g., "The service may not be available during maintenance").
- Instructions or steps in a procedure (e.g., "To export data, click the 'Esporta' button")."""
    },
    "entity-merging": {
        "allowed_entity_types": "ROLE, SYSTEM, SYSTEM_MODULE, DOCUMENT, PROCESS, CONCEPT, ORGANIZATION, PERSON, PLAN",
        "entity_type_mappings": """DPaC-specific entity type mappings:
- "Project Manager" -> ROLE
- "Business Manager" -> ROLE
- "Responsabile Istituto" -> ROLE
- "Piattaforma DPaC" -> SYSTEM
- "Checklist di Collaudo" -> DOCUMENT
- "Modulo di Pianificazione" -> SYSTEM_MODULE
- "Digitalizzazione" -> PROCESS
- "Cantiere" -> CONCEPT
- "Digital Library" -> ORGANIZATION""",
        "key_attributes": "role acronyms, full document names, module names, process steps, system names"
    },
    "entity-normalization": {
        "entity_types": "ROLE, SYSTEM, SYSTEM_MODULE, DOCUMENT, PROCESS, CONCEPT, ORGANIZATION, PERSON, PLAN",
        "normalization_rules": """DPaC-specific entity normalization rules:
- Canonicalize roles to their acronyms: "Project Manager" becomes "PM", "Business Manager" becomes "BM", "Responsabile Istituto" becomes "RI".
- Use full official names for documents: "Verbale inizio lavori" becomes "Verbale di Inizio Lavori".
- Standardize module names: "modulo di collaudo" becomes "Modulo di Collaudo".
- Use the acronym "DPaC" for "Piattaforma di Digitalizzazione del patrimonio culturale".""",
    }
}

def configure_dpac_domain(gateway):
    """Configure the LLMGateway for the DPaC domain."""
    gateway.configure_domain_defaults(DPAC_DOMAIN_CONFIG)
    return gateway