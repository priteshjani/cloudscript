import json
import random
import logging
import datetime
from typing import Dict, Any, List
from google.cloud import spanner

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SpannerDeployer:
    """
    Deploys Google Standard SQL schema and generates dummy data for
    Google Cloud Spanner instances.
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
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {}

    def deploy_schema(self) -> None:
        """Creates tables on Spanner database."""
        client = spanner.Client(project=self.project_id)
        instance = client.instance(self.instance_id)
        database = instance.database(self.database_id)

        ddl_statements = [
            # Drop tables if they exist
            "DROP TABLE IF EXISTS past_fills",
            "DROP TABLE IF EXISTS prescriptions",
            "DROP TABLE IF EXISTS prescribers",
            "DROP TABLE IF EXISTS patients",
            
            # Create patients
            """
            CREATE TABLE patients (
                id INT64 NOT NULL,
                name STRING(100) NOT NULL,
                dob DATE NOT NULL,
                insurance_id STRING(50),
                zip_code STRING(10),
                gender STRING(10),
                name_embedding ARRAY<FLOAT64>
            ) PRIMARY KEY (id)
            """,
            
            # Create prescribers
            """
            CREATE TABLE prescribers (
                npi STRING(20) NOT NULL,
                name STRING(100) NOT NULL,
                dea STRING(20),
                specialty STRING(100),
                address STRING(255)
            ) PRIMARY KEY (npi)
            """,
            
            # Create prescriptions
            """
            CREATE TABLE prescriptions (
                id INT64 NOT NULL,
                patient_id INT64,
                npi STRING(20),
                drug_name STRING(100) NOT NULL,
                strength STRING(20),
                qty INT64,
                days_supply INT64,
                refills INT64,
                ingested_at TIMESTAMP
            ) PRIMARY KEY (id)
            """,
            
            # Create past_fills
            """
            CREATE TABLE past_fills (
                id INT64 NOT NULL,
                patient_id INT64,
                drug_name STRING(100) NOT NULL,
                fill_date DATE NOT NULL
            ) PRIMARY KEY (id)
            """
        ]

        logger.info(f"Deploying Google Standard SQL DDL to Spanner database '{self.database_id}'...")
        # Since Spanner doesn't support DROP TABLE and CREATE TABLE in a single transactional batch easily
        # if dependent, we should execute them sequentially or handle exceptions.
        # But DDL update_schema handles an array of DDLs. Let's do it via update_ddl.
        try:
            operation = database.update_ddl(ddl_statements)
            logger.info("Waiting for DDL schema update to complete...")
            operation.result(timeout=240)
            logger.info("Spanner schema successfully deployed.")
        except Exception as e:
            logger.error(f"Error executing DDL on Spanner: {e}")
            raise e

    def generate_vector(self, name: str = None) -> List[float]:
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

    def seed_data(self, num_records: int) -> None:
        """Seeds Spanner using Mutations for high performance."""
        client = spanner.Client(project=self.project_id)
        instance = client.instance(self.instance_id)
        database = instance.database(self.database_id)

        # 1. Seed patients presets
        presets = [
            (1001, "Dorothy Thompson", "1942-02-14", "INS-100019", "77002", "Female"),
            (1002, "Robert Smith", "1980-11-30", "INS-900223", "90210", "Male"),
            (1003, "Elizabeth Jones", "1972-08-14", "INS-772091", "60611", "Female"),
            (1004, "Maria Garcia", "1990-05-12", "INS-909012", "77019", "Female"),
            (1005, "Maria Garcia", "1988-09-04", "INS-304011", "77019", "Female"),
        ]

        logger.info("Seeding patient presets to Spanner...")
        patient_data = []
        for pid, name, dob_str, ins, zip_code, gender in presets:
            embedding = self.generate_vector(name)
            patient_data.append((pid, name, dob_str, ins, zip_code, gender, embedding))

        # 2. Seed prescribers
        prescribers = [
            ("1234567890", "Dr. James Wilson", "JW1234567", "Internal Medicine", "1200 Main St. Houston, TX 77002"),
            ("9876543210", "Dr. Sarah Jenkins", "SJ9876543", "Endocrinology", "100 Beverly Hills, CA 90210"),
            ("1122334455", "Dr. Alan Mercer", "AM1122334", "Cardiology", "500 Michigan Ave, Chicago, IL 60611"),
            ("4455667788", "Dr. Carla Rossi", "CR4455667", "General Practice", "789 Westheimer Rd, Houston, TX 77019"),
        ]

        # 3. Generate dummy records
        first_names = ["John", "Mary", "David", "Linda", "James", "Patricia", "Robert", "Jennifer", "Michael", "Elizabeth"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
        genders = ["Male", "Female"]
        drugs = ["Lisinopril", "Metformin", "Atorvastatin", "Levothyroxine", "Amoxicillin", "Gabapentin", "Omeprazole"]

        logger.info(f"Generating {num_records} additional dummy patient records for Spanner...")
        past_fills_data = []
        past_fill_id = 1

        for i in range(num_records):
            pid = 2000 + i
            name = f"{random.choice(first_names)} {random.choice(last_names)}"
            year = random.randint(1940, 2000)
            month = random.randint(1, 12)
            day = random.randint(1, 28)
            dob_str = f"{year:04d}-{month:02d}-{day:02d}"
            ins = f"INS-{random.randint(100000, 999999)}"
            zip_code = f"{random.randint(10000, 99999):05d}"
            gender = random.choice(genders)
            embedding = self.generate_vector(name)
            
            patient_data.append((pid, name, dob_str, ins, zip_code, gender, embedding))

            # Add past fills
            if random.random() > 0.4:
                num_fills = random.randint(1, 4)
                for _ in range(num_fills):
                    fill_date_str = f"2026-{random.randint(1, 6):02d}-{random.randint(1, 28):02d}"
                    past_fills_data.append((past_fill_id, pid, random.choice(drugs), fill_date_str))
                    past_fill_id += 1

        # Perform mutations insert
        def insert_all(transaction):
            # Patients
            transaction.insert(
                "patients",
                columns=["id", "name", "dob", "insurance_id", "zip_code", "gender", "name_embedding"],
                values=[
                    [pid, name, datetime.date.fromisoformat(dob), ins, zip_code, gender, emb]
                    for pid, name, dob, ins, zip_code, gender, emb in patient_data
                ]
            )
            # Prescribers
            transaction.insert(
                "prescribers",
                columns=["npi", "name", "dea", "specialty", "address"],
                values=prescribers
            )
            # Past Fills
            if past_fills_data:
                transaction.insert(
                    "past_fills",
                    columns=["id", "patient_id", "drug_name", "fill_date"],
                    values=[
                        [fid, pid, drug, datetime.date.fromisoformat(fdate)]
                        for fid, pid, drug, fdate in past_fills_data
                    ]
                )

        logger.info("Applying Spanner transaction mutations...")
        database.run_in_transaction(insert_all)
        logger.info("Spanner data seeding completed successfully.")

if __name__ == "__main__":
    import sys
    num_records = 100
    if len(sys.argv) > 1:
        try:
            num_records = int(sys.argv[1])
        except ValueError:
            pass
            
    deployer = SpannerDeployer()
    try:
        deployer.deploy_schema()
        deployer.seed_data(num_records)
        logger.info("Spanner setup task finished successfully!")
    except Exception as e:
        logger.error(f"Error deploying Spanner: {e}", exc_info=True)
