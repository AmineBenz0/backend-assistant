"""
Configurazione di dominio D.PaC per il Graph Builder.

Questo modulo fornisce predefiniti specifici di dominio per i documenti del progetto D.PaC
(Digitalizzazione del Patrimonio Culturale).
Definisce entità, relazioni e regole specifiche della piattaforma D.PaC e dei suoi flussi operativi,
incluse le interazioni con sistemi correlati come I.PaC, DPaaS e ServiceNow.
"""

from typing import Dict, Any


# TODO: rendere dinamici anche vector_schema e sql_schema con lo snapshot dello schema e poi eliminare gli schemi statici
vector_schema = """
            id (string, unico) → collega a Node.id nel grafo quando applicabile.
            title (string) → titolo breve del contenuto (es. "Verbale di Inizio Lavori").
            content (text, embedded) → il contenuto testuale completo (workplan, report, checklist, ecc.).
            embedding (vector) → vettore denso del contenuto per similarità semantica.
        """

# TODO: rendere dinamici anche vector_schema e sql_schema con lo snapshot dello schema e poi eliminare gli schemi statici
sql_schema = """Tabelle:
                    projects(id, name, plan_type, start_date, end_date, location_id, manager_id),
                    documents(id, title, doc_type, created_at, author_id, project_id),
                    people(id, full_name, role, organization_id, email),
                    organizations(id, name, org_type, city),
                    locations(id, name, region, country).

                Join:
                    documents.project_id -> projects.id,
                    projects.manager_id -> people.id,
                    people.organization_id -> organizations.id,
                    projects.location_id -> locations.id
            """


