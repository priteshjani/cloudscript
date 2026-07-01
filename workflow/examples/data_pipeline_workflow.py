import logging
from typing import Dict, Any
from workflow.base import BaseWorkflow
from agents.db_agent import DatabaseAgent
from agents.nosql_agent import NoSQLAgent
from agents.analyst_agent import AnalystAgent
from skills.db.cloudsql.cloudsql_skills import CloudSQLSkills
from skills.nosql.firestore.firestore_skills import FirestoreSkills
from skills.nosql.memorystore.memorystore_skills import MemorystoreSkills
from skills.analytics.bigquery.bigquery_skills import BigQuerySkills

logger = logging.getLogger(__name__)

class DataPipelineWorkflow(BaseWorkflow):
    """
    Framework demonstration workflow:
    1. Extracts transactional data from Cloud SQL.
    2. Enriches records and updates Firestore documents.
    3. Caches lookup tables in Memorystore (Redis).
    4. Syncs aggregated metrics into BigQuery for reporting.
    """
    def __init__(self):
        super().__init__(name="DataPipelineWorkflow")
        self.db_agent = DatabaseAgent()
        self.nosql_agent = NoSQLAgent()
        self.analyst_agent = AnalystAgent()
        
        self.cloudsql_skills = CloudSQLSkills()
        self.firestore_skills = FirestoreSkills()
        self.memorystore_skills = MemorystoreSkills()
        self.bigquery_skills = BigQuerySkills()

    def run(self, initial_input: Dict[str, Any]) -> Dict[str, Any]:
        self.update_context(initial_input)
        
        # Step 1: Read from Cloud SQL
        self.set_state("EXTRACT_SQL")
        logger.info("Extracting transactional orders from Cloud SQL...")
        orders = self.cloudsql_skills.execute_query("SELECT * FROM Orders WHERE status = 'PENDING'")
        self.update_context({"extracted_orders": orders})

        # Step 2: Validate & enrich document store (Firestore)
        self.set_state("ENRICH_NOSQL")
        logger.info("Enriching customer profiles in Firestore...")
        for order in orders:
            customer_id = order.get("customer_id")
            doc = self.firestore_skills.get_document("customers", customer_id)
            order["customer_email"] = doc.get("email", "unknown@example.com")
            
        # Step 3: Cache active order list in Memorystore (Redis)
        self.set_state("CACHE_WARMUP")
        logger.info("Warming cache in Memorystore (Redis)...")
        cache_key = f"jetski:orders:pending"
        self.memorystore_skills.set_cache(cache_key, str(orders), ttl_seconds=600)

        # Step 4: Run BigQuery aggregation pipeline
        self.set_state("LOAD_ANALYTICS")
        logger.info("Running BigQuery analytics query...")
        bq_res = self.bigquery_skills.run_query(
            "SELECT COUNT(1) as total_pending FROM `my_dataset.orders` WHERE status = 'PENDING'"
        )
        self.update_context({"analytics_summary": bq_res})

        # Step 5: Verification by Analyst Agent
        self.set_state("AUDIT_VERIFICATION")
        audit_resp = self.analyst_agent.execute(
            task="Audit transactional order counts against BigQuery aggregations.",
            context=self.context
        )
        self.update_context(audit_resp.get("context_updates", {}))

        self.set_state("COMPLETED")
        return {
            "status": "success",
            "state": self.state,
            "final_context": self.context
        }
