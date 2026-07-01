terraform {
  required_version = ">= 1.3.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

# 1. Enable Required Google Cloud APIs
locals {
  apis = [
    "aiplatform.googleapis.com",      # Vertex AI API
    "artifactregistry.googleapis.com",# Artifact Registry API
    "cloudbuild.googleapis.com",      # Cloud Build API
    "run.googleapis.com",             # Cloud Run API
    "sqladmin.googleapis.com",         # Cloud SQL Admin API
    "spanner.googleapis.com",          # Cloud Spanner API
    "alloydb.googleapis.com",          # AlloyDB API
    "compute.googleapis.com"          # Compute Engine API (VPC Peering)
  ]
}

resource "google_project_service" "services" {
  for_each           = toset(local.apis)
  service            = each.key
  disable_on_destroy = false
}

# 2. Artifact Registry for Container Image
resource "google_artifact_registry_repository" "cloudscript_repo" {
  depends_on    = [google_project_service.services]
  location      = var.region
  repository_id = "cloudscript-repo"
  description   = "Docker registry for CloudScript containers"
  format        = "DOCKER"
}

# 3. Cloud Spanner Instance and Database
resource "google_spanner_instance" "spanner_inst" {
  depends_on   = [google_project_service.services]
  config       = "regional-${var.region}"
  display_name = "Spanner Demo Instance"
  name         = "spanner-demo-inst"
  num_nodes    = 1
}

resource "google_spanner_database" "spanner_db" {
  instance = google_spanner_instance.spanner_inst.name
  name     = "spanner-demo-db"
  
  # Schema definition matches spanner_setup script
  ddl = [
    "CREATE TABLE patients (id INT64, name STRING(100), dob DATE, insurance_id STRING(50), zip_code STRING(10), gender STRING(10), name_embedding ARRAY<FLOAT64>) PRIMARY KEY(id)",
    "CREATE INDEX patients_trgm_idx ON patients(name)",
    "CREATE TABLE prescribers (npi STRING(20) NOT NULL, name STRING(100) NOT NULL, dea STRING(20), specialty STRING(100), address STRING(255)) PRIMARY KEY(npi)",
    "CREATE TABLE prescriptions (id INT64 NOT NULL, patient_id INT64, npi STRING(20), drug_name STRING(100) NOT NULL, strength STRING(20), qty INT64, days_supply INT64, refills INT64, ingested_at TIMESTAMP) PRIMARY KEY(id)",
    "CREATE TABLE past_fills (id INT64 NOT NULL, patient_id INT64, drug_name STRING(100) NOT NULL, fill_date DATE NOT NULL) PRIMARY KEY(id)"
  ]
  deletion_protection = false
}

# 4. Cloud SQL PostgreSQL Instance and Database
resource "google_sql_database_instance" "cloudsql_inst" {
  depends_on       = [google_project_service.services]
  name             = "cloudsql-demo"
  database_version = "POSTGRES_15" # Compatible with standard pgvector extensions
  region           = var.region

  settings {
    tier = "db-f1-micro" # Small/cheap instance for demo/testing
    ip_configuration {
      ipv4_enabled = true # Enabled public IP for seeding/testing
    }
    database_flags {
      name  = "cloudsql.enable_pgaudit"
      value = "on"
    }
  }
  deletion_protection = false
}

resource "google_sql_database" "cloudsql_db" {
  name     = "cloudsql-demo-db"
  instance = google_sql_database_instance.cloudsql_inst.name
}

resource "google_sql_user" "cloudsql_user" {
  name     = "demo-user"
  instance = google_sql_database_instance.cloudsql_inst.name
  password = var.db_password
}

# 5. AlloyDB Cluster and Instance
resource "google_alloydb_cluster" "alloydb_cluster" {
  depends_on = [google_project_service.services]
  cluster_id = "alloydb-demo-cluster"
  location   = var.region

  initial_user {
    password = var.db_password
  }
}

resource "google_alloydb_instance" "alloydb_inst" {
  cluster       = google_alloydb_cluster.alloydb_cluster.name
  instance_id   = "alloydb-inst"
  instance_type = "PRIMARY"

  machine_config {
    cpu_count = 2 # Smallest supported tier
  }
}