# Configurazione di dominio specifica DPaC
IT_DPAC_DOMAIN_CONFIG: Dict[str, Dict[str, Any]] = {
    "out-of-context-detection": {
        "topics": [
            "Domande generali su DPaC/I.PaC: cos'è DPaC? cos'è I.PaC? significato dell'acronimo DPaC/DPAC/D_PAC e panoramica della piattaforma.",
            "Piattaforma DPaC (detta anche dpac, DPAC, D_PAC) Operatività e Governance: come usare la piattaforma, gestire i ruoli (PM, BM, RI, ROP) e comprendere la struttura dei progetti.",
            "Ciclo di vita e workflow dei progetti di digitalizzazione: fasi, documentazione e passaggi amministrativi nei progetti di digitalizzazione DPaC.",
            "Specifiche tecniche e controllo qualità: requisiti dei file, standard di metadatazione, qualità delle immagini e basi della validazione METS.",
            "Supporto utenti e interazione con i sistemi: procedure di helpdesk, protocolli di comunicazione e integrazione con la piattaforma I.PaC.",
            "Moduli del sistema DPaC (detta anche dpac, DPAC, D_PAC): panoramica di Modulo di Pianificazione, Modulo di Collaudo e Modulo di Gestione Documentale.",
            "Progetto PNRR per la digitalizzazione: informazioni generali sul Piano Nazionale di Ripresa e Resilienza per la digitalizzazione del patrimonio culturale.",
            "Istituzioni del patrimonio culturale: musei, archivi, biblioteche e siti culturali coinvolti nei progetti di digitalizzazione.",
            "Organismi italiani del patrimonio culturale: MiC, ICDP, Digital Library e relative istituzioni nazionali.",
            "Stakeholder dei progetti DPaC (detta anche dpac, DPAC, D_PAC): soggetti attuatori, fornitori, autorità regionali e organizzazioni associate.",
            "Digitalizzazione del patrimonio culturale: domande generali su processi di digitalizzazione e conservazione.",
            "Musei e siti culturali italiani: domande su musei specifici come il Museo Archeologico Nazionale, istituzioni culturali e siti del patrimonio in Italia.",
            "Geografia del patrimonio culturale italiano, istituzioni, artisti (es. Leonardo da Vinci), Rinascimento, luoghi simbolo (es. Colosseo), località: domande su ubicazione, storia o identità di musei, siti culturali, influenze storiche e istituzioni come Gallerie dell’Accademia, Galleria degli Uffizi o Museo Archeologico Nazionale.",
            "Influenze storiche e culturali italiane: domande su civiltà e culture (es. Impero Romano, Rinascimento, Etruschi, Greci) che hanno influenzato storia, arte e patrimonio dell’Italia.",
            "chat generale"
        ]
    },
    "sensitive-topics-detection": {
        "topics": [
            "Dettagli tecnici di digitalizzazione: struttura XML, profili METS ECO-MIC, campi di metadatazione, formati file (TIFF LZW) e script di validazione.",
            "Procedure amministrative e contrattuali: documentazione di gara, Accordi Quadro, OdA (Ordini di Attivazione), DUVRI e contratti di progetto.",
            "Integrazione con sistemi esterni: sistema ReGiS, integrazione con piattaforma I.PaC, interazioni M2M (machine-to-machine) e H2W (human-to-widget).",
            "Supporto e coordinamento regionali: interazioni con autorità regionali, riunioni SAL e FAQ regionali (es. Lombardia, Toscana, Sardegna).",
            "Ruoli formali di governance: responsabilità interne di RUP, PM, BM, RI, ROP e Soggetti Attuatori.",
            "Operatività interna DPaC: manutenzione backend, configurazioni server o log interni del sistema. Escludere domande generali su moduli della piattaforma o funzionalità utente.",
        ]
    },
    "nl2cypher": {
        "schema": "",
        "example": """
{
  "cypher": "MATCH (s:SYSTEM)-[:INTEGRATES_WITH]->(t:SYSTEM) RETURN s.name AS source, t.name AS target LIMIT 10",
  "explanation": "Esempio puramente illustrativo basato su pattern. Non copiare nomi letterali dagli esempi; usa nomi reali dallo schema/contenuto attuale.",
  "confidence_score": 0.90
}
{
  "cypher": "MATCH (o:ORGANIZATION) WHERE toUpper(o.name) = toUpper('Some Org') RETURN o {.id, .name, .type, .description} AS organization",
  "explanation": "Dimostra filtro case-insensitive e selezione compatta delle proprietà.",
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
        "normalization_rules": """Regole di normalizzazione entità specifiche D.PaC:
- Usa acronimi per i ruoli (es. PM, BM, RI, PO, DIR, ROP, OP) e ruoli di supporto (es. PM supporto).
- Usa i nomi italiani completi per i documenti (es. "Workplan di Cantiere", "Verbale di Inizio Lavori", "Verbale di Fine Lavori", "Ordine d'Acquisto", "Studio di Fattibilità").
- Standardizza i nomi dei moduli come "Modulo di [Nome]" (es. "Modulo di Pianificazione", "Modulo Descrittivo").
- Usa gli acronimi ufficiali per piani e organizzazioni (es. PNRR, PND, MiC, ICDP, ICCD, ICAR, ICCU).
- Canonicalizza i nomi dei sistemi: "D_PAC" per la piattaforma di digitalizzazione, "I_PAC" per l'infrastruttura software, "DPAAS" per Data Product as a Service, "SERVICENOW" per il portale di supporto.
- Canonicalizza i nomi degli strumenti: "Axway CFT" per il client di trasferimento file, "Moodle" per la piattaforma di formazione.
- Usa terminologia specifica per i lotti di lavoro: "Lotto di Digitalizzazione", "Lotto di Descrizione", "Lotto di Prototipazione".
- Standardizza i metodi di autenticazione: "SPID", "CIE", "LDAP".""",
        "examples": """Esempi di estrazione entità D.PaC:

Esempio 1 - Ecosistema dei sistemi:
Testo: "Le risorse digitali prodotte dai cantieri di digitalizzazione vengono depositate nel Data Lake di I.PaC. La piattaforma D.PaC gestisce questo processo. Per supporto, gli utenti possono aprire un ticket sul Service Portal di ServiceNow."
Output:
("entity"|D_PAC|SYSTEM|Piattaforma per la gestione della digitalizzazione del patrimonio culturale)
("entity"|I_PAC|SYSTEM|Infrastruttura software e data lake per il patrimonio culturale)
("entity"|SERVICENOW|SYSTEM|Portale di help desk e servizio di supporto per gli utenti)
("entity"|Data Lake|CONCEPT|Repository centralizzato per l'archiviazione di grandi quantità di dati)
("entity"|Cantiere di Digitalizzazione|CONCEPT|Sito di progetto di digitalizzazione)
("entity"|Risorse Digitali|CONCEPT|Risorse digitali prodotte durante il progetto)
("entity"|Ticket|DOCUMENT|Richiesta di supporto inviata da un utente)
("relationship"|D_PAC|I_PAC|DEPOSITS_INTO|La piattaforma D_PAC deposita le risorse digitali nel data lake di I_PAC|0.9)
("relationship"|I_PAC|DATA_LAKE|CONTAINS|L'infrastruttura I_PAC contiene il data lake|0.8)
("relationship"|Cantiere di Digitalizzazione|Risorse Digitali|PRODUCES|I cantieri di digitalizzazione producono risorse digitali|0.9)
("relationship"|UTENTE|SERVICENOW|USES|Gli utenti possono aprire ticket sul portale SERVICENOW|0.8)

Esempio 2 - Workflow OdA (Ordine di Acquisto):
Testo: "Il BM crea un nuovo Ordine d'Acquisto (OdA) per il cluster. L'OdA viene poi inviato in approvazione al PO. Il PO può approvare o respingere l'OdA. Il monitoraggio del budget e del borsellino è visibile nel Modulo di Rendicontazione e Gestione OdA."
Output:
("entity"|BM|ROLE|Business Manager, responsabile della creazione e dell'invio degli Ordini di Acquisto)
("entity"|PO|ROLE|Project Owner, responsabile dell'approvazione degli Ordini di Acquisto)
("entity"|Ordine d'Acquisto (OdA)|DOCUMENT|Ordine ufficiale per servizi o beni legati al progetto)
("entity"|Cluster|CONCEPT|Raggruppamento logico di cantieri di digitalizzazione)
("entity"|Budget|CONCEPT|Allocazione finanziaria complessiva del progetto)
("entity"|Borsellino|CONCEPT|Sotto-budget allocato ad attività specifiche)
("entity"|Modulo di Rendicontazione e Gestione OdA|SYSTEM_MODULE|Modulo D.PaC per la gestione di budget e ordini di acquisto)
("relationship"|BM|Ordine d'Acquisto (OdA)|CREATES|Il BM crea nuovi Ordini di Acquisto|0.9)
("relationship"|BM|PO|SUBMITS_FOR_APPROVAL|Il BM invia l'OdA al PO per l'approvazione|0.9)
("relationship"|PO|Ordine d'Acquisto (OdA)|APPROVES|Il PO approva o respinge l'OdA|0.8)
("relationship"|BM|Modulo di Rendicontazione e Gestione OdA|USES|Il BM usa il modulo OdA per monitorare il budget|0.9)

Esempio 3 - Flusso di digitalizzazione con nuove entità:
Testo: "Il Lotto di Digitalizzazione è basato sul Prototipo approvato. Il PM supporto assiste nella creazione del Verbale di Fine Lavori che richiede la firma digitale del PM. Il processo di Recupero del Digitale Pregresso include uno Studio di Fattibilità."
Output:
("entity"|Lotto di Digitalizzazione|CONCEPT|Pacchetto di lavoro per attività di digitalizzazione)
("entity"|Prototipo|CONCEPT|Prototipo approvato che costituisce la base per i lotti di digitalizzazione)
("entity"|PM supporto|ROLE|Ruolo di supporto che assiste il PM formale senza responsabilità finale)
("entity"|PM|ROLE|Project Manager, responsabile del coordinamento e della firma dei documenti)
("entity"|Verbale di Fine Lavori|DOCUMENT|Documento che certifica il completamento dei lavori in un cantiere)
("entity"|Firma Digitale|PROCESS|Procedura ufficiale di apposizione della firma digitale sui documenti)
("entity"|Recupero del Digitale Pregresso|PROCESS|Workflow per recuperare e integrare materiali già digitalizzati)
("entity"|Studio di Fattibilità|DOCUMENT|Documento di studio preliminare creato per il processo di recupero)
("relationship"|Lotto di Digitalizzazione|Prototipo|IS_BASED_ON|I lotti di digitalizzazione sono basati su prototipi approvati|0.9)
("relationship"|PM|PM supporto|HAS_SUPPORT_ROLE|Il PM ha un corrispettivo di supporto designato|0.8)
("relationship"|Verbale di Fine Lavori|PM|REQUIRES_SIGNATURE_FROM|Il documento di fine lavori richiede la firma digitale del PM|0.9)
("relationship"|PM supporto|Verbale di Fine Lavori|CREATES|Il ruolo di supporto assiste nella creazione del documento di fine lavori|0.8)
("relationship"|Recupero del Digitale Pregresso|Studio di Fattibilità|CONTAINS|Il processo di recupero include uno studio di fattibilità|0.9)

Esempio 4 - Organizzazioni e standard del patrimonio culturale:
Testo: "L'ICCD assegna i codici NCTN per l'identificazione univoca dei beni culturali. Il Fondo A del dominio Storico-Artistico viene digitalizzato secondo le linee guida. Le Schede D vengono create nel Modulo Descrittivo."
Output:
("entity"|ICCD|ORGANIZATION|Istituto Centrale per il Catalogo e la Documentazione)
("entity"|NCTN|DATA_STANDARD|Codici di identificazione univoci per i beni culturali)
("entity"|Fondo A|CONCEPT|Raccolta o archivio specifico oggetto di digitalizzazione)
("entity"|Storico-Artistico|CONCEPT|Dominio del patrimonio culturale storico-artistico)
("entity"|Linee guida|DOCUMENT|Linee guida ufficiali previste per le procedure)
("entity"|Scheda D|CONCEPT|Tipologia di scheda di catalogazione creata nel modulo descrittivo)
("entity"|Modulo Descrittivo|SYSTEM_MODULE|Modulo D.PaC per la catalogazione descrittiva)
("relationship"|ICCD|NCTN|ASSIGNS|ICCD assegna codici NCTN univoci per l'identificazione|0.9)
("relationship"|Fondo A|Storico-Artistico|IS_PART_OF|Il Fondo A appartiene al dominio storico-artistico|0.8)
("relationship"|Modulo Descrittivo|Scheda D|PRODUCES|Il modulo descrittivo è usato per creare schede di catalogazione|0.9)
("relationship"|Digitalizzazione|Linee guida|UNDERGOES|I processi di digitalizzazione seguono linee guida ufficiali|0.8)

Esempio 5 - Monitoraggio progetto e criticità:
Testo: "Il Report Avanzamento Lotti generato dal modulo Business Intelligence mostra le Criticità del progetto. Una Segnalazione viene aperta nei Casi Aperti tra BM e PM per questioni amministrative. Il Gantt viene aggiornato per la Ripianificazione."
Output:
("entity"|Report Avanzamento Lotti|DOCUMENT|Report che mostra l'avanzamento dei diversi lotti di lavoro)
("entity"|Business Intelligence|SYSTEM_MODULE|Modulo D.PaC per la generazione di report analitici)
("entity"|Criticità|CONCEPT|Problema critico che può impattare tempi o qualità)
("entity"|Segnalazione|CONCEPT|Segnalazione/issue ufficiale gestita tramite il sistema dei casi aperti)
("entity"|Casi Aperti|CONCEPT|Sistema per la gestione delle pratiche amministrative aperte tra ruoli)
("entity"|Gantt|CONCEPT|Diagramma di pianificazione e schedulazione del progetto)
("entity"|Ripianificazione|PROCESS|Processo di riorganizzazione delle attività progettuali)
("relationship"|Business Intelligence|Report Avanzamento Lotti|PRODUCES|Il modulo BI genera report di avanzamento|0.9)
("relationship"|Report Avanzamento Lotti|Criticità|ANALYZES|Il report di avanzamento analizza le criticità del progetto|0.8)
("relationship"|BM|Segnalazione|CREATES|Il BM crea segnalazioni ufficiali per questioni amministrative|0.9)
("relationship"|Segnalazione|Casi Aperti|IS_PART_OF|Le segnalazioni sono gestite all'interno del sistema dei casi aperti|0.8)
("relationship"|Ripianificazione|Gantt|USES|La ripianificazione utilizza i diagrammi di Gantt per la schedulazione|0.9)
"""
    },
    "relationship-extraction": {
        "entity_types": "ROLE, SYSTEM, TOOL, SYSTEM_MODULE, DOCUMENT, PROCESS, CONCEPT, ORGANIZATION, PERSON, PLAN, DATA_STANDARD",
        "relationship_types": "USES, MANAGES, CREATES, APPROVES, VERIFIES, SIGNS, PERFORMS, COORDINATES, MONITORS, SUPPORTS, IS_PART_OF, HAS_MODULE, SENDS_NOTIFICATION, ANALYZES, REPORTS_ERRORS_OF, UNDERGOES, RELATED_TO, INTEGRATES_WITH, DEPOSITS_INTO, SUBMITS_FOR_APPROVAL, TRANSFERS_WITH, PRODUCES, IS_BASED_ON, CONTAINS, TRIGGERS, HAS_STATUS, REQUIRES_SIGNATURE_FROM, ASSIGNS, MANAGES_BUDGET_OF, HAS_SUPPORT_ROLE",
        "normalization_rules": """Normalizzazione relazioni specifiche D.PaC:
- Usa in modo coerente i tipi di relazione dalla lista consentita.
- Mappa i compiti operativi a verbi specifici: PM `CREATES` documenti, BM `VERIFIES` qualità, RI/PO `APPROVES` piani/ordini.
- Un SYSTEM_MODULE `IS_PART_OF` un SYSTEM più ampio (es. D_PAC).
- Un ROLE `USES` un SYSTEM o TOOL per `PERFORM`are un PROCESS.
- Usa `INTEGRATES_WITH` per connessioni sistema-sistema.
- Usa `DEPOSITS_INTO` per i flussi dati, come da D_PAC a I_PAC.
- Usa `IS_BASED_ON` per dipendenze formali (es. Lotto -> IS_BASED_ON -> Prototipo).
- Usa `CONTAINS` per relazioni di contenimento (es. Cluster -> CONTAINS -> Cantiere).
- Usa `HAS_SUPPORT_ROLE` per collegare ruoli formali ai loro corrispettivi di supporto.""",
        "relationship_guidelines": """Linee guida relazioni specifiche D.PaC:
- `CREATES`: quando un ruolo è responsabile dell'autore di un documento (es. PM `CREATES` Workplan).
- `VERIFIES`: quando un ruolo svolge un controllo qualità/validazione (es. BM `VERIFIES` Checklist).
- `APPROVES`: per passaggi formali di approvazione (es. RI `APPROVES` Workplan; PO `APPROVES` OdA).
- `USES`: collega un ruolo a un sistema o strumento che utilizza (es. PM `USES` MODULO_PIANIFICAZIONE; OP `USES` AXWAY_CFT).
- `INTEGRATES_WITH`: connessione funzionale tra due sistemi (es. D_PAC `INTEGRATES_WITH` SERVICENOW).
- `DEPOSITS_INTO`: azione di depositare dati/risorse in un repository o altro sistema (es. D_PAC `DEPOSITS_INTO` I_PAC).
- `SUBMITS_FOR_APPROVAL`: quando un ruolo invia formalmente un documento a un altro per approvazione (es. BM `SUBMITS_FOR_APPROVAL` OdA a PO).
- `TRANSFERS_WITH`: uso di uno strumento specifico per il trasferimento dati (es. OP `TRANSFERS_WITH` Axway CFT).
- `IS_BASED_ON`: un processo o entità è formalmente basato su un altro (es. Lotto di Digitalizzazione `IS_BASED_ON` Prototipo).
- `CONTAINS`: relazione di contenimento (es. Cluster `CONTAINS` Cantiere; Lotto di Digitalizzazione `CONTAINS` Pacchetto Digitale).
- `TRIGGERS`: un'azione/evento che avvia un altro processo (es. Rifiuto Collaudo `TRIGGERS` Ripianificazione).
- `HAS_STATUS`: assegna uno stato a documento o processo (es. Workplan di Cantiere `HAS_STATUS` Approvato).
- `REQUIRES_SIGNATURE_FROM`: specifica quale ruolo deve firmare digitalmente un documento (es. Verbale di Fine Lavori `REQUIRES_SIGNATURE_FROM` PM).
- `ASSIGNS`: azione di assegnazione di un codice o risorsa (es. ICCD `ASSIGNS` NCTN).
- `MANAGES_BUDGET_OF`: collega un ruolo al concetto finanziario che gestisce (es. BM `MANAGES_BUDGET_OF` Cluster).
- `HAS_SUPPORT_ROLE`: collega un ruolo formale al suo corrispettivo di supporto (es. PM `HAS_SUPPORT_ROLE` PM supporto).""",
        "examples": """Esempi di estrazione relazioni D.PaC:

Esempio 1 - Comunicazioni per disservizio:
Testo: "Per comunicazioni di disservizio, una Notifica di Manutenzione Straordinaria viene inviata dal Servizio di supporto D.PaC. La mail deve essere inviata al gruppo D.PaC-Supporto, che include gli utenti DL e Helpdesk. Le segnalazioni possono essere gestite tramite il portale ServiceNow."
Output:
("entity"|Disservizio|CONCEPT|Disservizio del servizio)
("entity"|Notifica di Manutenzione Straordinaria|DOCUMENT|Notifica per manutenzione straordinaria)
("entity"|Servizio di supporto D.PaC|ORGANIZATION|Team di supporto D.PaC)
("entity"|D.PaC-Supporto|ROLE|Lista di distribuzione per utenti di supporto)
("entity"|Utenti DL|ROLE|Utenti con ruolo DL)
("entity"|ServiceNow|SYSTEM|Portale di help desk e supporto)
("relationship"|Servizio di supporto D.PaC|Notifica di Manutenzione Straordinaria|SENDS_NOTIFICATION|Il servizio di supporto D.PaC invia notifiche di manutenzione|0.9)
("relationship"|Notifica di Manutenzione Straordinaria|Disservizio|RELATED_TO|La notifica è relativa a un disservizio|0.8)
("relationship"|Utenti DL|D.PaC-Supporto|IS_PART_OF|Gli utenti DL fanno parte del gruppo D.PaC-Supporto|0.9)
("relationship"|Servizio di supporto D.PaC|ServiceNow|USES|Il servizio di supporto usa ServiceNow per gestire le segnalazioni|0.8)

Esempio 2 - Chiusura cantiere e firme digitali:
Testo: "Durante la Chiusura Cantiere, il PM deve firmare digitalmente il Verbale di Fine Lavori. Il processo di Firma Digitale viene eseguito esternamente alla piattaforma D.PaC. Il Verbale ha stato 'Approvato' dopo la firma."
Output:
("entity"|Chiusura Cantiere|PROCESS|Fase finale di un progetto di digitalizzazione)
("entity"|PM|ROLE|Project Manager responsabile della firma dei documenti)
("entity"|Firma Digitale|PROCESS|Procedura ufficiale di firma digitale dei documenti)
("entity"|Verbale di Fine Lavori|DOCUMENT|Documento che certifica il completamento dei lavori)
("entity"|D.PaC|SYSTEM|La piattaforma di digitalizzazione)
("entity"|Approvato|CONCEPT|Stato di approvazione del documento)
("relationship"|Chiusura Cantiere|Verbale di Fine Lavori|PRODUCES|La fase di chiusura produce il documento di fine lavori|0.9)
("relationship"|Verbale di Fine Lavori|PM|REQUIRES_SIGNATURE_FROM|Il documento richiede la firma digitale del PM|0.9)
("relationship"|PM|Firma Digitale|PERFORMS|Il PM esegue il processo di firma digitale|0.8)
("relationship"|Verbale di Fine Lavori|Approvato|HAS_STATUS|Dopo la firma, il documento ha stato 'Approvato'|0.9)

Esempio 3 - Dipendenze tra lotti e gestione budget:
Testo: "Il Lotto di Digitalizzazione è basato sul Prototipo validato dal BM. Il BM gestisce il budget del Cluster che contiene più Cantieri. Il rifiuto del collaudo scatena la Ripianificazione del lotto."
Output:
("entity"|Lotto di Digitalizzazione|CONCEPT|Pacchetto di lavoro per attività di digitalizzazione)
("entity"|Prototipo|CONCEPT|Prototipo approvato che costituisce la base dei lotti)
("entity"|BM|ROLE|Business Manager responsabile della validazione e della gestione del budget)
("entity"|Budget|CONCEPT|Allocazione finanziaria complessiva)
("entity"|Cluster|CONCEPT|Raggruppamento logico di cantieri)
("entity"|Cantiere|CONCEPT|Cantiere di progetto di digitalizzazione)
("entity"|Collaudo|PROCESS|Processo di collaudo e validazione)
("entity"|Ripianificazione|PROCESS|Processo di riorganizzazione delle attività)
("relationship"|Lotto di Digitalizzazione|Prototipo|IS_BASED_ON|I lotti di digitalizzazione sono basati su prototipi validati|0.9)
("relationship"|BM|Prototipo|VERIFIES|Il BM valida il prototipo prima della creazione del lotto|0.8)
("relationship"|BM|Budget|MANAGES_BUDGET_OF|Il BM gestisce l'allocazione finanziaria|0.9)
("relationship"|Cluster|Cantiere|CONTAINS|Un cluster contiene più cantieri|0.9)
("relationship"|Collaudo|Ripianificazione|TRIGGERS|Il rifiuto del collaudo attiva la ripianificazione|0.8)

Esempio 4 - Catalogazione e standard del patrimonio culturale:
Testo: "L'ICCD assegna i codici NCTN per identificare i beni del Fondo Storico-Artistico. Le Schede UA vengono create nel Modulo Descrittivo seguendo la Nomenclatura specifica. Il dominio Archivistico ha procedure diverse."
Output:
("entity"|ICCD|ORGANIZATION|Istituto Centrale per il Catalogo e la Documentazione)
("entity"|NCTN|DATA_STANDARD|Codici di identificazione univoci per i beni culturali)
("entity"|Fondo|CONCEPT|Raccolta/archivio oggetto di digitalizzazione)
("entity"|Storico-Artistico|CONCEPT|Dominio storico-artistico del patrimonio culturale)
("entity"|Scheda UA|CONCEPT|Tipologia specifica di scheda di catalogazione)
("entity"|Modulo Descrittivo|SYSTEM_MODULE|Modulo D.PaC per la catalogazione descrittiva)
("entity"|Nomenclatura|CONCEPT|Convenzioni specifiche di denominazione richieste per file e pacchetti)
("entity"|Archivistico|CONCEPT|Dominio archivistico del patrimonio culturale)
("relationship"|ICCD|NCTN|ASSIGNS|ICCD assegna codici di identificazione univoci|0.9)
("relationship"|NCTN|Fondo|RELATED_TO|I codici NCTN identificano i beni nelle raccolte|0.8)
("relationship"|Fondo|Storico-Artistico|IS_PART_OF|La raccolta appartiene al dominio storico-artistico|0.9)
("relationship"|Modulo Descrittivo|Scheda UA|PRODUCES|Il modulo descrittivo crea le schede di catalogazione|0.9)
("relationship"|Scheda UA|Nomenclatura|UNDERGOES|Le schede seguono convenzioni di denominazione specifiche|0.8)

Esempio 5 - Ruoli di supporto e trasferimento file:
Testo: "Il PM supporto assiste nella creazione del Report Avanzamento Lotti. L'OP utilizza il client Axway CFT per il Caricamento Pacchetti tramite Folder Monitoring. Il processo è automatizzato."
Output:
("entity"|PM supporto|ROLE|Ruolo di supporto che assiste il PM)
("entity"|PM|ROLE|Project Manager con responsabilità formale)
("entity"|Report Avanzamento Lotti|DOCUMENT|Report che mostra l'avanzamento dei lotti)
("entity"|OP|ROLE|Operatore responsabile dei trasferimenti file)
("entity"|Axway CFT|TOOL|Software client per il trasferimento file)
("entity"|Caricamento Pacchetti|PROCESS|Azione specifica di caricamento pacchetti digitali)
("entity"|Folder Monitoring|PROCESS|Processo automatizzato di caricamento da cartella)
("relationship"|PM|PM supporto|HAS_SUPPORT_ROLE|Il PM ha un corrispettivo di supporto designato|0.9)
("relationship"|PM supporto|Report Avanzamento Lotti|CREATES|Il ruolo di supporto assiste nella creazione del report|0.8)
("relationship"|OP|Axway CFT|USES|L'operatore usa il client di trasferimento file|0.9)
("relationship"|OP|Caricamento Pacchetti|PERFORMS|L'operatore esegue il processo di caricamento pacchetti|0.9)
("relationship"|Caricamento Pacchetti|Folder Monitoring|USES|Il caricamento pacchetti utilizza il monitoraggio di cartelle|0.8)
"""
    },
    "claim-extraction": {
        "entity_specs": "ROLE, PROCESS, DOCUMENT, SYSTEM, SYSTEM_MODULE, TOOL",
        "claim_description": """Claim specifici D.PaC da estrarre:
- Responsabilità di un ruolo specifico (es. "Il PM deve creare il Workplan").
- Stato o esito di un processo (es. "La validazione del file METS è fallita").
- Requisiti o regole per un documento (es. "La checklist deve essere approvata dal BM").
- Stato o disponibilità di un sistema o modulo (es. "Il servizio potrebbe non essere disponibile durante la manutenzione").
- Istruzioni o passi di una procedura (es. "Per esportare i dati da D.PaC, l'utente deve cliccare il pulsante 'Esporta'").
- Capacità o scopo di un sistema (es. "I.PaC è lo spazio dati progettato per preservare e gestire il patrimonio culturale digitale")."""
    },
    "entity-merging": {
        "allowed_entity_types": "ROLE, SYSTEM, TOOL, SYSTEM_MODULE, DOCUMENT, PROCESS, CONCEPT, ORGANIZATION, PERSON, PLAN, DATA_STANDARD",
        "entity_type_mappings": """Mappature tipi entità specifiche D.PaC:
- "Project Manager" O "PM" -> ROLE
- "Business Manager" O "BM" -> ROLE
- "Responsabile Istituto" O "RI" -> ROLE
- "Project Manager supporto" O "PM supporto" -> ROLE
- "Piattaforma D.PaC" O "Piattaforma di Digitalizzazione del patrimonio culturale" -> SYSTEM
- "I.PaC" O "Infrastruttura Software per il Patrimonio Culturale" -> SYSTEM
- "DPaaS" O "Data Product as a Service" -> SYSTEM
- "ServiceNow" O "Service Portal" -> SYSTEM
- "Cliente Axway" O "Client Axway" O "Axway CFT" -> TOOL
- "Checklist di Collaudo" O "Checklist di Prototipazione" -> DOCUMENT
- "Verbale di Inizio Lavori" O "Verbale di Fine Lavori" -> DOCUMENT
- "Studio di Fattibilità" O "Report Avanzamento Lotti" -> DOCUMENT
- "Modulo di Pianificazione" O "Modulo di Collaudo" O "Modulo Descrittivo" -> SYSTEM_MODULE
- "Business Intelligence" O "Modulo di Rendicontazione e Gestione OdA" -> SYSTEM_MODULE
- "Digitalizzazione" O "Recupero del Digitale Pregresso" O "Firma Digitale" -> PROCESS
- "Caricamento Pacchetti" O "Folder Monitoring" O "Chiusura Cantiere" -> PROCESS
- "Cantiere" O "Lotto di Digitalizzazione" O "Lotto di Descrizione" -> CONCEPT
- "Cluster" O "Fondo" O "Scheda" O "Dominio" O "Nomenclatura" -> CONCEPT
- "Digital Library" O "ICCD" O "ICAR" O "ICCU" -> ORGANIZATION
- "METS" O "NCTN" O "CIE" O "SPID" O "LDAP" -> DATA_STANDARD""",
        "key_attributes": "acronimi ruoli, nomi completi documenti, nomi moduli, passi di processo, nomi sistemi e piattaforme, nomi strumenti, tipi di lotti di lavoro, domini del patrimonio culturale, metodi di autenticazione"
    },
    "entity-normalization": {
        "entity_types": "ROLE, SYSTEM, TOOL, SYSTEM_MODULE, DOCUMENT, PROCESS, CONCEPT, ORGANIZATION, PERSON, PLAN, DATA_STANDARD",
        "normalization_rules": """Regole di normalizzazione entità specifiche D.PaC:
- Canonicalizza i ruoli ai relativi acronimi: "Project Manager" diventa "PM", "Business Manager" diventa "BM", "Responsabile Istituto" diventa "RI", "Project Manager supporto" diventa "PM supporto".
- Usa i nomi ufficiali dei documenti: "Verbale inizio lavori" diventa "Verbale di Inizio Lavori", "Verbale fine lavori" diventa "Verbale di Fine Lavori", "Studio fattibilità" diventa "Studio di Fattibilità".
- Standardizza i nomi dei moduli: "modulo di collaudo" diventa "Modulo di Collaudo", "modulo descrittivo" diventa "Modulo Descrittivo", "business intelligence" diventa "Business Intelligence".
- Usa acronimi per i sistemi: "Piattaforma di Digitalizzazione del patrimonio culturale" diventa "D_PAC"; "Infrastruttura Software per il Patrimonio Culturale" diventa "I_PAC"; "Data Product as a Service" diventa "DPAAS".
- Canonicalizza i nomi degli strumenti: "cliente Axway" diventa "Axway CFT"; "Piattaforma di formazione" diventa "Moodle".
- Standardizza i nomi dei lotti: "lotto digitalizzazione" diventa "LOTTO_DIGITALIZZAZIONE", "lotto descrizione" diventa "LOTTO_DESCRIZIONE", "lotto prototipazione" diventa "LOTTO_PROTOTIPAZIONE".
- Usa acronimi ufficiali delle organizzazioni: "Istituto Centrale per il Catalogo e la Documentazione" diventa "ICCD", "Istituto Centrale per gli Archivi" diventa "ICAR", "Istituto Centrale per il Catalogo Unico" diventa "ICCU".
- Standardizza i metodi di autenticazione: "Carta Identità Elettronica" diventa "CIE", "Sistema Pubblico Identità Digitale" diventa "SPID".""",
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


def it_configure_dpac_domain(gateway):
    """Configura il LLMGateway per il dominio D.PaC."""
    gateway.configure_domain_defaults(IT_DPAC_DOMAIN_CONFIG)
    return gateway


