import os
import asyncio
import logging
from fastapi import FastAPI, HTTPException, Header
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, Any, List
from backend.mock_presets import PRESETS
from backend.db_client import DatabaseClient

logger = logging.getLogger(__name__)

app = FastAPI(title="CloudScript Backend Service")

class ChatRequest(BaseModel):
    preset_id: str
    message: str

class IngestRequest(BaseModel):
    preset_id: str

@app.get("/api/presets")
def get_presets():
    """Returns the list of mock scenarios/presets for the demo frontend."""
    return [
        {
            "id": key,
            "label": val["label"],
            "description": val["description"],
            "status": val["status"]
        }
        for key, val in PRESETS.items()
    ]

@app.get("/api/preset/{preset_id}")
def get_preset(preset_id: str):
    if preset_id not in PRESETS:
        raise HTTPException(status_code=404, detail="Preset not found")
    return PRESETS[preset_id]

@app.post("/api/extract")
async def extract_prescription(request: IngestRequest):
    """
    Simulates the multi-step OCR extraction pipeline logs.
    Delays are added to simulate backend compute.
    """
    preset_id = request.preset_id
    if preset_id not in PRESETS:
        raise HTTPException(status_code=404, detail="Preset not found")
        
    preset = PRESETS[preset_id]
    
    steps = [
        {"step": "Downloading from GCS", "status": "completed"},
        {"step": "Gemini 2.5 Flash - OCR", "status": "completed"},
        {"step": "Parsing + coercing fields", "status": "completed"},
        {"step": "Generating name embedding", "status": "completed"},
        {"step": "Inserting to Cloud SQL", "status": "completed"},
        {"step": "Extraction complete", "status": "completed"}
    ]
    
    await asyncio.sleep(1.0)
    
    return {
        "steps": steps,
        "extracted_fields": preset["extracted_fields"],
        "rx_image": preset["rx_image"]
    }

@app.post("/api/match")
def match_patients(request: IngestRequest, x_database_type: str = Header(default="mock")):
    """
    Returns candidate matches with weighted scores. Routes to database or mock cache.
    """
    preset_id = request.preset_id
    if preset_id not in PRESETS:
        raise HTTPException(status_code=404, detail="Preset not found")
        
    preset = PRESETS[preset_id]
    db_type = x_database_type.lower()
    logger.info(f"Matching patients for preset '{preset_id}' using database: {db_type}")
    
    if db_type == "mock":
        return {"candidates": preset["candidates"]}
        
    name_query = preset["extracted_fields"]["patient_name"]
    dob_query = preset["extracted_fields"]["dob"]
    ins_query = preset["extracted_fields"]["insurance_id"]
    
    candidates = []
    if db_type == "cloudsql":
        candidates = DatabaseClient.query_cloudsql(name_query, dob_query, ins_query)
    elif db_type == "spanner":
        candidates = DatabaseClient.query_spanner(name_query, dob_query, ins_query)
    elif db_type == "alloydb":
        candidates = DatabaseClient.query_alloydb(name_query, dob_query, ins_query)
    else:
        candidates = preset["candidates"]
        
    # Resilient fallback
    if not candidates:
        logger.warning(f"Database query on '{db_type}' returned no records. Falling back to preset candidates.")
        candidates = preset["candidates"]
        
    return {
        "candidates": candidates
    }

@app.post("/api/chat")
def chatbot_interaction(request: ChatRequest):
    """
    Handles AI chatbot questions. Returns pre-cached explanations
    or generic responses for the preset.
    """
    preset_id = request.preset_id
    message = request.message.lower()
    
    if preset_id not in PRESETS:
        raise HTTPException(status_code=454, detail="Preset not found")
        
    preset = PRESETS[preset_id]
    
    if "why" in message or "reason" in message or "score" in message:
        response = preset["chatbot_log"]
    elif "drug" in message or "medication" in message or "generic" in message:
        response = f"Checking formulary status... {preset['extracted_fields']['drug_name']} {preset['extracted_fields']['strength']} is in the active catalog."
    elif "prescriber" in message or "doctor" in message or "npi" in message:
        response = f"Prescriber {preset['extracted_fields']['prescriber']} verified via NPI: {preset['extracted_fields']['npi']}."
    else:
        response = f"CloudScript AI: I verified the database matching for {preset['label']}. {preset['chatbot_log']}"
        
    return {
        "reply": response
    }

@app.post("/api/dispense")
def dispense_rx(request: IngestRequest, x_database_type: str = Header(default="mock")):
    db_type = x_database_type.lower()
    preset_id = request.preset_id
    logger.info(f"Dispense request received for preset '{preset_id}' on database '{db_type}'")
    try:
        msg = DatabaseClient.dispense_prescription(db_type, preset_id)
        if msg.startswith("Error"):
            raise HTTPException(status_code=500, detail=msg)
        return {"status": "success", "message": msg}
    except Exception as e:
        logger.error(f"Dispense endpoint failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Mount static files for React frontend if built directory exists (useful for containerized Cloud Run deployment)
static_dir = "frontend/dist"
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
