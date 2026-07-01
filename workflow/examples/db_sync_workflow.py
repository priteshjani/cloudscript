import logging
from typing import Dict, Any
from workflow.base import BaseWorkflow
from agents.db_agent import DatabaseAgent
from agents.analyst_agent import AnalystAgent
from skills.db.spanner.spanner_skills import SpannerSkills
from skills.analytics.bigquery.bigquery_skills import BigQuerySkills

logger = logging.getLogger(__name__)

class DBSyncWorkflow(BaseWorkflow):
    """
    Example workflow to replicate/sync records from a transactional database (Spanner)
    to an analytical database (BigQuery).
    """
    def __init__(self):
        super().__init__(name="DBSyncWorkflow")
        self.db_agent = DatabaseAgent()
        self.analyst_agent = AnalystAgent()
        self.spanner_skills = SpannerSkills()
        self.bigquery_skills = BigQuerySkills()

    def run(self, initial_input: Dict[str, Any]) -> Dict[str, Any]:
        self.set_state("READING_SOURCE")
        self.update_context(initial_input)
        
        # Step 1: Read data from Spanner
        logger.info("Step 1: Reading records from Spanner source...")
        try:
            records = self.spanner_skills.execute_query("SELECT * FROM Users")
            self.update_context({"source_records": records})
        except Exception as e:
            self.set_state("FAILED")
            raise RuntimeError(f"Failed to read from Spanner: {e}")

        # Step 2: Formulate loading plan using database agent
        self.set_state("PLANNING_LOAD")
        agent_resp = self.db_agent.execute(
            task=f"Formulate a partition loading plan for {len(records)} records into BigQuery target dataset.",
            context=self.context
        )
        self.update_context(agent_resp.get("context_updates", {}))

        # Step 3: Run insert query in BigQuery
        self.set_state("WRITING_TARGET")
        target_dataset = self.context.get("dataset_id")
        logger.info(f"Step 3: Loading records into BigQuery dataset '{target_dataset}'...")
        
        bq_result = self.bigquery_skills.run_query(
            f"INSERT INTO `{target_dataset}.users` (UserId, UserName, Email) VALUES ..."
        )
        self.update_context({"bq_write_result": bq_result})

        # Step 4: Run analyst verification
        self.set_state("VERIFYING")
        analysis_resp = self.analyst_agent.execute(
            task="Verify sync integrity and compile a record count audit report.",
            context=self.context
        )
        self.update_context(analysis_resp.get("context_updates", {}))

        self.set_state("COMPLETED")
        return {
            "status": "success",
            "state": self.state,
            "final_context": self.context
        }
