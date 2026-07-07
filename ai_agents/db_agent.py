import logging
from typing import Dict, Any
from agents.base import BaseAgent

logger = logging.getLogger(__name__)

class DatabaseAgent(BaseAgent):
    """
    Agent specialized in exploring, querying, and verifying schemas
    across relational databases (AlloyDB, Spanner, CloudSQL).
    """
    def __init__(self, config_path: str = "config.json"):
        system_prompt = (
            "You specialize in relational database operations. Your objective is to assist "
            "with inspecting schemas, drafting queries, and checking database status. "
            "You have access to AlloyDB, Spanner, and CloudSQL tools. "
            "Always follow security guidelines: never drop production tables, "
            "use parameterized queries, and limit query results to 100 rows unless requested."
        )
        super().__init__(
            name="DB-Whisperer",
            role="Database Specialist Agent",
            system_prompt=system_prompt,
            config_path=config_path
        )

    def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Executes a database inspection/query task.
        """
        logger.info(f"{self.name} starting task: {task}")
        context = context or {}
        
        response = {
            "status": "success",
            "message": f"Successfully planned DB operation for task: '{task}'",
            "suggested_actions": ["check_spanner_schema", "query_alloydb_metadata"],
            "context_updates": {
                "active_db": "spanner",
                "spanner_instance": self.config.get("databases", {}).get("spanner", {}).get("instance_id")
            }
        }
        
        return response
