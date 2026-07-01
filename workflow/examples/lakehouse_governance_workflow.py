import logging
from typing import Dict, Any
from workflow.base import BaseWorkflow
from agents.catalog_agent import CatalogAgent
from agents.db_agent import DatabaseAgent
from agents.analyst_agent import AnalystAgent
from skills.catalog.dataplex.dataplex_skills import DataplexCatalogSkills
from skills.db.spanner.spanner_skills import SpannerSkills
from skills.analytics.bigquery.bigquery_skills import BigQuerySkills

logger = logging.getLogger(__name__)

class LakehouseGovernanceWorkflow(BaseWorkflow):
    """
    Demonstrates Data Lakehouse operations:
    1. Discovers target reporting table using Dataplex Catalog.
    2. Extracts operational records from Spanner.
    3. Aggregates and loads reporting views in BigQuery.
    4. Attaches a 'Quality Status' tag in Dataplex Catalog.
    """
    def __init__(self):
        super().__init__(name="LakehouseGovernanceWorkflow")
        self.catalog_agent = CatalogAgent()
        self.db_agent = DatabaseAgent()
        self.analyst_agent = AnalystAgent()

        self.dataplex_skills = DataplexCatalogSkills()
        self.spanner_skills = SpannerSkills()
        self.bigquery_skills = BigQuerySkills()

    def run(self, initial_input: Dict[str, Any]) -> Dict[str, Any]:
        self.update_context(initial_input)

        # Step 1: Search Dataplex Catalog for target reports
        self.set_state("DISCOVER_ASSETS")
        logger.info("Searching Dataplex Catalog for Lakehouse targets...")
        assets = self.dataplex_skills.search_assets(query="type=table orders_summary")
        if not assets:
            raise ValueError("Target Lakehouse reporting table not found in Dataplex Catalog.")
        target_asset = assets[0]
        self.update_context({"target_asset": target_asset})

        # Step 2: Read operational inputs from Spanner
        self.set_state("EXTRACT_OPERATIONAL")
        logger.info("Reading source sales data from Spanner transactional schemas...")
        records = self.spanner_skills.execute_query("SELECT * FROM Orders")
        self.update_context({"source_records": records})

        # Step 3: Run pipeline aggregation and insert into BigQuery
        self.set_state("LOAD_LAKEHOUSE")
        logger.info("Inserting aggregated metrics into BigQuery reporting table...")
        bq_res = self.bigquery_skills.run_query(
            "INSERT INTO `lakehouse_ds.orders_summary` (SummaryDate, TotalAmount) VALUES ..."
        )
        self.update_context({"load_result": bq_res})

        # Step 4: Tag entry in Dataplex Catalog to show quality audit pass
        self.set_state("APPLY_GOVERNANCE")
        logger.info("Applying quality tag to Dataplex entry...")
        tag_status = self.dataplex_skills.create_entry_tag(
            entry_name=target_asset.get("entry_name"),
            template_name="DataQualityTemplate",
            fields={"audit_passed": True, "audited_by": "JetskiOrchestrator"}
        )
        self.update_context({"governance_tag_status": tag_status})

        self.set_state("COMPLETED")
        return {
            "status": "success",
            "state": self.state,
            "final_context": self.context
        }
