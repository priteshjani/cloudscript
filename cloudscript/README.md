# CloudScript: Pharmacy Intelligence Demo

This is a self-contained demonstration project showing AI-powered prescription processing on Google Cloud. It uses a React frontend and a FastAPI backend to show how structured fields, patient candidates matching, and chatbot verification loops operate in a transactional pharmacy queue.

## Features Illustrated
- **Stage 1 (Ingest + Extract)**: Visualizes Gemini 2.5 Flash performing OCR extraction on PDF prescription scans.
- **Stage 2 (Match + Review)**: Visualizes how pgvector and pg_trgm similarity queries match extracted parameters against patient databases using a weighted scoring engine.
- **Stage 3 (Verify & Dispense)**: Final checkpoint and record commit to Cloud SQL.
- **AI Assistant Chatbot**: Natural language bot answering questions about match scores, patient NPI/DEA validations, and drug history.

## Tech Stack
- **Frontend**: React (Vite + Tailwind CSS v4 + Lucide Icons)
- **Backend**: Python 3.10+ (FastAPI + Uvicorn)

## Folder Layout
```text
cloudscript/
├── backend/
│   ├── main.py            # FastAPI endpoints (OCR, candidates match, chatbot)
│   ├── mock_presets.py    # Pre-cached scenario definitions (Dorothy, Bob, Maria, etc.)
│   └── requirements.txt   # Python backend packages
├── frontend/
│   ├── src/               # React application code
│   │   ├── App.jsx        # Main UI tabs and logic
│   │   └── main.jsx       # React DOM entrypoint
│   ├── package.json       # Frontend scripts and deps
│   └── vite.config.js     # Dev proxy configuration
├── Dockerfile             # Unified Dockerfile for containerized deployment
└── README.md              # This guide
```

---

## Running the Demo Locally

### 1. Start the Backend
1. Open a terminal and navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the FastAPI server using uvicorn on port `3001` (to match the Vite dev proxy):
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 3001
   ```

### 2. Start the Frontend
1. Open a second terminal window and navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Start the Vite React development server:
   ```bash
   npm run dev
   ```
3. Open your browser and navigate to the local URL (usually `http://localhost:5173`).

---

## Deploying to Google Cloud Run (Containerized)

The application can be deployed as a unified single-container app to Cloud Run. The React frontend is built locally into static assets and packaged inside the FastAPI container.

### Step 1: Build the React Assets Locally
```bash
cd frontend
npm run build
cd ..
```

### Step 2: Create Artifact Registry Repository (if not already done)
```bash
gcloud artifacts repositories create cloudscript-repo \
  --repository-format=docker \
  --location=us-west4 \
  --description="Docker repository for CloudScript pharmacy demo"
```

### Step 3: Build & Push Image using Cloud Build
```bash
gcloud builds submit --tag us-west4-docker.pkg.dev/my-host-prj-472917/cloudscript-repo/cloudscript:latest
```

### Step 4: Deploy to Cloud Run
```bash
gcloud run deploy cloudscript \
  --image us-west4-docker.pkg.dev/my-host-prj-472917/cloudscript-repo/cloudscript:latest \
  --platform managed \
  --region us-west4 \
  --project my-host-prj-472917
```

*Note: Due to standard corporate sandbox organization policy restrictions (`constraints/iam.allowedPolicyMemberDomains`), the service cannot be set to allow unauthenticated public users. You must access the URL using your authenticated Google Workspace credentials.*

---

## Pushing to GitHub

A local git repository has been initialized and committed in this folder. To publish it to GitHub:

1. Create a new repository on your GitHub account (e.g. named `cloudscript`).
2. Add the remote origin and push:
   ```bash
   git remote add origin https://github.com/YOUR_GITHUB_USERNAME/cloudscript.git
   git branch -M main
   git push -u origin main
   ```
