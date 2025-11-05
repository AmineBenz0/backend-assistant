"""
D.PaC domain configuration for Graph Builder.

This module provides domain-specific defaults for D.PaC 
(Digitalizzazione Patrimonio Culturale - Digitization of Cultural Heritage) project documents.
It defines entities, relationships, and rules specific to the D.PaC platform and its operational workflows,
including its interactions with related systems like I.PaC, DPaaS, and ServiceNow.
"""

from typing import Dict, Any


# TODO: make vector_schema and sql_schema dynamic too with the schema snapshot and then delete the static schemas
vector_schema = """
            id (string, unique) → links to Node.id in the graph when applicable.
            title (string) → short title of the content (e.g. “Verbale di Inizio Lavori”).
            content (text, embedded) → the full textual content (workplans, reports, checklists, etc.).
            embedding (vector) → dense embedding of content for semantic similarity.
        """

# TODO: make vector_schema and sql_schema dynamic too with the schema snapshot and then delete the static schemas
sql_schema = """Tables: 
                    projects(id, name, plan_type, start_date, end_date, location_id, manager_id), 
                    documents(id, title, doc_type, created_at, author_id, project_id), 
                    people(id, full_name, role, organization_id, email), 
                    organizations(id, name, org_type, city), 
                    locations(id, name, region, country). 
                
                Joins: 
                    documents.project_id -> projects.id, 
                    projects.manager_id -> people.id, 
                    people.organization_id -> organizations.id, 
                    projects.location_id -> locations.id
            """


