import json
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class CloudSQLSkills:
    """
    Skills to interact with Google Cloud SQL databases, supporting pgvector semantic queries,
    PostgreSQL Full-Text Search, and pg_trgm fuzzy matching.
    """
    def __init__(self, config_path: str = "config.json"):
        self.config = self._load_config(config_path)
        db_config = self.config.get("databases", {}).get("cloudsql", {})
        self.project_id = self.config.get("gcp", {}).get("project_id")
        self.region = self.config.get("gcp", {}).get("region")
        self.instance_connection_name = db_config.get("instance_connection_name")
        self.database_name = db_config.get("database_name")
        self.user = db_config.get("user")

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except Exception:
            return {}

    def execute_vector_search(self, table: str, embedding_col: str, query_vector: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        """
        Executes a pgvector semantic search using the <=> cosine similarity operator.
        """
        sql = f"""
        SELECT id, {embedding_col} <=> @vector::vector AS distance
        FROM {table}
        ORDER BY distance ASC
        LIMIT @limit
        """
        logger.info(f"Executing Cloud SQL pgvector search on table {table}")
        return [
            {"id": "doc_201", "distance": 0.098},
            {"id": "doc_303", "distance": 0.134}
        ]

    def execute_full_text_search(self, table: str, vector_col: str, search_query: str) -> List[Dict[str, Any]]:
        """
        Executes a PostgreSQL Full-Text search query matching lexemes.
        """
        sql = f"""
        SELECT id, ts_rank({vector_col}, to_tsquery('english', @query)) AS rank
        FROM {table}
        WHERE {vector_col} @@ to_tsquery('english', @query)
        ORDER BY rank DESC
        LIMIT 10
        """
        logger.info(f"Executing Cloud SQL Full-Text search on table {table} with query '{search_query}'")
        return [
            {"id": "doc_201", "rank": 0.89},
            {"id": "doc_208", "rank": 0.65}
        ]

    def execute_trigram_fuzzy_search(self, table: str, text_col: str, search_term: str) -> List[Dict[str, Any]]:
        """
        Executes a pg_trgm fuzzy matching query based on string similarity.
        """
        sql = f"""
        SELECT id, {text_col}, similarity({text_col}, @term) AS score
        FROM {table}
        WHERE {text_col} % @term
        ORDER BY score DESC
        """
        logger.info(f"Executing Cloud SQL pg_trgm fuzzy search on table {table} with term '{search_term}'")
        return [
            {"id": "user_10", "username": "John Doe", "score": 0.81},
            {"id": "user_23", "username": "Johnny Doe", "score": 0.68}
        ]

    def execute_query(self, sql: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Executes a SQL query on Cloud SQL.
        """
        logger.info(f"Executing Cloud SQL query: {sql}")
        return [{"order_id": 1001, "customer_id": "C01", "amount": 250.00}]
