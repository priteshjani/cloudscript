# CloudScript: Pharmacy Intelligence & Automation Platform

CloudScript is a reference implementation of an AI-powered healthcare automation pipeline on Google Cloud. It demonstrates the transition of paper/faxed prescriptions into structured, secure patient records across **Google Cloud Spanner**, **Google Cloud AlloyDB**, and **Cloud SQL PostgreSQL 18** databases.

The system showcases **Multi-Signal Hybrid Matching**: combining HNSW vector cosine embeddings (via Vertex AI text-embeddings and pgvector) with trigram fuzzy string parsing (pg_trgm) to accurately identify patient profiles despite typos, OCR artifacts, or name variations.

---

## 🌟 Core Features & Architecture

1.  **Stage 1: Ingest & OCR Extraction**
    *   Prescriptions arrive as images (fax/upload simulation).
    *   Gemini 2.5 Flash processes the document, extracting key fields (Patient Name, DOB, Insurance ID, Prescriber NPI, Medication, and Refills) in structured JSON format.
2.  **Stage 2: Match & Review (Multi-Signal Query)**
    *   AI search client executes weighted lookups on patient profiles:
        *   **Date of Birth** (35% weight)
        *   **Patient Name** (20% weight: HNSW vector similarity + trigram search score)
        *   **Insurance ID** (20% weight)
        *   **NPI / Fill History** (25% weight)
3.  **Stage 3: Verify & Dispense**
    *   Pharmacist validates the match. On confirmation, the system commits a transactional insert writing the prescription to the chosen target database.
---

## 🗺️ Ingestion Pipeline Architecture

```mermaid
graph TD
    A[Prescription Image / Fax] -->|Gemini 2.5 Flash OCR| B(Structured Fields JSON)
    B --> C{Hybrid Search Routing}
    C -->|Vector + Trigram Query| D[(Cloud SQL PostgreSQL 18)]
    C -->|Vector + Trigram Query| E[(Google Cloud AlloyDB)]
    C -->|Transactional Query| F[(Google Cloud Spanner)]
    D --> G(Patient Match Candidate List)
    E --> G
    F --> G
    G -->|Pharmacist Review / HITL| H{Dispense Approved?}
    H -->|Yes| I[Dispense Prescription Insert Transaction]
    I -->|Commit Row| J[(Target Active Database)]
```

---

## 🖥️ User Interface Preview

### 1. Ingest & Extract Ingest Pipeline
Simulated digital prescription scanner with real-time logging, Gemini extraction status pipeline logs, and extracted field validation cards:
![Ingest and Extract Scan](docs/screenshots/extraction.png)

### 2. Live Patient Matching & Review (Verify & Dispense)
Pharmacist interface displaying matches, similarity scoring metrics per patient profile, and secure transactional inserts:
![Pharmacy Dashboard Verification Screen](docs/screenshots/dashboard.png)

---

## 🛠️ Technology Stack

