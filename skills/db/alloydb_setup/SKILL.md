---
name: alloydb-database-deployment
description: Deploy DDL schemas, enable pgvector and pg_trgm extensions, and seed mock data for AlloyDB clusters. Use when initializing the demo database.
---
# AlloyDB Database Deployment Skill

This skill assists in executing DDL scripts, establishing PostgreSQL-compatible extensions, and generating vector embeddings and dummy records for the pharmacy intelligence queue on AlloyDB.

## DDL execution order
1. Enable extensions: `CREATE EXTENSION IF NOT EXISTS vector;` and `CREATE EXTENSION IF NOT EXISTS pg_trgm;`.
2. Create base tables: `patients`, `prescribers`.
3. Create dependent tables: `prescriptions`, `past_fills`.
4. Create HNSW and Trigram indexes for Vector/String matching.

## Execution
Run the setup script with Python 3.9 virtual environment:
```bash
.venv/bin/python skills/db/alloydb_setup/setup_alloydb.py [NUM_RECORDS]
```
