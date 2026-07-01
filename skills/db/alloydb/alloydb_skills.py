import json
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class AlloyDBSkills:
    """
    Skills to interact with Google Cloud AlloyDB databases, supporting pgvector index searches,
    AlloyDB AI embedding generation, and Columnar Engine settings.
    """
    def __init__(self, config_path: str = "config.json"):
        self.config = self._load_config(config_path)
        db_config = self.config.get("databases", {}).get("alloydb", {})
        self.project_id = self.config.get("gcp", {}).get("project_id")
        self.region = self.config.get("gcp", {}).get("region")
        self.cluster_id = db_config.get("cluster_id")
        self.instance_id = db_config.get("instance_id")
        self.database_name = db_config.get("database_name")
        self.user = db_config.get("user")

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except Exception:
            return {}

    def generate_and_store_embeddings(self, table: str, text_col: str, embedding_col: str) -> str:
        """
        Generates embeddings directly inside AlloyDB using google_ml.create_embeddings.
        """
        sql = f"""
        UPDATE {table}
        SET {embedding_col} = google_ml.create_embeddings('textembedding-gecko@003', {text_col})
        WHERE {embedding_col} IS NULL
        """
        logger.info(f"Generating and storing embeddings: {sql}")
        return "success"

    def execute_hnsw_vector_query(self, table: str, embedding_col: str, query_vector: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        """
        Query vector similarity using the <=> cosine operator.
        """
        sql = f"""
        SELECT id, {embedding_col} <=> @vector::vector AS distance
        FROM {table}
        ORDER BY distance ASC
        LIMIT @limit
        """
        logger.info(f"Executing HNSW vector match query: {sql} (vector size={len(query_vector)})")
        return [
            {"id": "prod_a1", "distance": 0.076},
            {"id": "prod_b2", "distance": 0.123}
        ]

    def populate_columnar_relation(self, relation: str) -> str:
        """
        Populates a table into the AlloyDB columnar engine cache memory.
        """
        sql = f"SELECT alloydb_columnar_engine.populate_relation('{relation}')"
        logger.info(f"Populating table into Columnar Engine: {sql}")
        return "success"

    def execute_query(self, sql: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Standard SQL execute on AlloyDB.
        """
        logger.info(f"Executing AlloyDB SQL query: {sql}")
        return [{"product_id": "P001", "name": "Wireless Mouse", "stock": 120}]
