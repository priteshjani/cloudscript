---
name: cloudsql-database-deployment
description: Deploy schemas, enable pgvector and pg_trgm extensions, and generate mock data for Cloud SQL PostgreSQL instances. Use when initializing the demo database.
---
# Cloud SQL Database Deployment Skill

This skill assists in executing DDL scripts, establishing PostgreSQL extensions, and generating dummy data for the pharmacy intelligence queue.

## When to use this skill
- Use to initialize the Cloud SQL database for the first time.
- Use to load dummy patient candidates, prescribers, and prescription history profiles into the tables.

## How to use it
- **DDL Execution Order**:
  1. Enable extensions: `CREATE EXTENSION IF NOT EXISTS vector;` and `CREATE EXTENSION IF NOT EXISTS pg_trgm;`.
  2. Create base tables: `patients`, `prescribers`.
  3. Create dependent tables: `prescriptions`, `past_fills`.
  4. Create indices: `CREATE INDEX ON patients USING hnsw (name_embedding vector_cosine_ops);` and `CREATE INDEX ON patients USING gin (name gin_trgm_ops);`.

- **Mock Data Generation**:
  - Accept a parameter `num_records` specifying how many patient records to generate.
  - Generate realistic names, insurance IDs, and zip codes.
  - For `name_embedding`, generate 768-dimension vectors (e.g. using random floats scaled between -1.0 and 1.0, or query Vertex AI if configured).
