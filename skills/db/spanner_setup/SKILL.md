---
name: spanner-database-deployment
description: Deploy DDL schemas and seed mock data for Google Cloud Spanner instances. Use when initializing the demo database.
---
# Spanner Database Deployment Skill

This skill assists in executing Google Standard SQL DDL scripts, establishing schemas, and seeding patient search tables and array embeddings on Spanner.

## DDL schema elements
1. Base tables: `patients`, `prescribers`.
2. Dependent tables: `prescriptions`, `past_fills`.
3. In Spanner, primary keys are declared directly in the tables (e.g. `PRIMARY KEY (id)`).

## Execution
Run the setup script with Python 3.9 virtual environment:
```bash
.venv/bin/python skills/db/spanner_setup/setup_spanner.py [NUM_RECORDS]
```
