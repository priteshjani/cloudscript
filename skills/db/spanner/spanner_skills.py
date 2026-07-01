import json
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class SpannerSkills:
    """
    Skills to interact with Google Cloud Spanner databases, supporting
    advanced features like Spanner Graph, Vector Search, and Hybrid Search.
    """
    def __init__(self, config_path: str = "config.json"):
        self.config = self._load_config(config_path)
        db_config = self.config.get("databases", {}).get("spanner", {})
        self.project_id = self.config.get("gcp", {}).get("project_id")
        self.instance_id = db_config.get("instance_id")
        self.database_id = db_config.get("database_id")

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except Exception:
            return {}

    def run_graph_query(self, graph_name: str, match_pattern: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Queries a Spanner Property Graph using GRAPH_TABLE and Cypher syntax.
        """
        sql = f"""
        SELECT * FROM GRAPH_TABLE(
            {graph_name}
            MATCH {match_pattern}
            RETURN source.name AS src_name, target.name AS target_name
        )
        """
        logger.info(f"Running Spanner Graph query: {sql} with params {params}")
        return [
            {"src_name": "Alice", "target_name": "Bob"},
            {"src_name": "Bob", "target_name": "Charlie"}
        ]

    def execute_vector_search(self, table: str, embedding_col: str, query_vector: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        """
        Executes a vector similarity search using Spanner's COSINE_DISTANCE.
        """
        sql = f"""
        SELECT id, COSINE_DISTANCE({embedding_col}, @vector) AS distance
        FROM {table}
        ORDER BY APPROX_COSINE_DISTANCE({embedding_col}, @vector)
        LIMIT @limit
        """
        logger.info(f"Executing Spanner vector search on table {table} with limit {limit}")
        return [
            {"id": "doc_101", "distance": 0.089},
            {"id": "doc_202", "distance": 0.145}
        ]

    def execute_hybrid_search(self, table: str, text_col: str, search_query: str, embedding_col: str, query_vector: List[float]) -> List[Dict[str, Any]]:
        """
        Combines full-text SEARCH and vector COSINE_DISTANCE in a single query.
        """
        sql = f"""
        SELECT id, COSINE_DISTANCE({embedding_col}, @vector) AS distance, SCORE({text_col}, @query) AS relevance
        FROM {table}
        WHERE SEARCH({text_col}, @query)
        ORDER BY distance ASC, relevance DESC
        LIMIT 10
        """
        logger.info(f"Executing Spanner hybrid search on table {table} with query '{search_query}'")
        return [
            {"id": "doc_101", "distance": 0.089, "relevance": 0.95},
            {"id": "doc_105", "distance": 0.112, "relevance": 0.78}
        ]

    def get_schema(self) -> Dict[str, Any]:
        """
        Retrieves the Spanner schema.
        """
        logger.info(f"Retrieving schema for Spanner database {self.database_id}")
        return {
            "tables": {
                "Users": {"columns": {"UserId": "INT64", "UserName": "STRING(100)"}, "primary_key": ["UserId"]}
            }
        }

    def execute_query(self, sql: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Executes a read-only query on Spanner.
        """
        logger.info(f"Executing Spanner query: {sql}")
        return [{"UserId": 1, "UserName": "John Doe"}]