# DPaC-specific domain configuration
EN_DPAC_DOMAIN_CONFIG: Dict[str, Dict[str, Any]] = {
    "out-of-context-detection": {
        "topics": [
            "General questions about DPaC/I.PaC: what is DPaC? what is I.PaC? meaning of the acronym DPaC/DPAC/D_PAC and platform overview.",
            "DPaC (aka dpac, DPAC, D_PAC) Platform Operations & Governance: How to use the platform, manage roles (PM, BM, RI, ROP), and understand project structure.",
            "Digitization Project Lifecycle & Workflow: Phases, documentation, and administrative steps in DPaC digitization projects.",
            "Technical Specifications & Quality Control: File requirements, metadata standards, image quality, and METS validation basics.",
            "User Support & System Interaction: Helpdesk procedures, communication protocols, and integration with the I.PaC platform.",
            "DPaC (aka dpac, DPAC, D_PAC) System Modules: Overview of Modulo di Pianificazione, Modulo di Collaudo, and Modulo di Gestione Documentale.",
            "PNRR Digitization Project: General information about Italy’s National Recovery and Resilience Plan for cultural heritage digitization.",
            "Cultural Heritage Institutions: Museums, archives, libraries, and cultural sites involved in digitization projects.",
            "Italian Cultural Heritage Organizations: MiC, ICDP, Digital Library, and related national institutions.",
            "DPaC (aka dpac, DPAC, D_PAC) Project Stakeholders: Implementing bodies, contractors, regional authorities, and associated organizations.",
            "Cultural Heritage Digitization: General questions about digitization processes and heritage preservation.",
            "Italian Museums and Cultural Sites: Questions about specific museums like Museo Archeologico Nazionale, cultural institutions, and heritage sites in Italy.",
            "Italian Cultural Heritage Geography,  Institutions, Artists(like Leonardo da Vinci, ...), Renaissance, Landmark(like Colosseum, ...), Locations: Questions about the location, history, or identity of Italian museums, cultural sites, historical influences, and heritage institutions such as the Gallerie dell’Accademia, Uffizi Gallery, or Museo Archeologico Nazionale.",
            "Italian Historical and Cultural Influences: Questions about the civilizations and cultures (e.g., Roman Empire, Renaissance, Etruscans, Greeks) that influenced Italy’s history, art, and heritage.",
            "general chat questions",
        ]
    },
    "sensitive-topics-detection": {
        "topics": [
            "Digitization Technical Details: XML structure, METS ECO-MIC profiles, metadata fields, file formats (TIFF LZW), and validation scripts.",
            "Administrative & Contractual Procedures: Tender documentation, Accordi Quadro, OdA (Activation Orders), DUVRI, and project contracts.",
            "External Systems Integration: ReGiS system, I.PaC platform integration, M2M (Machine-to-Machine) and H2W (Human-to-Widget) interactions.",
            "Regional Support and Coordination: Regional authority interactions, SAL meetings, and regional FAQs (e.g., Lombardy, Tuscany, Sardinia).",
            "Formal Governance Roles: Internal roles and responsibilities of RUP, PM, BM, RI, ROP, and Implementing Bodies (Soggetti Attuatori).",
            "DPaC Internal Operations: Backend maintenance, server configurations, or internal system logs. Exclude general questions about platform modules or user functionalities.",
        ]
    },
    "nl2cypher": {
        "schema": "",
        "example": """
{
  "cypher": "MATCH (s:SYSTEM)-[:INTEGRATES_WITH]->(t:SYSTEM) RETURN s.name AS source, t.name AS target LIMIT 10",
  "explanation": "Illustrative pattern-only example. Do not copy literal names from examples; use actual names from the live schema/context.",
  "confidence_score": 0.90
}
{
  "cypher": "MATCH (o:ORGANIZATION) WHERE toUpper(o.name) = toUpper('Some Org') RETURN o {.id, .name, .type, .description} AS organization",
  "explanation": "Demonstrates case-insensitive filtering and compact property selection.",
  "confidence_score": 0.88
}
        """
    },
    "query-rewriting": { 
        "schema": "",
        "vector_schema": vector_schema,
        "sql_schema": sql_schema,
    },
    "query-expansion": { 
        "schema": "",
        "vector_schema": vector_schema,
        "sql_schema": sql_schema,
        "domain_synonyms": """
        
        """
    },
    "query-decomposition": { 
        "schema": "",
        "vector_schema": vector_schema,
        "sql_schema": sql_schema,
    },
    "query-routing": { 
        "schema": "",
        "vector_schema": vector_schema,
        "sql_schema": sql_schema,
    },
    "extract-entities": {
        "entity_types": "ROLE, SYSTEM, TOOL, SYSTEM_MODULE, DOCUMENT, PROCESS, CONCEPT, ORGANIZATION, PERSON, PLAN, DATA_STANDARD",
        "normalization_rules": """D.PaC-specific entity normalization rules:
- Use acronyms for roles (e.g., PM, BM, RI, PO, DIR, ROP, OP) and support roles (e.g., PM supporto).
- Use full Italian names for documents (e.g., "Workplan di Cantiere", "Verbale di Inizio Lavori", "Verbale di Fine Lavori", "Ordine d'Acquisto", "Studio di Fattibilità").
- Standardize system module names as "Modulo di [Name]" (e.g., "Modulo di Pianificazione", "Modulo Descrittivo").
- Use official acronyms for plans and organizations (e.g., PNRR, PND, MiC, ICDP, ICCD, ICAR, ICCU).
- Canonicalize system names: "D_PAC" for the digitization platform, "I_PAC" for the core infrastructure, "DPAAS" for Data Product as a Service, "SERVICENOW" for the support portal.
- Canonicalize tool names: "Axway CFT" for the file transfer client, "Moodle" for the training platform.
- Use specific terminology for work packages: "Lotto di Digitalizzazione", "Lotto di Descrizione", "Lotto di Prototipazione".
- Standardize authentication methods: "SPID", "CIE", "LDAP".""",
        "examples": """D.PaC Entity Extraction Examples:

Example 1 - System Ecosystem:
Text: "Le risorse digitali prodotte dai cantieri di digitalizzazione vengono depositate nel Data Lake di I.PaC. La piattaforma D.PaC gestisce questo processo. Per supporto, gli utenti possono aprire un ticket sul Service Portal di ServiceNow."
Output:
("entity"|D_PAC|SYSTEM|Platform for managing the digitization of cultural heritage)
("entity"|I_PAC|SYSTEM|Core software infrastructure and data lake for cultural heritage)
("entity"|SERVICENOW|SYSTEM|Help desk and service portal for user support)
("entity"|Data Lake|CONCEPT|A centralized repository for storing large amounts of data)
("entity"|Cantiere di Digitalizzazione|CONCEPT|A digitization project site)
("entity"|Risorse Digitali|CONCEPT|Digital assets produced during the project)
("entity"|Ticket|DOCUMENT|A support request submitted by a user)
("relationship"|D_PAC|I_PAC|DEPOSITS_INTO|The D_PAC platform deposits digital resources into the I_PAC data lake|0.9)
("relationship"|I_PAC|DATA_LAKE|CONTAINS|The I_PAC infrastructure contains the data lake|0.8)
("relationship"|Cantiere di Digitalizzazione|Risorse Digitali|PRODUCES|Digitization sites produce digital resources|0.9)
("relationship"|UTENTE|SERVICENOW|USES|Users can open support tickets on the SERVICENOW portal|0.8)

Example 2 - Order for Purchase (OdA) Workflow:
Text: "Il BM crea un nuovo Ordine d'Acquisto (OdA) per il cluster. L'OdA viene poi inviato in approvazione al PO. Il PO può approvare o respingere l'OdA. Il monitoraggio del budget e del borsellino è visibile nel Modulo di Rendicontazione e Gestione OdA."
Output:
("entity"|BM|ROLE|Business Manager, responsible for creating and submitting Orders for Purchase)
("entity"|PO|ROLE|Project Owner, responsible for approving Orders for Purchase)
("entity"|Ordine d'Acquisto (OdA)|DOCUMENT|An official order for services or goods related to the project)
("entity"|Cluster|CONCEPT|A logical grouping of digitization sites)
("entity"|Budget|CONCEPT|The overall financial allocation for the project)
("entity"|Borsellino|CONCEPT|A sub-budget or wallet allocated for specific activities)
("entity"|Modulo di Rendicontazione e Gestione OdA|SYSTEM_MODULE|The D.PaC module for managing budgets and purchase orders)
("relationship"|BM|Ordine d'Acquisto (OdA)|CREATES|The BM creates new Orders for Purchase|0.9)
("relationship"|BM|PO|SUBMITS_FOR_APPROVAL|The BM submits the OdA to the PO for approval|0.9)
("relationship"|PO|Ordine d'Acquisto (OdA)|APPROVES|The PO is responsible for approving or rejecting the OdA|0.8)
("relationship"|BM|Modulo di Rendicontazione e Gestione OdA|USES|The BM uses the OdA module to monitor the budget|0.9)

Example 3 - Digitization Workflow with New Entities:
Text: "Il Lotto di Digitalizzazione è basato sul Prototipo approvato. Il PM supporto assiste nella creazione del Verbale di Fine Lavori che richiede la firma digitale del PM. Il processo di Recupero del Digitale Pregresso include uno Studio di Fattibilità."
Output:
("entity"|Lotto di Digitalizzazione|CONCEPT|A work package for digitization activities)
("entity"|Prototipo|CONCEPT|An approved prototype that serves as the basis for digitization lots)
("entity"|PM supporto|ROLE|A support role that assists the formal PM but does not hold final responsibility)
("entity"|PM|ROLE|Project Manager, responsible for project oversight and document signing)
("entity"|Verbale di Fine Lavori|DOCUMENT|The document certifying the completion of work at a digitization site)
("entity"|Firma Digitale|PROCESS|The official process of applying a digital signature to documents)
("entity"|Recupero del Digitale Pregresso|PROCESS|A workflow for recovering and integrating previously digitized materials)
("entity"|Studio di Fattibilità|DOCUMENT|A feasibility study document created for the recovery process)
("relationship"|Lotto di Digitalizzazione|Prototipo|IS_BASED_ON|Digitization lots are formally based on approved prototypes|0.9)
("relationship"|PM|PM supporto|HAS_SUPPORT_ROLE|The PM has a designated support counterpart|0.8)
("relationship"|Verbale di Fine Lavori|PM|REQUIRES_SIGNATURE_FROM|The completion document requires digital signature from the PM|0.9)
("relationship"|PM supporto|Verbale di Fine Lavori|CREATES|The PM support assists in creating the completion document|0.8)
("relationship"|Recupero del Digitale Pregresso|Studio di Fattibilità|CONTAINS|The recovery process includes a feasibility study|0.9)

Example 4 - Cultural Heritage Organizations and Standards:
Text: "L'ICCD assegna i codici NCTN per l'identificazione univoca dei beni culturali. Il Fondo A del dominio Storico-Artistico viene digitalizzato secondo le linee guida. Le Schede D vengono create nel Modulo Descrittivo."
Output:
("entity"|ICCD|ORGANIZATION|Istituto Centrale per il Catalogo e la Documentazione)
("entity"|NCTN|DATA_STANDARD|Unique identification codes for cultural heritage assets)
("entity"|Fondo A|CONCEPT|A specific collection or archive that is the subject of digitization)
("entity"|Storico-Artistico|CONCEPT|The historical-artistic cultural heritage domain)
("entity"|Linee guida|DOCUMENT|Official guidelines provided for various procedures)
("entity"|Scheda D|CONCEPT|A specific type of cataloging record created within the descriptive module)
("entity"|Modulo Descrittivo|SYSTEM_MODULE|The D.PaC module for descriptive cataloging)
("relationship"|ICCD|NCTN|ASSIGNS|ICCD assigns unique NCTN codes for cultural heritage identification|0.9)
("relationship"|Fondo A|Storico-Artistico|IS_PART_OF|Fund A belongs to the historical-artistic domain|0.8)
("relationship"|Modulo Descrittivo|Scheda D|PRODUCES|The descriptive module is used to create cataloging records|0.9)
("relationship"|Digitalizzazione|Linee guida|UNDERGOES|Digitization processes follow official guidelines|0.8)

Example 5 - Project Monitoring and Critical Issues:
Text: "Il Report Avanzamento Lotti generato dal modulo Business Intelligence mostra le Criticità del progetto. Una Segnalazione viene aperta nei Casi Aperti tra BM e PM per questioni amministrative. Il Gantt viene aggiornato per la Ripianificazione."
Output:
("entity"|Report Avanzamento Lotti|DOCUMENT|A report generated showing the progress of different work lots)
("entity"|Business Intelligence|SYSTEM_MODULE|The D.PaC module for generating analytical reports)
("entity"|Criticità|CONCEPT|A critical issue or problem that could impact the project timeline or quality)
("entity"|Segnalazione|CONCEPT|An official report or issue submitted through the open cases system)
("entity"|Casi Aperti|CONCEPT|The system for managing open administrative issues between roles)
("entity"|Gantt|CONCEPT|The project management chart used for planning and scheduling)
("entity"|Ripianificazione|PROCESS|The process of replanning project activities)
("relationship"|Business Intelligence|Report Avanzamento Lotti|PRODUCES|The BI module generates progress reports|0.9)
("relationship"|Report Avanzamento Lotti|Criticità|ANALYZES|The progress report analyzes critical project issues|0.8)
("relationship"|BM|Segnalazione|CREATES|The BM creates official reports for administrative issues|0.9)
("relationship"|Segnalazione|Casi Aperti|IS_PART_OF|Reports are managed within the open cases system|0.8)
("relationship"|Ripianificazione|Gantt|USES|The replanning process uses Gantt charts for scheduling|0.9)
"""

    },
    "relationship-extraction": {
        "entity_types": "ROLE, SYSTEM, TOOL, SYSTEM_MODULE, DOCUMENT, PROCESS, CONCEPT, ORGANIZATION, PERSON, PLAN, DATA_STANDARD",
        "relationship_types": "USES, MANAGES, CREATES, APPROVES, VERIFIES, SIGNS, PERFORMS, COORDINATES, MONITORS, SUPPORTS, IS_PART_OF, HAS_MODULE, SENDS_NOTIFICATION, ANALYZES, REPORTS_ERRORS_OF, UNDERGOES, RELATED_TO, INTEGRATES_WITH, DEPOSITS_INTO, SUBMITS_FOR_APPROVAL, TRANSFERS_WITH, PRODUCES, IS_BASED_ON, CONTAINS, TRIGGERS, HAS_STATUS, REQUIRES_SIGNATURE_FROM, ASSIGNS, MANAGES_BUDGET_OF, HAS_SUPPORT_ROLE",
        "normalization_rules": """D.PaC-specific relationship normalization:
- Use consistent relationship types from the allowed list.
- Map operational tasks to specific verbs: PM `CREATES` documents, BM `VERIFIES` quality, RI/PO `APPROVES` plans/orders.
- A SYSTEM_MODULE `IS_PART_OF` a larger SYSTEM (e.g., D_PAC).
- A ROLE `USES` a SYSTEM or TOOL to `PERFORM` a PROCESS.
- Use `INTEGRATES_WITH` for system-to-system connections.
- Use `DEPOSITS_INTO` for data flow relationships, like from D_PAC to I_PAC.
- Use `IS_BASED_ON` for formal dependencies (e.g., Lotto -> IS_BASED_ON -> Prototipo).
- Use `CONTAINS` for containment relationships (e.g., Cluster -> CONTAINS -> Cantiere).
- Use `HAS_SUPPORT_ROLE` to link formal roles with their support counterparts.""",
        "relationship_guidelines": """D.PaC-specific relationship guidelines:
- `CREATES`: Used when a role is responsible for the authoring of a document (e.g., PM `CREATES` Workplan).
- `VERIFIES`: Used when a role performs a quality check or validation (e.g., BM `VERIFIES` Checklist).
- `APPROVES`: Used for formal approval steps in the workflow (e.g., RI `APPROVES` Workplan; PO `APPROVES` OdA).
- `USES`: Connects a role to a system or tool they operate (e.g., PM `USES` MODULO_PIANIFICAZIONE; OP `USES` AXWAY_CFT).
- `INTEGRATES_WITH`: Describes a functional connection between two systems (e.g., D_PAC `INTEGRATES_WITH` SERVICENOW).
- `DEPOSITS_INTO`: Represents the action of placing data or resources into a repository or another system (e.g., D_PAC `DEPOSITS_INTO` I_PAC).
- `SUBMITS_FOR_APPROVAL`: Used when a role formally submits a document to another role for approval (e.g., BM `SUBMITS_FOR_APPROVAL` OdA to PO).
- `TRANSFERS_WITH`: Describes the use of a specific tool for data transfer (e.g., OP `TRANSFERS_WITH` Axway CFT).
- `IS_BASED_ON`: Indicates that one process or entity is formally based on another (e.g., Lotto di Digitalizzazione `IS_BASED_ON` Prototipo).
- `CONTAINS`: Describes a containment relationship (e.g., Cluster `CONTAINS` Cantiere; Lotto di Digitalizzazione `CONTAINS` Pacchetto Digitale).
- `TRIGGERS`: Represents an action or event that causes another process to start (e.g., Rifiuto Collaudo `TRIGGERS` Ripianificazione).
- `HAS_STATUS`: Assigns a state or status to a document or process (e.g., Workplan di Cantiere `HAS_STATUS` Approvato).
- `REQUIRES_SIGNATURE_FROM`: Specifies which role is required to digitally sign a document (e.g., Verbale di Fine Lavori `REQUIRES_SIGNATURE_FROM` PM).
- `ASSIGNS`: Indicates the action of assigning a code or resource (e.g., ICCD `ASSIGNS` NCTN).
- `MANAGES_BUDGET_OF`: Connects a role to the financial concept they manage (e.g., BM `MANAGES_BUDGET_OF` Cluster).
- `HAS_SUPPORT_ROLE`: Links a formal role to its designated support counterpart (e.g., PM `HAS_SUPPORT_ROLE` PM supporto).""",
        "examples": """D.PaC Relationship Extraction Examples:

Example 1 - Communication for Service Disruption:
Text: "Per comunicazioni di disservizio, una Notifica di Manutenzione Straordinaria viene inviata dal Servizio di supporto D.PaC. La mail deve essere inviata al gruppo D.PaC-Supporto, che include gli utenti DL e Helpdesk. Le segnalazioni possono essere gestite tramite il portale ServiceNow."
Output:
("entity"|Disservizio|CONCEPT|Service Disruption)
("entity"|Notifica di Manutenzione Straordinaria|DOCUMENT|Notification for extraordinary maintenance)
("entity"|Servizio di supporto D.PaC|ORGANIZATION|The D.PaC support service team)
("entity"|D.PaC-Supporto|ROLE|A distribution list for support users)
("entity"|Utenti DL|ROLE|Users with the DL role)
("entity"|ServiceNow|SYSTEM|Help desk and service portal for user support)
("relationship"|Servizio di supporto D.PaC|Notifica di Manutenzione Straordinaria|SENDS_NOTIFICATION|The D.PaC support service sends maintenance notifications|0.9)
("relationship"|Notifica di Manutenzione Straordinaria|Disservizio|RELATED_TO|The notification is related to a service disruption|0.8)
("relationship"|Utenti DL|D.PaC-Supporto|IS_PART_OF|DL users are part of the D.PaC-Support group|0.9)
("relationship"|Servizio di supporto D.PaC|ServiceNow|USES|The support service uses ServiceNow to manage issues|0.8)

Example 2 - Project Closure and Digital Signatures:
Text: "Durante la Chiusura Cantiere, il PM deve firmare digitalmente il Verbale di Fine Lavori. Il processo di Firma Digitale viene eseguito esternamente alla piattaforma D.PaC. Il Verbale ha stato 'Approvato' dopo la firma."
Output:
("entity"|Chiusura Cantiere|PROCESS|The final phase of a digitization project)
("entity"|PM|ROLE|Project Manager responsible for document signing)
("entity"|Firma Digitale|PROCESS|The official process of applying a digital signature to documents)
("entity"|Verbale di Fine Lavori|DOCUMENT|The document certifying the completion of work)
("entity"|D.PaC|SYSTEM|The digitization platform)
("entity"|Approvato|CONCEPT|An approval status for documents)
("relationship"|Chiusura Cantiere|Verbale di Fine Lavori|PRODUCES|The project closure phase produces the completion document|0.9)
("relationship"|Verbale di Fine Lavori|PM|REQUIRES_SIGNATURE_FROM|The completion document requires digital signature from the PM|0.9)
("relationship"|PM|Firma Digitale|PERFORMS|The PM performs the digital signature process|0.8)
("relationship"|Verbale di Fine Lavori|Approvato|HAS_STATUS|The document has an approved status after signing|0.9)

Example 3 - Work Package Dependencies and Budget Management:
Text: "Il Lotto di Digitalizzazione è basato sul Prototipo validato dal BM. Il BM gestisce il budget del Cluster che contiene più Cantieri. Il rifiuto del collaudo scatena la Ripianificazione del lotto."
Output:
("entity"|Lotto di Digitalizzazione|CONCEPT|A work package for digitization activities)
("entity"|Prototipo|CONCEPT|An approved prototype that serves as the basis for digitization lots)
("entity"|BM|ROLE|Business Manager responsible for validation and budget management)
("entity"|Budget|CONCEPT|The overall financial allocation for the project)
("entity"|Cluster|CONCEPT|A logical grouping of digitization sites)
("entity"|Cantiere|CONCEPT|Individual digitization project sites)
("entity"|Collaudo|PROCESS|The testing and validation process)
("entity"|Ripianificazione|PROCESS|The process of replanning project activities)
("relationship"|Lotto di Digitalizzazione|Prototipo|IS_BASED_ON|Digitization lots are formally based on validated prototypes|0.9)
("relationship"|BM|Prototipo|VERIFIES|The BM validates the prototype before lot creation|0.8)
("relationship"|BM|Budget|MANAGES_BUDGET_OF|The BM manages the financial allocation|0.9)
("relationship"|Cluster|Cantiere|CONTAINS|A cluster contains multiple digitization sites|0.9)
("relationship"|Collaudo|Ripianificazione|TRIGGERS|A failed testing process triggers replanning|0.8)

Example 4 - Cultural Heritage Cataloging and Standards:
Text: "L'ICCD assegna i codici NCTN per identificare i beni del Fondo Storico-Artistico. Le Schede UA vengono create nel Modulo Descrittivo seguendo la Nomenclatura specifica. Il dominio Archivistico ha procedure diverse."
Output:
("entity"|ICCD|ORGANIZATION|Istituto Centrale per il Catalogo e la Documentazione)
("entity"|NCTN|DATA_STANDARD|Unique identification codes for cultural heritage assets)
("entity"|Fondo|CONCEPT|A collection or archive that is the subject of digitization)
("entity"|Storico-Artistico|CONCEPT|The historical-artistic cultural heritage domain)
("entity"|Scheda UA|CONCEPT|A specific type of cataloging record)
("entity"|Modulo Descrittivo|SYSTEM_MODULE|The D.PaC module for descriptive cataloging)
("entity"|Nomenclatura|CONCEPT|The specific naming convention required for files and packages)
("entity"|Archivistico|CONCEPT|The archival cultural heritage domain)
("relationship"|ICCD|NCTN|ASSIGNS|ICCD assigns unique identification codes|0.9)
("relationship"|NCTN|Fondo|RELATED_TO|NCTN codes are used to identify assets in collections|0.8)
("relationship"|Fondo|Storico-Artistico|IS_PART_OF|The collection belongs to the historical-artistic domain|0.9)
("relationship"|Modulo Descrittivo|Scheda UA|PRODUCES|The descriptive module is used to create cataloging records|0.9)
("relationship"|Scheda UA|Nomenclatura|UNDERGOES|Cataloging records follow specific naming conventions|0.8)

Example 5 - Support Roles and File Transfer:
Text: "Il PM supporto assiste nella creazione del Report Avanzamento Lotti. L'OP utilizza il client Axway CFT per il Caricamento Pacchetti tramite Folder Monitoring. Il processo è automatizzato."
Output:
("entity"|PM supporto|ROLE|A support role that assists the formal PM)
("entity"|PM|ROLE|Project Manager with formal responsibility)
("entity"|Report Avanzamento Lotti|DOCUMENT|A report showing the progress of different work lots)
("entity"|OP|ROLE|Operator responsible for file transfers)
("entity"|Axway CFT|TOOL|File transfer client software)
("entity"|Caricamento Pacchetti|PROCESS|The specific action of uploading digital packages)
("entity"|Folder Monitoring|PROCESS|The automated process of uploading files)
("relationship"|PM|PM supporto|HAS_SUPPORT_ROLE|The PM has a designated support counterpart|0.9)
("relationship"|PM supporto|Report Avanzamento Lotti|CREATES|The support role assists in creating progress reports|0.8)
("relationship"|OP|Axway CFT|USES|The operator uses the file transfer client|0.9)
("relationship"|OP|Caricamento Pacchetti|PERFORMS|The operator performs the package upload process|0.9)
("relationship"|Caricamento Pacchetti|Folder Monitoring|USES|Package upload uses automated folder monitoring|0.8)
"""
    },
    "claim-extraction": {
        "entity_specs": "ROLE, PROCESS, DOCUMENT, SYSTEM, SYSTEM_MODULE, TOOL",
        "claim_description": """D.PaC-specific claims to extract:
- Responsibilities of a specific role (e.g., "The PM must create the Workplan").
- The status or outcome of a process (e.g., "The validation of the METS file failed").
- Requirements or rules for a document (e.g., "The checklist must be approved by the BM").
- State or availability of a system or module (e.g., "The service may not be available during maintenance").
- Instructions or steps in a procedure (e.g., "To export data from D.PaC, the user must click the 'Esporta' button").
- Capabilities or purpose of a system (e.g., "I.PaC is the data space designed to preserve and manage digital cultural heritage")."""
    },
    "entity-merging": {
        "allowed_entity_types": "ROLE, SYSTEM, TOOL, SYSTEM_MODULE, DOCUMENT, PROCESS, CONCEPT, ORGANIZATION, PERSON, PLAN, DATA_STANDARD",
        "entity_type_mappings": """D.PaC-specific entity type mappings:
- "Project Manager" OR "PM" -> ROLE
- "Business Manager" OR "BM" -> ROLE
- "Responsabile Istituto" OR "RI" -> ROLE
- "Project Manager supporto" OR "PM supporto" -> ROLE
- "Piattaforma D.PaC" OR "Piattaforma di Digitalizzazione del patrimonio culturale" -> SYSTEM
- "I.PaC" OR "Infrastruttura Software per il Patrimonio Culturale" -> SYSTEM
- "DPaaS" OR "Data Product as a Service" -> SYSTEM
- "ServiceNow" OR "Service Portal" -> SYSTEM
- "Cliente Axway" OR "Client Axway" OR "Axway CFT" -> TOOL
- "Checklist di Collaudo" OR "Checklist di Prototipazione" -> DOCUMENT
- "Verbale di Inizio Lavori" OR "Verbale di Fine Lavori" -> DOCUMENT
- "Studio di Fattibilità" OR "Report Avanzamento Lotti" -> DOCUMENT
- "Modulo di Pianificazione" OR "Modulo di Collaudo" OR "Modulo Descrittivo" -> SYSTEM_MODULE
- "Business Intelligence" OR "Modulo di Rendicontazione e Gestione OdA" -> SYSTEM_MODULE
- "Digitalizzazione" OR "Recupero del Digitale Pregresso" OR "Firma Digitale" -> PROCESS
- "Caricamento Pacchetti" OR "Folder Monitoring" OR "Chiusura Cantiere" -> PROCESS
- "Cantiere" OR "Lotto di Digitalizzazione" OR "Lotto di Descrizione" -> CONCEPT
- "Cluster" OR "Fondo" OR "Scheda" OR "Dominio" OR "Nomenclatura" -> CONCEPT
- "Digital Library" OR "ICCD" OR "ICAR" OR "ICCU" -> ORGANIZATION
- "METS" OR "NCTN" OR "CIE" OR "SPID" OR "LDAP" -> DATA_STANDARD""",
        "key_attributes": "role acronyms, full document names, module names, process steps, system names, platform names, tool names, work package types, cultural heritage domains, authentication methods"
    },
    "entity-normalization": {
        "entity_types": "ROLE, SYSTEM, TOOL, SYSTEM_MODULE, DOCUMENT, PROCESS, CONCEPT, ORGANIZATION, PERSON, PLAN, DATA_STANDARD",
        "normalization_rules": """D.PaC-specific entity normalization rules:
- Canonicalize roles to their acronyms: "Project Manager" becomes "PM", "Business Manager" becomes "BM", "Responsabile Istituto" becomes "RI", "Project Manager supporto" becomes "PM supporto".
- Use full official names for documents: "Verbale inizio lavori" becomes "Verbale di Inizio Lavori", "Verbale fine lavori" becomes "Verbale di Fine Lavori", "Studio fattibilità" becomes "Studio di Fattibilità".
- Standardize module names: "modulo di collaudo" becomes "Modulo di Collaudo", "modulo descrittivo" becomes "Modulo Descrittivo", "business intelligence" becomes "Business Intelligence".
- Use acronyms for systems: "Piattaforma di Digitalizzazione del patrimonio culturale" becomes "D_PAC"; "Infrastruttura Software per il Patrimonio Culturale" becomes "I_PAC"; "Data Product as a Service" becomes "DPAAS".
- Canonicalize tool names: "cliente Axway" becomes "Axway CFT"; "Piattaforma di formazione" becomes "Moodle".
- Standardize work package names: "lotto digitalizzazione" becomes "LOTTO_DIGITALIZZAZIONE", "lotto descrizione" becomes "LOTTO_DESCRIZIONE", "lotto prototipazione" becomes "LOTTO_PROTOTIPAZIONE".
- Use official organization acronyms: "Istituto Centrale per il Catalogo e la Documentazione" becomes "ICCD", "Istituto Centrale per gli Archivi" becomes "ICAR", "Istituto Centrale per il Catalogo Unico" becomes "ICCU".
- Standardize authentication methods: "Carta Identità Elettronica" becomes "CIE", "Sistema Pubblico Identità Digitale" becomes "SPID".""",
        "language": "Italian",
        "entities": "[]",
        "relationships": "[]",
        "entity_mappings": {
            # ROLES - Canonical name: [variations]
            "PM": ["Project Manager", "PM", "project manager", "pm"],
            "BM": ["Business Manager", "BM", "business manager", "bm"],
            "RI": ["Responsabile Istituto", "RI", "responsabile istituto", "ri"],
            "PO": ["Project Owner", "PO", "project owner", "po"],
            "DIR": ["Direttore", "DIR", "direttore", "dir"],
            "OP": ["Operatore", "OP", "operatore", "op"],
            "PM supporto": ["Project Manager supporto", "PM supporto", "project manager supporto", "pm supporto"],
            
            # SYSTEMS - Canonical name: [variations]
            "D_PAC": ["Piattaforma di Digitalizzazione del patrimonio culturale", "Piattaforma D.PaC", "D.PaC", "DPaC", "DPAC", "dpac", "d.pac", "D_PAC", "d_pac"],
            "I_PAC": ["Infrastruttura Software per il Patrimonio Culturale", "I.PAC", "I.PaC", "IPaC", "IPAC", "ipac", "i.pac", "I_PAC", "i_pac"],
            "DPAAS": ["Data Product as a Service", "DPaaS", "DPAAS", "dpaas"],
            "SERVICENOW": ["Service Portal", "Portale ServiceNow", "ServiceNow", "SERVICENOW", "servicenow"],
            "MOODLE": ["Piattaforma di formazione", "Moodle", "MOODLE", "moodle"],
            "AXWAY_CFT": ["Cliente Axway", "Client Axway", "Axway CFT", "AXWAY_CFT", "axway cft"],
            
            # DOCUMENTS - Canonical name: [variations]
            "VERBALE_INIZIO_LAVORI": ["Verbale inizio lavori", "Verbale di Inizio Lavori", "verbale inizio lavori", "VERBALE_INIZIO_LAVORI"],
            "VERBALE_FINE_LAVORI": ["Verbale fine lavori", "Verbale di Fine Lavori", "verbale fine lavori", "VERBALE_FINE_LAVORI"],
            "STUDIO_FATTIBILITA": ["Studio fattibilità", "Studio di Fattibilità", "studio fattibilità", "STUDIO_FATTIBILITA"],
            "CHECKLIST_COLLAUDO": ["Checklist collaudo", "Checklist di Collaudo", "checklist collaudo", "CHECKLIST_COLLAUDO"],
            "CHECKLIST_PROTOTIPAZIONE": ["Checklist prototipazione", "Checklist di Prototipazione", "checklist prototipazione", "CHECKLIST_PROTOTIPAZIONE"],
            "REPORT_AVANZAMENTO_LOTTI": ["Report avanzamento", "Report Avanzamento Lotti", "report avanzamento lotti", "REPORT_AVANZAMENTO_LOTTI"],
            "ORDINE_ACQUISTO": ["Ordine d'Acquisto", "Ordine di Acquisto", "OdA", "oda", "ODA", "ORDINE_ACQUISTO"],
            
            # SYSTEM_MODULES - Canonical name: [variations]
            "MODULO_PIANIFICAZIONE": ["Modulo pianificazione", "Modulo di Pianificazione", "modulo pianificazione", "MODULO_PIANIFICAZIONE"],
            "MODULO_COLLAUDO": ["Modulo collaudo", "Modulo di Collaudo", "modulo collaudo", "MODULO_COLLAUDO"],
            "MODULO_DESCRITTIVO": ["Modulo descrittivo", "Modulo Descrittivo", "modulo descrittivo", "MODULO_DESCRITTIVO"],
            "MODULO_RENDICONTAZIONE_ODA": ["Modulo rendicontazione", "Modulo di Rendicontazione e Gestione OdA", "modulo rendicontazione", "MODULO_RENDICONTAZIONE_ODA"],
            "BUSINESS_INTELLIGENCE": ["Business intelligence", "Business Intelligence", "business intelligence", "BUSINESS_INTELLIGENCE"],
            
            # CONCEPTS - Canonical name: [variations]
            "LOTTO_DIGITALIZZAZIONE": ["Lotto digitalizzazione", "Lotto di Digitalizzazione", "lotto digitalizzazione", "LOTTO_DIGITALIZZAZIONE"],
            "LOTTO_DESCRIZIONE": ["Lotto descrizione", "Lotto di Descrizione", "lotto descrizione", "LOTTO_DESCRIZIONE"],
            "LOTTO_PROTOTIPAZIONE": ["Lotto prototipazione", "Lotto di Prototipazione", "lotto prototipazione", "LOTTO_PROTOTIPAZIONE"],
            
            # ORGANIZATIONS - Canonical name: [variations]
            "ICCD": ["Istituto Centrale per il Catalogo e la Documentazione", "ICCD", "iccd"],
            "ICAR": ["Istituto Centrale per gli Archivi", "ICAR", "icar"],
            "ICCU": ["Istituto Centrale per il Catalogo Unico", "ICCU", "iccu"],
            "MIC": ["Ministero della Cultura", "MiC", "MIC", "mic"],
            "ICDP": ["Istituto Centrale per la Digitalizzazione del Patrimonio Culturale", "ICDP", "icdp"],
            
            # DATA_STANDARDS - Canonical name: [variations]
            "CIE": ["Carta Identità Elettronica", "CIE", "cie"],
            "SPID": ["Sistema Pubblico Identità Digitale", "SPID", "spid"],
            
            # PLANS - Canonical name: [variations]
            "PNRR": ["Piano Nazionale di Ripresa e Resilienza", "PNRR", "pnrr"],
            "PND": ["Piano Nazionale Digitalizzazione", "PND", "pnd"]
        }
    }
}

def en_configure_dpac_domain(gateway):
    """Configure the LLMGateway for the D.PaC domain."""
    gateway.configure_domain_defaults(DPAC_DOMAIN_CONFIG)
    return gateway