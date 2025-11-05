"""
D.PaC domain configuration for Graph Builder - French version.

This module provides domain-specific defaults for D.PaC 
(Digitalizzazione Patrimonio Culturale - Digitization of Cultural Heritage) project documents.
French language version.
"""

from typing import Dict, Any


# TODO: make vector_schema and sql_schema dynamic too with the schema snapshot and then delete the static schemas
vector_schema = """
            id (string, unique) → links to Node.id in the graph when applicable.
            title (string) → short title of the content (e.g. "Verbale di Inizio Lavori").
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


# DPaC-specific domain configuration - French version
FR_DPAC_DOMAIN_CONFIG: Dict[str, Dict[str, Any]] = {
    "out-of-context-detection": {
        "topics": [
            "Questions générales sur DPaC/I.PaC : qu'est-ce que DPaC ? qu'est-ce que I.PaC ? signification de l'acronyme DPaC/DPAC/D_PAC et aperçu de la plateforme.",
            "Opérations et gouvernance de la plateforme DPaC (aka dpac, DPAC, D_PAC) : Comment utiliser la plateforme, gérer les rôles (PM, BM, RI, ROP), et comprendre la structure du projet.",
            "Cycle de vie et flux de travail du projet de numérisation : Phases, documentation et étapes administratives dans les projets de numérisation DPaC.",
            "Spécifications techniques et contrôle qualité : Exigences des fichiers, normes de métadonnées, qualité d'image et bases de validation METS.",
            "Support utilisateur et interaction système : Procédures d'assistance, protocoles de communication et intégration avec la plateforme I.PaC.",
            "Modules système DPaC (aka dpac, DPAC, D_PAC) : Aperçu du Modulo di Pianificazione, Modulo di Collaudo et Modulo di Gestione Documentale.",
            "Projet de numérisation PNRR : Informations générales sur le Plan national de relance et de résilience de l'Italie pour la numérisation du patrimoine culturel.",
            "Institutions du patrimoine culturel : Musées, archives, bibliothèques et sites culturels impliqués dans les projets de numérisation.",
            "Organisations italiennes du patrimoine culturel : MiC, ICDP, Bibliothèque numérique et institutions nationales connexes.",
            "Parties prenantes du projet DPaC (aka dpac, DPAC, D_PAC) : Organismes de mise en œuvre, entrepreneurs, autorités régionales et organisations associées.",
            "Numérisation du patrimoine culturel : Questions générales sur les processus de numérisation et la préservation du patrimoine.",
            "Musées et sites culturels italiens : Questions sur des musées spécifiques comme le Museo Archeologico Nazionale, les institutions culturelles et les sites patrimoniaux en Italie.",
            "Géographie du patrimoine culturel italien, Institutions, Artistes (comme Léonard de Vinci, ...), Renaissance, Monuments (comme le Colisée, ...), Lieux : Questions sur l'emplacement, l'histoire ou l'identité des musées italiens, des sites culturels, des influences historiques et des institutions patrimoniales telles que les Gallerie dell'Accademia, la Galerie des Offices ou le Museo Archeologico Nazionale.",
            "Influences historiques et culturelles italiennes : Questions sur les civilisations et cultures (par exemple, Empire romain, Renaissance, Étrusques, Grecs) qui ont influencé l'histoire, l'art et le patrimoine de l'Italie.",
            "questions de discussion générale",
        ]
    },
    "sensitive-topics-detection": {
        "topics": [
            "Détails techniques de numérisation : Structure XML, profils METS ECO-MIC, champs de métadonnées, formats de fichiers (TIFF LZW) et scripts de validation.",
            "Procédures administratives et contractuelles : Documentation d'appel d'offres, Accordi Quadro, OdA (Ordres d'activation), DUVRI et contrats de projet.",
            "Intégration de systèmes externes : Système ReGiS, intégration de la plateforme I.PaC, interactions M2M (Machine-to-Machine) et H2W (Human-to-Widget).",
            "Support et coordination régionaux : Interactions avec les autorités régionales, réunions SAL et FAQ régionales (par exemple, Lombardie, Toscane, Sardaigne).",
            "Rôles de gouvernance formels : Rôles et responsabilités internes de RUP, PM, BM, RI, ROP et organismes de mise en œuvre (Soggetti Attuatori).",
            "Opérations internes DPaC : Maintenance backend, configurations de serveur ou journaux système internes. Exclure les questions générales sur les modules de plateforme ou les fonctionnalités utilisateur.",
        ]
    },
    "nl2cypher": {
        "schema": "",
        "example": """
{
  "cypher": "MATCH (s:SYSTEM)-[:INTEGRATES_WITH]->(t:SYSTEM) RETURN s.name AS source, t.name AS target LIMIT 10",
  "explanation": "Exemple de modèle illustratif uniquement. Ne copiez pas les noms littéraux des exemples ; utilisez les noms réels du schéma/contexte en direct.",
  "confidence_score": 0.90
}
{
  "cypher": "MATCH (o:ORGANIZATION) WHERE toUpper(o.name) = toUpper('Some Org') RETURN o {.id, .name, .type, .description} AS organization",
  "explanation": "Démontre le filtrage insensible à la casse et la sélection compacte des propriétés.",
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
        "normalization_rules": """Règles de normalisation des entités spécifiques à D.PaC :
- Utilisez des acronymes pour les rôles (par exemple, PM, BM, RI, PO, DIR, ROP, OP) et les rôles de support (par exemple, PM supporto).
- Utilisez les noms italiens complets pour les documents (par exemple, "Workplan di Cantiere", "Verbale di Inizio Lavori", "Verbale di Fine Lavori", "Ordine d'Acquisto", "Studio di Fattibilità").
- Standardisez les noms de modules système comme "Modulo di [Name]" (par exemple, "Modulo di Pianificazione", "Modulo Descrittivo").
- Utilisez les acronymes officiels pour les plans et organisations (par exemple, PNRR, PND, MiC, ICDP, ICCD, ICAR, ICCU).
- Canonicalisez les noms de système : "D_PAC" pour la plateforme de numérisation, "I_PAC" pour l'infrastructure de base, "DPAAS" pour Data Product as a Service, "SERVICENOW" pour le portail de support.
- Canonicalisez les noms d'outils : "Axway CFT" pour le client de transfert de fichiers, "Moodle" pour la plateforme de formation.
- Utilisez une terminologie spécifique pour les lots de travail : "Lotto di Digitalizzazione", "Lotto di Descrizione", "Lotto di Prototipazione".
- Standardisez les méthodes d'authentification : "SPID", "CIE", "LDAP".""",
        "examples": """Exemples d'extraction d'entités D.PaC (voir la version anglaise pour des exemples détaillés)"""
    },
    "relationship-extraction": {
        "entity_types": "ROLE, SYSTEM, TOOL, SYSTEM_MODULE, DOCUMENT, PROCESS, CONCEPT, ORGANIZATION, PERSON, PLAN, DATA_STANDARD",
        "relationship_types": "USES, MANAGES, CREATES, APPROVES, VERIFIES, SIGNS, PERFORMS, COORDINATES, MONITORS, SUPPORTS, IS_PART_OF, HAS_MODULE, SENDS_NOTIFICATION, ANALYZES, REPORTS_ERRORS_OF, UNDERGOES, RELATED_TO, INTEGRATES_WITH, DEPOSITS_INTO, SUBMITS_FOR_APPROVAL, TRANSFERS_WITH, PRODUCES, IS_BASED_ON, CONTAINS, TRIGGERS, HAS_STATUS, REQUIRES_SIGNATURE_FROM, ASSIGNS, MANAGES_BUDGET_OF, HAS_SUPPORT_ROLE",
        "normalization_rules": """Normalisation des relations spécifiques à D.PaC :
- Utilisez des types de relations cohérents de la liste autorisée.
- Mappez les tâches opérationnelles à des verbes spécifiques : PM `CREATES` documents, BM `VERIFIES` qualité, RI/PO `APPROVES` plans/commandes.
- Un SYSTEM_MODULE `IS_PART_OF` un SYSTEM plus large (par exemple, D_PAC).
- Un ROLE `USES` un SYSTEM ou TOOL pour `PERFORM` un PROCESS.
- Utilisez `INTEGRATES_WITH` pour les connexions système à système.
- Utilisez `DEPOSITS_INTO` pour les relations de flux de données, comme de D_PAC à I_PAC.
- Utilisez `IS_BASED_ON` pour les dépendances formelles (par exemple, Lotto -> IS_BASED_ON -> Prototipo).
- Utilisez `CONTAINS` pour les relations de confinement (par exemple, Cluster -> CONTAINS -> Cantiere).
- Utilisez `HAS_SUPPORT_ROLE` pour lier les rôles formels avec leurs homologues de support.""",
        "relationship_guidelines": """Directives de relations spécifiques à D.PaC (voir la version anglaise pour des directives détaillées)""",
        "examples": """Exemples d'extraction de relations D.PaC (voir la version anglaise pour des exemples détaillés)"""
    },
    "claim-extraction": {
        "entity_specs": "ROLE, PROCESS, DOCUMENT, SYSTEM, SYSTEM_MODULE, TOOL",
        "claim_description": """Revendications spécifiques à D.PaC à extraire :
- Responsabilités d'un rôle spécifique (par exemple, "Le PM doit créer le Workplan").
- Le statut ou le résultat d'un processus (par exemple, "La validation du fichier METS a échoué").
- Exigences ou règles pour un document (par exemple, "La liste de contrôle doit être approuvée par le BM").
- État ou disponibilité d'un système ou module (par exemple, "Le service peut ne pas être disponible pendant la maintenance").
- Instructions ou étapes dans une procédure (par exemple, "Pour exporter des données de D.PaC, l'utilisateur doit cliquer sur le bouton 'Esporta'").
- Capacités ou objectif d'un système (par exemple, "I.PaC est l'espace de données conçu pour préserver et gérer le patrimoine culturel numérique")."""
    },
    "entity-merging": {
        "allowed_entity_types": "ROLE, SYSTEM, TOOL, SYSTEM_MODULE, DOCUMENT, PROCESS, CONCEPT, ORGANIZATION, PERSON, PLAN, DATA_STANDARD",
        "entity_type_mappings": """Mappages de types d'entités spécifiques à D.PaC (voir la version anglaise pour des mappages détaillés)""",
        "key_attributes": "acronymes de rôles, noms complets de documents, noms de modules, étapes de processus, noms de systèmes, noms de plateformes, noms d'outils, types de lots de travail, domaines du patrimoine culturel, méthodes d'authentification"
    },
    "entity-normalization": {
        "entity_types": "ROLE, SYSTEM, TOOL, SYSTEM_MODULE, DOCUMENT, PROCESS, CONCEPT, ORGANIZATION, PERSON, PLAN, DATA_STANDARD",
        "normalization_rules": """Règles de normalisation des entités spécifiques à D.PaC (voir la version anglaise pour des règles détaillées)""",
        "language": "French",
        "entities": "[]",
        "relationships": "[]",
        "entity_mappings": {}
    }
}
