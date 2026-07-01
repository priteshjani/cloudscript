import json
import random
import logging
from typing import Dict, Any, List
from google.cloud.alloydb.connector import Connector
import pg8000

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AlloyDBDeployer:
    """
    Deploys DDL schema and generates dummy data for AlloyDB instance.
    Uses google-cloud-alloydb-connector with pg8000.
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
        self.password = db_config.get("password", "Password123!") # Default password

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {}

    def get_connection(self):
        """Establishes connection to AlloyDB using google-cloud-alloydb-connector."""
        connector = Connector()
        # Connection path format: projects/PROJECT/locations/REGION/clusters/CLUSTER/instances/INSTANCE
        instance_connection_path = f"projects/{self.project_id}/locations/{self.region}/clusters/{self.cluster_id}/instances/{self.instance_id}"
        logger.info(f"Connecting to AlloyDB instance '{instance_connection_path}' as admin user 'postgres'...")
        conn = connector.connect(
            instance_connection_path,
            "pg8000",
            user="postgres",
            password=self.password,
            db=self.database_name,
            enable_iam_auth=False,
            ip_type="public"
        )
        return conn

    def deploy_schema(self, conn) -> None:
        """Executes DDL statements to set up extensions and tables on AlloyDB."""
        cursor = conn.cursor()
        
        logger.info("Enabling pgvector and pg_trgm extensions on AlloyDB...")
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        cursor.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
        
        logger.info("Dropping existing tables if any...")
        cursor.execute("DROP TABLE IF EXISTS past_fills CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS prescriptions CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS prescribers CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS patients CASCADE;")

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
        
        logger.info("Creating indexes on 'patients'...")
        cursor.execute("CREATE INDEX ON patients USING hnsw (name_embedding vector_cosine_ops);")
        cursor.execute("CREATE INDEX ON patients USING gin (name gin_trgm_ops);")

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

        logger.info("Creating table 'past_fills'...")
        cursor.execute("""
            CREATE TABLE past_fills (
                id SERIAL PRIMARY KEY,
                patient_id INT REFERENCES patients(id),
                drug_name VARCHAR(100) NOT NULL,
                fill_date DATE NOT NULL
            );
        """)

        logger.info("Granting app user permissions...")
        cursor.execute(f'GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO "{self.user}";')
        cursor.execute(f'GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO "{self.user}";')
        
        conn.commit()
        logger.info("AlloyDB DDL Schema successfully deployed.")

    def generate_vector(self) -> List[float]:
        vec = [random.uniform(-1.0, 1.0) for _ in range(768)]
        norm = sum(x*x for x in vec) ** 0.5
        return [x / norm for x in vec]

    def seed_demo_presets(self, conn) -> List[int]:
        cursor = conn.cursor()
        patient_ids = []

        logger.info("Seeding demo patient presets on AlloyDB...")
        presets = [
            ("Dorothy Thompson", "1942-02-14", "INS-100019", "77002", "Female"),
            ("Robert Smith", "1980-11-30", "INS-900223", "90210", "Male"),
            ("Elizabeth Jones", "1972-08-14", "INS-772091", "60611", "Female"),
            ("Maria Garcia", "1990-05-12", "INS-909012", "77019", "Female"),
            ("Maria Garcia", "1988-09-04", "INS-304011", "77019", "Female"),
        ]
        
        for name, dob, ins, zip_code, gender in presets:
            embedding = self.generate_vector()
            emb_str = "[" + ",".join(map(str, embedding)) + "]"
            cursor.execute("""
                INSERT INTO patients (name, dob, insurance_id, zip_code, gender, name_embedding)
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;
            """, (name, dob, ins, zip_code, gender, emb_str))
            pid = cursor.fetchone()[0]
            patient_ids.append(pid)

        logger.info("Seeding demo prescriber presets on AlloyDB...")
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
        cursor = conn.cursor()
        
        first_names = ["John", "Mary", "David", "Linda", "James", "Patricia", "Robert", "Jennifer", "Michael", "Elizabeth"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
        genders = ["Male", "Female"]
        drugs = ["Lisinopril", "Metformin", "Atorvastatin", "Levothyroxine", "Amoxicillin", "Gabapentin", "Omeprazole"]

        logger.info(f"Generating {num_records} additional dummy patient records for AlloyDB...")
        
        for i in range(num_records):
            name = f"{random.choice(first_names)} {random.choice(last_names)}"
            year = random.randint(1940, 2000)
            month = random.randint(1, 12)
            day = random.randint(1, 28)
            dob = f"{year:04d}-{month:02d}-{day:02d}"
            
            ins = f"INS-{random.randint(100000, 999999)}"
            zip_code = f"{random.randint(10000, 99999):05d}"
            gender = random.choice(genders)
            embedding = self.generate_vector()
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
        logger.info(f"Successfully loaded dummy data to AlloyDB.")

    def create_database_if_not_exists(self) -> None:
        """Connects to default 'postgres' database and creates the target database if missing."""
        connector = Connector()
        instance_connection_path = f"projects/{self.project_id}/locations/{self.region}/clusters/{self.cluster_id}/instances/{self.instance_id}"
        logger.info(f"Connecting to default database 'postgres' to check database '{self.database_name}' presence...")
        
        conn = connector.connect(
            instance_connection_path,
            "pg8000",
            user="postgres",
            password=self.password,
            db="postgres",
            enable_iam_auth=False,
            ip_type="public"
        )
        # Set autocommit to True to run CREATE DATABASE and CREATE ROLE statements
        conn.autocommit = True
        cursor = conn.cursor()
        
        try:
            # 1. Create target database if it doesn't exist
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (self.database_name,))
            exists = cursor.fetchone()
            if not exists:
                logger.info(f"Database '{self.database_name}' not found. Creating...")
                cursor.execute(f'CREATE DATABASE "{self.database_name}"')
                logger.info(f"Database '{self.database_name}' successfully created.")
            else:
                logger.info(f"Database '{self.database_name}' already exists.")

            # 2. Create demo-user role if it doesn't exist
            cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (self.user,))
            user_exists = cursor.fetchone()
            if not user_exists:
                logger.info(f"Role '{self.user}' not found. Creating...")
                cursor.execute(f'CREATE ROLE "{self.user}" WITH LOGIN PASSWORD \'{self.password}\'')
                logger.info(f"Role '{self.user}' successfully created.")
            else:
                logger.info(f"Role '{self.user}' already exists.")

            # 3. Grant privileges
            cursor.execute(f'GRANT "{self.user}" TO "postgres"')
            cursor.execute(f'ALTER DATABASE "{self.database_name}" OWNER TO "{self.user}"')
            logger.info(f"Assigned owner of '{self.database_name}' to '{self.user}'")
            
        except Exception as e:
            logger.error(f"Error during database initialization: {e}")
        finally:
            conn.close()

if __name__ == "__main__":
    import sys
    num_records = 100
    if len(sys.argv) > 1:
        try:
            num_records = int(sys.argv[1])
        except ValueError:
            pass
            
    deployer = AlloyDBDeployer()
    try:
        logger.info("Initializing AlloyDB database presence...")
        deployer.create_database_if_not_exists()
        logger.info("Connecting to target AlloyDB database...")
        conn = deployer.get_connection()
        deployer.deploy_schema(conn)
        demo_pids = deployer.seed_demo_presets(conn)
        deployer.generate_dummy_data(conn, num_records, demo_pids)
        conn.close()
        logger.info("AlloyDB deployment and seeding completed successfully!")
    except Exception as e:
        logger.error(f"Error deploying AlloyDB: {e}", exc_info=True)
