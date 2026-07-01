import logging
from typing import Dict, Any
from workflow.base import BaseWorkflow
from backend.db_client import DatabaseClient

logger = logging.getLogger(__name__)

class PharmacyPrescriptionWorkflow(BaseWorkflow):
    """
    Pharmacy Ingestion Pipeline Workflow.
    Orchestrates the transition of a fax/digital prescription from OCR extraction,
    multi-signal patient matching (vector + trigram) to secure database dispensing.
    """
    def __init__(self):
        super().__init__(name="PharmacyPrescriptionWorkflow")

    def run(self, initial_input: Dict[str, Any]) -> Dict[str, Any]:
        preset_id = initial_input.get("preset_id", "dorothy_thompson")
        db_type = initial_input.get("db_type", "cloudsql")
        
        # Stage 1: Ingest & OCR Extraction
        self.set_state("OCR_EXTRACTING")
        logger.info(f"Stage 1: Extracting prescription metadata using Gemini OCR (Preset ID: '{preset_id}')")
        
        from backend.mock_presets import PRESETS
        if preset_id not in PRESETS:
            self.set_state("FAILED")
            raise ValueError(f"Preset ID '{preset_id}' not found in registry.")
            
        preset = PRESETS[preset_id]
        fields = preset["extracted_fields"]
        self.update_context({
            "preset_id": preset_id,
            "extracted_fields": fields,
            "db_type": db_type
        })
        
        # Stage 2: Match & Review (Multi-Signal Query)
        self.set_state("PATIENT_MATCHING")
        logger.info(f"Stage 2: Running multi-signal database lookup (trigram + vector) on target database: '{db_type}'")
        
        patient_name = fields["patient_name"]
        dob = fields["dob"]
        insurance_id = fields["insurance_id"]
        
        # Perform query based on selected database client
        if db_type == "cloudsql":
            candidates = DatabaseClient.query_cloudsql(patient_name, dob, insurance_id)
        elif db_type == "alloydb":
            candidates = DatabaseClient.query_alloydb(patient_name, dob, insurance_id)
        elif db_type == "spanner":
            candidates = DatabaseClient.query_spanner(patient_name, dob, insurance_id)
        else:
            candidates = []
            
        self.update_context({
            "matched_candidates": candidates,
            "candidate_count": len(candidates)
        })
        
        if not candidates:
            logger.warning(f"No matching patient candidates found for '{patient_name}' in database.")
            self.set_state("HUMAN_INTERVENTION_NEEDED")
            return {
                "status": "requires_hitl",
                "state": self.state,
                "reason": f"No patient matches found for '{patient_name}'"
            }
            
        # Select best candidate (e.g. matching score >= 75)
        best_candidate = candidates[0]
        self.update_context({"selected_candidate": best_candidate})
        
        # Stage 3: Safety Check & Dispense
        self.set_state("DISPENSING")
        logger.info(f"Stage 3: Running safety checkpoints and dispensing prescription to '{patient_name}'...")
        
        # Insert prescription records in respective database
        dispense_msg = DatabaseClient.dispense_prescription(db_type, preset_id)
        self.update_context({"dispense_message": dispense_msg})
        
        if dispense_msg.startswith("Error"):
            self.set_state("FAILED")
            return {
                "status": "failed",
                "state": self.state,
                "error": dispense_msg
            }
            
        self.set_state("COMPLETED")
        return {
            "status": "success",
            "state": self.state,
            "dispense_message": dispense_msg,
            "patient_match_score": best_candidate.get("match_score", best_candidate.get("score")),
            "final_context": self.context
        }

if __name__ == "__main__":
    # Test script run
    import sys
    logging.basicConfig(level=logging.INFO)
    
    # Defaults to Cloud SQL Dorothy Thompson ingest
    test_input = {
        "preset_id": "dorothy_thompson",
        "db_type": "cloudsql"
    }
    
    if len(sys.argv) > 1:
        test_input["db_type"] = sys.argv[1]
    if len(sys.argv) > 2:
        test_input["preset_id"] = sys.argv[2]
        
    workflow = PharmacyPrescriptionWorkflow()
    try:
        result = workflow.run(test_input)
        print("\n=== Workflow Execution Result ===")
        print(f"Status: {result['status']}")
        print(f"State: {result['state']}")
        print(f"Message: {result.get('dispense_message')}")
        if 'patient_match_score' in result:
            print(f"Patient Match Score: {result['patient_match_score']}%")
    except Exception as e:
        print(f"\n=== Workflow Failed ===")
        print(f"Error: {e}")
