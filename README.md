# Jetski Agentic Framework: Core Demo Platform

Welcome to the Jetski Agentic Demo Framework. This repository is built as a reference architecture combining a modern React-based frontend (`dbce/`) with a modular, stateful Python-based backend that orchestrates autonomous agents, workflows, and database-specific skills.

## Core Tech Stack

- **Frontend**: React UI (under [dbce/](file:///Users/priteshjani/Documents/jetski/dbce))
- **Backend**: Python 3.10+ (Agents, Workflows, Skills)
- **Database & Data Cloud Engines Supported**:
  - *Relational*: Google Cloud Spanner, AlloyDB, Cloud SQL
  - *NoSQL & Document*: Cloud Firestore, Cloud Bigtable
  - *Cache*: Cloud Memorystore for Redis
  - *Analytics & Lakehouse*: Google Cloud BigQuery
  - *Data Discovery & Governance*: Google Cloud Dataplex / Knowledge Catalog
- **Interoperability**: Model Context Protocol (MCP) support for dynamic tool binding.

---

## Directory Layout

```text
jetski/
├── dbce/                    # React Frontend
├── agents/                  # AI Agent definitions and prompts
│   ├── README.md            # [Deep Technical] Agent architectures & prompting rules
│   ├── base.py              # BaseAgent abstract class
│   ├── db_agent.py          # Database Agent (Relational databases)
│   ├── nosql_agent.py       # NoSQL Agent (Bigtable, Firestore, Memorystore)
│   ├── analyst_agent.py     # Analyst Agent (BigQuery analytics)
│   └── catalog_agent.py     # Catalog Agent (Dataplex discovery & governance)
├── skills/                  # Atomic database operations and MCP clients
│   ├── README.md            # [Deep Technical] Client connection & authentication rules
│   ├── db/                  # Relational database skills
│   │   ├── spanner/
│   │   ├── alloydb/
│   │   └── cloudsql/
│   ├── nosql/               # NoSQL, cache, and document skills
│   │   ├── bigtable/
│   │   ├── firestore/
│   │   └── memorystore/
│   ├── analytics/           # BigQuery skills
│   │   └── bigquery/
│   ├── catalog/             # Dataplex Catalog discovery skills
│   │   └── dataplex/
│   └── mcp_client/          # Model Context Protocol wrappers
│       └── mcp_client.py
├── workflow/                # State machine & DAG orchestrators
│   ├── README.md            # [Deep Technical] States, rollbacks, and HITL mechanics
│   ├── base.py              # BaseWorkflow state coordinator
│   ├── orchestrator.py      # Core execution registry
│   └── examples/            # Reference workflows
│       ├── db_sync_workflow.py       # Spanner -> BigQuery replication
│       ├── data_pipeline_workflow.py  # Cloud SQL -> Firestore -> Memorystore -> BigQuery
│       └── lakehouse_governance_workflow.py # Dataplex Catalog -> Spanner -> BigQuery -> Dataplex Tagging
├── config.json              # Unified GCP and database parameters configuration
├── requirements.txt         # Core Python dependencies
└── README.md                # This file
```

---

## Getting Started

### 1. Credentials & Configuration
Authenticate with Google Cloud using Application Default Credentials (ADC):
```bash
gcloud auth application-default login
```

Configure your GCP settings by updating [config.json](file:///Users/priteshjani/Documents/jetski/config.json).

### 2. Backend Setup
Create and activate your Python virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Frontend Setup
See the [dbce README](file:///Users/priteshjani/Documents/jetski/dbce/README.md) to launch the React development server.
