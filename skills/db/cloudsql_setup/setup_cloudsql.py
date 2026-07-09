import json
import random
import logging
from typing import Dict, Any, List
import pg8000
from google.cloud.sql.connector import Connector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CloudSQLDeployer:
    """
    Deploys DDL schema, enables pgvector/pg_trgm extensions, and generates dummy
    data for Cloud SQL PostgreSQL instance using standard pg8000 client connection.
    """
    def __init__(self, config_path: str = "config.json"):
        self.config = self._load_config(config_path)
        db_config = self.config.get("databases", {}).get("cloudsql", {})
        self.project_id = self.config.get("gcp", {}).get("project_id")
        self.region = self.config.get("gcp", {}).get("region")
        
        import sys
        self.instance_connection_name = db_config.get("instance_connection_name")
        self.database_name = db_config.get("database_name")
        if len(sys.argv) > 2:
            self.database_name = sys.argv[2]
            logger.info(f"Overriding target database with: '{self.database_name}'")
        self.user = db_config.get("user")
        
        # Read host and port from config if present, otherwise default to localhost (for Cloud SQL Auth Proxy)
        self.host = db_config.get("host", "127.0.0.1")
        self.port = int(db_config.get("port", 5432))
        self.password = db_config.get("password", None)

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {}

    def get_connection(self):
        """Establishes connection to Cloud SQL PostgreSQL using google-cloud-sql-connector."""
        logger.info(f"Connecting to database {self.database_name} via Cloud SQL Connector: {self.instance_connection_name} as user '{self.user}'...")
        connector = Connector()
        conn = connector.connect(
            self.instance_connection_name,
            "pg8000",
            user=self.user,
            password=self.password,
            db=self.database_name
        )
        return conn

    def deploy_schema(self, conn) -> None:
        """Executes DDL statements to set up extensions and tables."""
        cursor = conn.cursor()
        
        # 1. Enable extensions
        logger.info("Enabling pgvector and pg_trgm extensions...")
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        cursor.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
        
        # 2. Drop tables if exist (safe for demo environment)
        logger.info("Dropping existing tables if any...")
        cursor.execute("DROP TABLE IF EXISTS past_fills CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS prescriptions CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS prescribers CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS patients CASCADE;")

        # 3. Create patients table
        logger.info("Creating table 'patients'...")
        cursor.execute("""
            CREATE TABLE patients (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                dob DATE NOT NULL,
                insurance_id VARCHAR(50),
                zip_code VARCHAR(10),
                gender VARCHAR(10),
                name_embedding vector(768)
            );
        """)
        
        # 4. Create indexes
        logger.info("Creating indexes on 'patients'...")
        cursor.execute("CREATE INDEX ON patients USING hnsw (name_embedding vector_cosine_ops);")
        cursor.execute("CREATE INDEX ON patients USING gin (name gin_trgm_ops);")

        # 5. Create prescribers table
        logger.info("Creating table 'prescribers'...")
        cursor.execute("""
            CREATE TABLE prescribers (
                npi VARCHAR(20) PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                dea VARCHAR(20),
                specialty VARCHAR(100),
                address VARCHAR(255)
            );
        """)

        # 6. Create prescriptions table
        logger.info("Creating table 'prescriptions'...")
        cursor.execute("""
            CREATE TABLE prescriptions (
                id SERIAL PRIMARY KEY,
                patient_id INT REFERENCES patients(id),
                npi VARCHAR(20) REFERENCES prescribers(npi),
                drug_name VARCHAR(100) NOT NULL,
                strength VARCHAR(20),
                qty INT,
                days_supply INT,
                refills INT,
                ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 7. Create past_fills table
        logger.info("Creating table 'past_fills'...")
        cursor.execute("""
            CREATE TABLE past_fills (
                id SERIAL PRIMARY KEY,
                patient_id INT REFERENCES patients(id),
                drug_name VARCHAR(100) NOT NULL,
                fill_date DATE NOT NULL
            );
        """)

        conn.commit()
        logger.info("DDL Schema successfully deployed.")

    def generate_vector(self, name: str = None) -> List[float]:
        """Generates a mock 768-dimension vector normalized for cosine similarity."""
        if name:
            import hashlib
            h = int(hashlib.sha256(name.lower().encode('utf-8')).hexdigest()[:8], 16)
            random.seed(h)
        else:
            import time
            random.seed(time.time_ns())
        vec = [random.uniform(-1.0, 1.0) for _ in range(768)]
        norm = sum(x*x for x in vec) ** 0.5
        return [x / norm for x in vec]

    def seed_demo_presets(self, conn) -> List[int]:
        """Seeds the exact patient/presciber presets needed for the frontend demo scenarios."""
        cursor = conn.cursor()
        patient_ids = []

        logger.info("Seeding demo patient presets...")
        presets = [
            ("Dorothy Thompson", "1942-02-14", "INS-100019", "77002", "Female"),
            ("Robert Smith", "1980-11-30", "INS-900223", "90210", "Male"),
            ("Elizabeth Jones", "1972-08-14", "INS-772091", "60611", "Female"),
            ("Maria Garcia", "1990-05-12", "INS-909012", "77019", "Female"),
            ("Maria Garcia", "1988-09-04", "INS-304011", "77019", "Female"),
        ]
        
        for name, dob, ins, zip_code, gender in presets:
            embedding = self.generate_vector(name)
            emb_str = "[" + ",".join(map(str, embedding)) + "]"
            cursor.execute("""
                INSERT INTO patients (name, dob, insurance_id, zip_code, gender, name_embedding)
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;
            """, (name, dob, ins, zip_code, gender, emb_str))
            pid = cursor.fetchone()[0]
            patient_ids.append(pid)

        logger.info("Seeding demo prescriber presets...")
        prescribers = [
            ("1234567890", "Dr. James Wilson", "JW1234567", "Internal Medicine", "1200 Main St. Houston, TX 77002"),
            ("9876543210", "Dr. Sarah Jenkins", "SJ9876543", "Endocrinology", "100 Beverly Hills, CA 90210"),
            ("1122334455", "Dr. Alan Mercer", "AM1122334", "Cardiology", "500 Michigan Ave, Chicago, IL 60611"),
            ("4455667788", "Dr. Carla Rossi", "CR4455667", "General Practice", "789 Westheimer Rd, Houston, TX 77019"),
        ]
        for npi, name, dea, spec, addr in prescribers:
            cursor.execute("""
                INSERT INTO prescribers (npi, name, dea, specialty, address)
                VALUES (%s, %s, %s, %s, %s) ON CONFLICT (npi) DO NOTHING;
            """, (npi, name, dea, spec, addr))

        conn.commit()
        return patient_ids

    def generate_dummy_data(self, conn, num_records: int, demo_patient_ids: List[int]) -> None:
        """Generates random patient records to populate the database for scale testing."""
        cursor = conn.cursor()
        
        first_names = ["John", "Mary", "David", "Linda", "James", "Patricia", "Robert", "Jennifer", "Michael", "Elizabeth"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
        genders = ["Male", "Female"]
        drugs = ["Lisinopril", "Metformin", "Atorvastatin", "Levothyroxine", "Amoxicillin", "Gabapentin", "Omeprazole"]

        logger.info(f"Generating {num_records} additional dummy patient records...")
        
        for i in range(num_records):
            name = f"{random.choice(first_names)} {random.choice(last_names)}"
            year = random.randint(1940, 2000)
            month = random.randint(1, 12)
            day = random.randint(1, 28)
            dob = f"{year:04d}-{month:02d}-{day:02d}"
            
            ins = f"INS-{random.randint(100000, 999999)}"
            zip_code = f"{random.randint(10000, 99999):05d}"
            gender = random.choice(genders)
            embedding = self.generate_vector(name)
            emb_str = "[" + ",".join(map(str, embedding)) + "]"
            
            cursor.execute("""
                INSERT INTO patients (name, dob, insurance_id, zip_code, gender, name_embedding)
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;
            """, (name, dob, ins, zip_code, gender, emb_str))
            
            pid = cursor.fetchone()[0]
            
            if random.random() > 0.4:
                num_fills = random.randint(1, 4)
                for _ in range(num_fills):
                    fill_date = f"2026-{random.randint(1, 6):02d}-{random.randint(1, 28):02d}"
                    cursor.execute("""
                        INSERT INTO past_fills (patient_id, drug_name, fill_date)
                        VALUES (%s, %s, %s);
                    """, (pid, random.choice(drugs), fill_date))
                    
        conn.commit()
        logger.info(f"Successfully generated and inserted dummy data.")

if __name__ == "__main__":
    import sys
    num_records = 100
    if len(sys.argv) > 1:
        try:
            num_records = int(sys.argv[1])
        except ValueError:
            pass
            
    deployer = CloudSQLDeployer()
    try:
        logger.info("Connecting to PostgreSQL database...")
        conn = deployer.get_connection()
        deployer.deploy_schema(conn)
        demo_pids = deployer.seed_demo_presets(conn)
        deployer.generate_dummy_data(conn, num_records, demo_pids)
        conn.close()
        logger.info("Database deployment and seeding completed successfully!")
    except Exception as e:
        logger.error(f"Error deploying database: {e}", exc_info=True)
