import os
import json
import logging
from typing import List, Dict, Any
import pg8000

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Config loading helper
def load_config(config_path: str = "config.json") -> Dict[str, Any]:
    try:
        # Check parent folder or local path depending on execution context
        path = config_path
        if not os.path.exists(path):
            path = os.path.join("..", config_path)
        if not os.path.exists(path):
            path = "/Users/priteshjani/Documents/jetski/config.json"
            
        with open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load config.json: {e}")
        return {}

CONFIG = load_config()

class DatabaseClient:
    """Unified client to query patient matching data across different GCP databases."""
    
    @staticmethod
    def query_cloudsql(name_query: str, dob_query: str, ins_query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Queries Cloud SQL PostgreSQL 18 database using pgvector and pg_trgm similarity."""
        db_config = CONFIG.get("databases", {}).get("cloudsql", {})
        host = db_config.get("host", "127.0.0.1")
        port = int(db_config.get("port", 5432))
        database = db_config.get("database_name", "cloudsql-demo-db")
        user = db_config.get("user", "demo-user")
        password = db_config.get("password", "Password123!")
        
        is_cloud_run = os.environ.get("K_SERVICE") is not None
        instance_connection_name = db_config.get("instance_connection_name", "my-host-prj-472917:us-west4:cloudsql-demo")

        try:
            if is_cloud_run:
                unix_sock = f"/cloudsql/{instance_connection_name}/.s.PGSQL.5432"
                logger.info(f"Running on Cloud Run. Connecting to database via Unix socket: {unix_sock}")
                conn = pg8000.dbapi.connect(
                    unix_sock=unix_sock,
                    database=database,
                    user=user,
                    password=password
                )
            else:
                logger.info(f"Running locally. Connecting to database via TCP: {host}:{port}")
                conn = pg8000.dbapi.connect(
                    host=host,
                    port=port,
                    database=database,
                    user=user,
                    password=password
                )
            cursor = conn.cursor()
            
            # Since we don't have active Vertex AI API calls, we generate a mock query vector 
            # for the query. To make it match presets, we check if the query name matches 
            # our seeded profiles. Otherwise, we generate a random query vector.
            query_vector = DatabaseClient._get_seed_vector_for_name(name_query)
            qvec_str = "[" + ",".join(map(str, query_vector)) + "]"
            
            # Weighted Scoring Query:
            # - Cosine similarity (1 - distance) on name embedding: weight 0.50
            # - Trigram similarity (word similarity) on name string: weight 0.20
            # - DOB match (1.0 if identical, 0.0 if not): weight 0.15
            # - Zip code match (1.0 if identical, 0.0 if not): weight 0.10
            # - Insurance match (1.0 if identical, 0.0 if not): weight 0.05
            sql = """
                SELECT 
                    id, 
                    name, 
                    dob, 
                    insurance_id, 
                    zip_code, 
                    gender,
                    (1 - (name_embedding <=> %s))::float AS vector_similarity,
                    similarity(name, %s)::float AS string_similarity,
                    CASE WHEN dob = %s THEN 1.0 ELSE 0.0 END AS dob_match,
                    CASE WHEN insurance_id = %s THEN 1.0 ELSE 0.0 END AS ins_match
                FROM patients
                ORDER BY 
                    ((1 - (name_embedding <=> %s)) * 0.50 + 
                     similarity(name, %s) * 0.20 + 
                     (CASE WHEN dob = %s THEN 1.0 ELSE 0.0 END) * 0.15 +
                     (CASE WHEN insurance_id = %s THEN 1.0 ELSE 0.0 END) * 0.05) DESC
                LIMIT %s;
            """
            
            # Execute SQL
            cursor.execute(sql, (qvec_str, name_query, dob_query, ins_query, qvec_str, name_query, dob_query, ins_query, limit))
            rows = cursor.fetchall()
            
            candidates = []
            for row in rows:
                pid, name, dob, ins, zip_code, gender, vec_sim, str_sim, dob_match, ins_match = row
                
                # Compute total weighted matching score
                match_score = int((vec_sim * 0.50 + str_sim * 0.20 + dob_match * 0.15 + ins_match * 0.05) * 100)
                # Keep score within 0-100 range
                match_score = max(0, min(100, match_score))
                
                candidates.append({
                    "id": str(pid),
                    "name": name,
                    "dob": str(dob),
                    "insurance_id": ins,
                    "zip_code": zip_code,
                    "gender": gender,
                    "match_score": match_score,
                    "details": {
                        "name_embedding_similarity": int(vec_sim * 100),
                        "name_fuzzy_match": int(str_sim * 100),
                        "dob_match": dob_match > 0.9,
                        "insurance_id_match": ins_match > 0.9
                    }
                })
            
            conn.close()
            return candidates
        except Exception as e:
            logger.error(f"Error querying Cloud SQL: {e}", exc_info=True)
            return []

    @staticmethod
    def query_alloydb(name_query: str, dob_query: str, ins_query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Queries AlloyDB database using pgvector and pg_trgm similarity."""
        db_config = CONFIG.get("databases", {}).get("alloydb", {})
        project_id = CONFIG.get("gcp", {}).get("project_id", "my-host-prj-472917")
        region = CONFIG.get("gcp", {}).get("region", "us-west4")
        cluster_id = db_config.get("cluster_id", "alloydb-demo-cluster")
        instance_id = db_config.get("instance_id", "alloydb-inst")
        database = db_config.get("database_name", "alloydb-demo-db")
        user = db_config.get("user", "demo-user")
        password = db_config.get("password", "Password123!")

        try:
            from google.cloud.alloydb.connector import Connector
            connector = Connector()
            instance_connection_path = f"projects/{project_id}/locations/{region}/clusters/{cluster_id}/instances/{instance_id}"
            
            logger.info(f"Connecting to AlloyDB via Python Connector: {instance_connection_path}")
            conn = connector.connect(
                instance_connection_path,
                "pg8000",
                user=user,
                password=password,
                db=database,
                enable_iam_auth=False,
                ip_type="public"
            )
            cursor = conn.cursor()
            
            query_vector = DatabaseClient._get_seed_vector_for_name(name_query)
            qvec_str = "[" + ",".join(map(str, query_vector)) + "]"
            
            sql = """
                SELECT 
                    id, 
                    name, 
                    dob, 
                    insurance_id, 
                    zip_code, 
                    gender,
                    (1 - (name_embedding <=> %s))::float AS vector_similarity,
                    similarity(name, %s)::float AS string_similarity,
                    CASE WHEN dob = %s THEN 1.0 ELSE 0.0 END AS dob_match,
                    CASE WHEN insurance_id = %s THEN 1.0 ELSE 0.0 END AS ins_match
                FROM patients
                ORDER BY 
                    ((1 - (name_embedding <=> %s)) * 0.50 + 
                     similarity(name, %s) * 0.20 + 
                     (CASE WHEN dob = %s THEN 1.0 ELSE 0.0 END) * 0.15 +
                     (CASE WHEN insurance_id = %s THEN 1.0 ELSE 0.0 END) * 0.05) DESC
                LIMIT %s;
            """
            
            cursor.execute(sql, (qvec_str, name_query, dob_query, ins_query, qvec_str, name_query, dob_query, ins_query, limit))
            rows = cursor.fetchall()
            
            candidates = []
            for row in rows:
                pid, name, dob, ins, zip_code, gender, vec_sim, str_sim, dob_match, ins_match = row
                match_score = int((vec_sim * 0.50 + str_sim * 0.20 + dob_match * 0.15 + ins_match * 0.05) * 100)
                match_score = max(0, min(100, match_score))
                
                candidates.append({
                    "id": str(pid),
                    "name": name,
                    "dob": str(dob),
                    "insurance_id": ins,
                    "zip_code": zip_code,
                    "gender": gender,
                    "match_score": match_score,
                    "details": {
                        "name_embedding_similarity": int(vec_sim * 100),
                        "name_fuzzy_match": int(str_sim * 100),
                        "dob_match": dob_match > 0.9,
                        "insurance_id_match": ins_match > 0.9
                    }
                })
            
            conn.close()
            connector.close()
            return candidates
        except Exception as e:
            logger.error(f"Error querying AlloyDB: {e}", exc_info=True)
            return []

    @staticmethod
    def query_spanner(name_query: str, dob_query: str, ins_query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Queries Google Cloud Spanner database using SQL and Array Cosine Similarity calculation."""
        db_config = CONFIG.get("databases", {}).get("spanner", {})
        project_id = CONFIG.get("gcp", {}).get("project_id")
        instance_id = db_config.get("instance_id", "spanner-demo-inst")
        database_id = db_config.get("database_id", "spanner-demo-db")

        try:
            from google.cloud import spanner
            client = spanner.Client(project=project_id)
            instance = client.instance(instance_id)
            database = instance.database(database_id)
            
            query_vector = DatabaseClient._get_seed_vector_for_name(name_query)

            # Spanner does not support pgvector <=> or similarity() out of the box,
            # so we perform a cosine similarity calculation over arrays using Spanner SQL functions:
            # cosine_similarity = dot_product(A, B) / (norm(A) * norm(B))
            # Since our vector entries are pre-normalized in seed data (norm = 1.0),
            # cosine_similarity is just the dot product of A and B: sum(A[i] * B[i])!
            # And for fuzzy match, we use standard edit distance or LIKE similarity.
            sql = """
                SELECT 
                    id, 
                    name, 
                    dob, 
                    insurance_id, 
                    zip_code, 
                    gender,
                    (
                      SELECT SUM(x * y) 
                      FROM UNNEST(name_embedding) AS x WITH OFFSET idx 
                      JOIN UNNEST(@query_vector) AS y WITH OFFSET idx2 ON idx = idx2
                    ) AS dot_product,
                    CASE WHEN LOWER(name) LIKE LOWER(@name_like) THEN 1.0 ELSE 0.0 END AS name_like_match,
                    CASE WHEN dob = @dob THEN 1.0 ELSE 0.0 END AS dob_match,
                    CASE WHEN insurance_id = @insurance_id THEN 1.0 ELSE 0.0 END AS ins_match
                FROM patients
                ORDER BY 
                    (dot_product * 0.60 + 
                     name_like_match * 0.15 + 
                     dob_match * 0.15 + 
                     ins_match * 0.10) DESC
                LIMIT @limit
            """
            
            params = {
                "query_vector": query_vector,
                "name_like": f"%{name_query.split()[0]}%", # Query prefix match
                "dob": spanner.parse_date(dob_query),
                "insurance_id": ins_query,
                "limit": limit
            }
            param_types = {
                "query_vector": spanner.param_types.Array(spanner.param_types.FLOAT64),
                "name_like": spanner.param_types.STRING,
                "dob": spanner.param_types.DATE,
                "insurance_id": spanner.param_types.STRING,
                "limit": spanner.param_types.INT64
            }

            candidates = []
            with database.snapshot() as snapshot:
                results = snapshot.execute_sql(sql, params=params, param_types=param_types)
                for row in results:
                    pid, name, dob, ins, zip_code, gender, dot_product, name_like, dob_match, ins_match = row
                    
                    dot_product = dot_product if dot_product is not None else 0.0
                    match_score = int((dot_product * 0.60 + name_like * 0.15 + dob_match * 0.15 + ins_match * 0.10) * 100)
                    match_score = max(0, min(100, match_score))

                    candidates.append({
                        "id": str(pid),
                        "name": name,
                        "dob": str(dob),
                        "insurance_id": ins,
                        "zip_code": zip_code,
                        "gender": gender,
                        "match_score": match_score,
                        "details": {
                            "name_embedding_similarity": int(dot_product * 100),
                            "name_fuzzy_match": int(name_like * 100),
                            "dob_match": dob_match > 0.9,
                            "insurance_id_match": ins_match > 0.9
                        }
                    })
            return candidates
        except Exception as e:
            logger.error(f"Error querying Spanner: {e}", exc_info=True)
            return []

    @staticmethod
    def _get_seed_vector_for_name(name: str) -> List[float]:
        """Returns a deterministic 768-dimension vector based on name for presets matching."""
        # Use simple hash seed for name to generate deterministic pseudo-random floats
        # so name searches generate matching vector alignments
        h = hash(name.lower())
        random.seed(abs(h))
        vec = [random.uniform(-1.0, 1.0) for _ in range(768)]
        norm = sum(x*x for x in vec) ** 0.5
        return [x / norm for x in vec]

    @staticmethod
    def dispense_prescription(db_type: str, preset_id: str) -> str:
        """Inserts a prescription record into the selected database and returns a success message."""
        from backend.mock_presets import PRESETS
        if preset_id not in PRESETS:
            raise ValueError("Preset not found")
            
        preset = PRESETS[preset_id]
        fields = preset["extracted_fields"]
        
        patient_name = fields["patient_name"]
        npi = fields["npi"]
        drug_name = fields["drug_name"]
        strength = fields["strength"]
        
        # Parse qty and days_supply from fields["qty_days"] e.g. "30 / 90d" -> qty=30, days_supply=90
        qty = 30
        days_supply = 90
        try:
            parts = fields["qty_days"].split("/")
            qty = int(parts[0].strip())
            days_supply = int(parts[1].replace("d", "").strip())
        except Exception:
            pass
            
        try:
            refills = int(fields["refills"])
        except Exception:
            refills = 0
            
        db_type = db_type.lower()
        logger.info(f"Dispensing prescription for '{patient_name}' (preset_id='{preset_id}') on database: {db_type}")
        
        if db_type == "mock":
            return "Prescription successfully dispensed and recorded in Mock (In-Memory) database."
        elif db_type == "cloudsql":
            return DatabaseClient._dispense_cloudsql(patient_name, npi, drug_name, strength, qty, days_supply, refills)
        elif db_type == "alloydb":
            return DatabaseClient._dispense_alloydb(patient_name, npi, drug_name, strength, qty, days_supply, refills)
        elif db_type == "spanner":
            return DatabaseClient._dispense_spanner(patient_name, npi, drug_name, strength, qty, days_supply, refills)
        else:
            raise ValueError(f"Unsupported database type: {db_type}")

    @staticmethod
    def _dispense_cloudsql(patient_name: str, npi: str, drug_name: str, strength: str, qty: int, days_supply: int, refills: int) -> str:
        db_config = CONFIG.get("databases", {}).get("cloudsql", {})
        database = db_config.get("database_name", "cloudsql-demo-db")
        user = db_config.get("user", "demo-user")
        password = db_config.get("password", "Password123!")
        
        is_cloud_run = os.environ.get("K_SERVICE") is not None
        instance_connection_name = db_config.get("instance_connection_name", "my-host-prj-472917:us-west4:cloudsql-demo")
        
        conn = None
        try:
            if is_cloud_run:
                unix_sock = f"/cloudsql/{instance_connection_name}/.s.PGSQL.5432"
                conn = pg8000.dbapi.connect(unix_sock=unix_sock, database=database, user=user, password=password)
            else:
                conn = pg8000.dbapi.connect(host=db_config.get("host", "127.0.0.1"), port=int(db_config.get("port", 5432)), database=database, user=user, password=password)
                
            cursor = conn.cursor()
            
            # Find patient_id
            cursor.execute("SELECT id FROM patients WHERE name = %s LIMIT 1;", (patient_name,))
            patient_row = cursor.fetchone()
            if not patient_row:
                return f"Error: Patient '{patient_name}' not found in Cloud SQL database."
            patient_id = patient_row[0]
            
            # Ensure prescriber exists
            cursor.execute("SELECT npi FROM prescribers WHERE npi = %s LIMIT 1;", (npi,))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO prescribers (npi, name) VALUES (%s, %s);", (npi, "Demo Prescriber"))
                
            # Insert prescription
            cursor.execute("""
                INSERT INTO prescriptions (patient_id, npi, drug_name, strength, qty, days_supply, refills)
                VALUES (%s, %s, %s, %s, %s, %s, %s);
            """, (patient_id, npi, drug_name, strength, qty, days_supply, refills))
            
            conn.commit()
            return "Prescription successfully dispensed and recorded in Cloud SQL."
        except Exception as e:
            logger.error(f"Cloud SQL dispense failed: {e}", exc_info=True)
            return f"Error: Failed to record in Cloud SQL ({e})"
        finally:
            if conn:
                conn.close()

    @staticmethod
    def _dispense_alloydb(patient_name: str, npi: str, drug_name: str, strength: str, qty: int, days_supply: int, refills: int) -> str:
        db_config = CONFIG.get("databases", {}).get("alloydb", {})
        project_id = CONFIG.get("gcp", {}).get("project_id", "my-host-prj-472917")
        region = CONFIG.get("gcp", {}).get("region", "us-west4")
        cluster_id = db_config.get("cluster_id", "alloydb-demo-cluster")
        instance_id = db_config.get("instance_id", "alloydb-inst")
        database = db_config.get("database_name", "alloydb-demo-db")
        user = db_config.get("user", "demo-user")
        password = db_config.get("password", "Password123!")
        
        from google.cloud.alloydb.connector import Connector
        connector = Connector()
        instance_connection_path = f"projects/{project_id}/locations/{region}/clusters/{cluster_id}/instances/{instance_id}"
        
        try:
            conn = connector.connect(
                instance_connection_path,
                "pg8000",
                user=user,
                password=password,
                db=database,
                enable_iam_auth=False,
                ip_type="public"
            )
            cursor = conn.cursor()
            
            # Find patient_id
            cursor.execute("SELECT id FROM patients WHERE name = %s LIMIT 1;", (patient_name,))
            patient_row = cursor.fetchone()
            if not patient_row:
                return f"Error: Patient '{patient_name}' not found in AlloyDB database."
            patient_id = patient_row[0]
            
            # Ensure prescriber exists
            cursor.execute("SELECT npi FROM prescribers WHERE npi = %s LIMIT 1;", (npi,))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO prescribers (npi, name) VALUES (%s, %s);", (npi, "Demo Prescriber"))
                
            # Insert prescription
            cursor.execute("""
                INSERT INTO prescriptions (patient_id, npi, drug_name, strength, qty, days_supply, refills)
                VALUES (%s, %s, %s, %s, %s, %s, %s);
            """, (patient_id, npi, drug_name, strength, qty, days_supply, refills))
            
            conn.commit()
            return "Prescription successfully dispensed and recorded in AlloyDB."
        except Exception as e:
            logger.error(f"AlloyDB dispense failed: {e}", exc_info=True)
            return f"Error: Failed to record in AlloyDB ({e})"
        finally:
            connector.close()

    @staticmethod
    def _dispense_spanner(patient_name: str, npi: str, drug_name: str, strength: str, qty: int, days_supply: int, refills: int) -> str:
        db_config = CONFIG.get("databases", {}).get("spanner", {})
        project_id = CONFIG.get("gcp", {}).get("project_id")
        instance_id = db_config.get("instance_id", "spanner-demo-inst")
        database_id = db_config.get("database_id", "spanner-demo-db")
        
        from google.cloud import spanner
        client = spanner.Client(project=project_id)
        instance = client.instance(instance_id)
        database = instance.database(database_id)
        
        def insert_tx(transaction):
            # Find patient ID
            results = transaction.execute_sql(
                "SELECT id FROM patients WHERE name = @name LIMIT 1",
                params={"name": patient_name},
                param_types={"name": spanner.param_types.STRING}
            )
            rows = list(results)
            if not rows:
                raise ValueError(f"Patient '{patient_name}' not found in Spanner database.")
            patient_id = rows[0][0]
            
            # Ensure prescriber exists
            res_pres = transaction.execute_sql(
                "SELECT npi FROM prescribers WHERE npi = @npi LIMIT 1",
                params={"npi": npi},
                param_types={"npi": spanner.param_types.STRING}
            )
            if not list(res_pres):
                transaction.execute_update(
                    "INSERT INTO prescribers (npi, name) VALUES (@npi, @name)",
                    params={"npi": npi, "name": "Demo Prescriber"},
                    param_types={"npi": npi, "name": spanner.param_types.STRING}
                )
                
            # Get next prescription ID
            res_max = transaction.execute_sql("SELECT COALESCE(MAX(id), 0) + 1 FROM prescriptions")
            next_id = list(res_max)[0][0]
            
            # Insert prescription
            transaction.execute_update(
                """
                INSERT INTO prescriptions (id, patient_id, npi, drug_name, strength, qty, days_supply, refills, ingested_at)
                VALUES (@id, @patient_id, @npi, @drug_name, @strength, @qty, @days_supply, @refills, CURRENT_TIMESTAMP())
                """,
                params={
                    "id": next_id,
                    "patient_id": patient_id,
                    "npi": npi,
                    "drug_name": drug_name,
                    "strength": strength,
                    "qty": qty,
                    "days_supply": days_supply,
                    "refills": refills
                },
                param_types={
                    "id": spanner.param_types.INT64,
                    "patient_id": spanner.param_types.INT64,
                    "npi": spanner.param_types.STRING,
                    "drug_name": spanner.param_types.STRING,
                    "strength": spanner.param_types.STRING,
                    "qty": spanner.param_types.INT64,
                    "days_supply": spanner.param_types.INT64,
                    "refills": spanner.param_types.INT64
                }
            )
            
        try:
            database.run_in_transaction(insert_tx)
            return "Prescription successfully dispensed and recorded in Spanner."
        except Exception as e:
            logger.error(f"Spanner dispense failed: {e}")
            return f"Error: Failed to record in Spanner ({e})"

