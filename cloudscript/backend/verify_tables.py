import os
import pg8000
from google.cloud.alloydb.connector import Connector

def verify_cloudsql():
    print("--- Verifying Cloud SQL (PostgreSQL 18) ---")
    try:
        # Since we are running locally, we need to connect via localhost:5432 (Cloud SQL Proxy must be running!)
        conn = pg8000.dbapi.connect(
            host="127.0.0.1",
            port=5432,
            database="cloudsql-demo-db",
            user="demo-user",
            password="Password123!"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
        tables = cursor.fetchall()
        print("Tables found:")
        for t in tables:
            print(f" - {t[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM patients;")
        count = cursor.fetchone()[0]
        print(f"Patients count: {count}")
        conn.close()
    except Exception as e:
        print(f"Cloud SQL verification failed: {e}")

def verify_alloydb():
    print("\n--- Verifying AlloyDB ---")
    try:
        connector = Connector()
        conn = connector.connect(
            "projects/my-host-prj-472917/locations/us-west4/clusters/alloydb-demo-cluster/instances/alloydb-inst",
            "pg8000",
            user="demo-user",
            password="Password123!",
            db="alloydb-demo-db",
            enable_iam_auth=False,
            ip_type="public"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
        tables = cursor.fetchall()
        print("Tables found:")
        for t in tables:
            print(f" - {t[0]}")
            
        cursor.execute("SELECT COUNT(*) FROM patients;")
        count = cursor.fetchone()[0]
        print(f"Patients count: {count}")
        conn.close()
    except Exception as e:
        print(f"AlloyDB verification failed: {e}")

if __name__ == "__main__":
    verify_cloudsql()
    verify_alloydb()