*   **Frontend**: React + Vite + Tailwind CSS dashboard (located under [cloudscript/frontend](file:///Users/priteshjani/Documents/jetski/cloudscript/frontend))
*   **Backend**: Python FastAPI backend service (located under [cloudscript/backend](file:///Users/priteshjani/Documents/jetski/cloudscript/backend))
*   **Databases Supported**:
    *   *Cloud SQL PostgreSQL 18*: Low-latency relational storage.
    *   *Google Cloud AlloyDB*: High-performance analytical and transaction engine.
    *   *Google Cloud Spanner*: Globally scalable transactional database.
*   **AI Models**: Gemini 2.5 Flash and Vertex AI text-embeddings.

---

## 📂 Directory Layout

```text
jetski/
├── cloudscript/             # Main Application Suite
│   ├── frontend/            # React Client Dashboard (white/soothing layout)
│   └── backend/             # Python FastAPI service, database client router
│       ├── main.py          # FastAPI application server and routers
│       ├── db_client.py     # Unified query router (Spanner, Cloud SQL, AlloyDB)
│       └── requirements.txt # Python requirements
├── skills/                  # Atomic database operations and MCP clients
│   ├── db/                  # Database orchestration and setup scripts
│   │   ├── cloudsql_setup/  # Setup and seed script for Cloud SQL PostgreSQL 18
│   │   ├── alloydb_setup/   # Setup and seed script for AlloyDB Cluster/Database
│   │   └── spanner_setup/   # Setup and seed script for Google Cloud Spanner
├── workflow/                # State machine & DAG orchestrators
│   └── examples/            # Reference workflows
│       ├── pharmacy_prescription_workflow.py # Pharmacy Ingestion Pipeline example
│       ├── db_sync_workflow.py              # Transactional -> Analytical sync
│       └── lakehouse_governance_workflow.py # Dataplex tagging workflow
├── config.example.json      # Configuration parameters template
└── README.md                # This file
```

---

## 🚀 Deployment & Getting Started

### Prerequisites
*   A **Google Cloud Project** with active billing.
*   Google Cloud SDK installed and authenticated on your local machine:
    ```bash
    gcloud auth application-default login
    ```

---

### 🗺️ Option A: Automated Infrastructure Deployment (With Terraform)

You can provision all required databases, Artifact Registry, and project APIs automatically using the provided Terraform script.

#### 1. Initialize and Run Terraform
Navigate to the `terraform/` directory, initialize the providers, and execute deployment:
```bash
cd terraform
terraform init
terraform apply -var="project_id=YOUR_GCP_PROJECT_ID"
```
*This automatically provisions: Enabled GCP APIs, Spanner Instance & Database, Cloud SQL PostgreSQL 18 Instance & Database, AlloyDB Cluster & Primary Instance, and Artifact Registry repository.*

#### 2. Copy and Configure Settings
Create your configuration file from the template and fill in your project ID:
```bash
cd ..
cp config.example.json config.json
```

#### 3. Seed Databases with Presets
Once the databases are created, run the python seeding scripts to create schemas and insert the Dorothy Thompson preset:
```bash
python3 skills/db/cloudsql_setup/setup_cloudsql.py
python3 skills/db/alloydb_setup/setup_alloydb.py
python3 skills/db/spanner_setup/setup_spanner.py
```

---

### 🗺️ Option B: Manual Infrastructure Deployment (Without Terraform)

If you prefer to use existing instances or configure resources manually, follow these steps:

#### 1. Enable Required APIs
Enable the following APIs in your Google Cloud Console:
```bash
gcloud services enable \
  aiplatform.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  sqladmin.googleapis.com \
  spanner.googleapis.com \
  alloydb.googleapis.com
```

#### 2. Create Database Resources
Ensure your GCP project has the following instances set up with their default names:
*   **Cloud SQL (PostgreSQL 15 or 18)**: Instance ID `cloudsql-demo`, Database `cloudsql-demo-db`, User `demo-user`.
*   **AlloyDB**: Cluster ID `alloydb-demo-cluster`, Instance ID `alloydb-inst`, Database `alloydb-demo-db`, User `demo-user`.
*   **Cloud Spanner**: Instance ID `spanner-demo-inst`, Database `spanner-demo-db`.
*   **Artifact Registry**: Docker Repository named `cloudscript-repo` in region `us-west4`.

#### 3. Copy and Configure Settings
```bash
cp config.example.json config.json
```
*(Open `config.json` and configure details for your manual instances).*

#### 4. Seed Databases with Presets
```bash
python3 skills/db/cloudsql_setup/setup_cloudsql.py
python3 skills/db/alloydb_setup/setup_alloydb.py
python3 skills/db/spanner_setup/setup_spanner.py
```

---

### 🖥️ Running the Application

#### 1. Run Local Frontend Development Server
Navigate to the frontend folder, install packages, and launch:
```bash
cd cloudscript/frontend
npm install
npm run dev
```

#### 2. Deploy Application Container to Cloud Run
To package and deploy the containerized application to Google Cloud Run:
```bash
cd cloudscript
gcloud builds submit --tag us-west4-docker.pkg.dev/YOUR_PROJECT_ID/cloudscript-repo/cloudscript:latest
gcloud run deploy cloudscript --image us-west4-docker.pkg.dev/YOUR_PROJECT_ID/cloudscript-repo/cloudscript:latest --platform managed --region us-west4
```
