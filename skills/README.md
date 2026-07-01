# Jetski Skills Framework: Deep Technical Guide

This directory contains the action blocks (skills) used by the Jetski agents to interact with GCP storage, cache, and database engines.

## Architectural Patterns

Each skill represents a single, focused logical tool. To make a skill reliable and safe:
1. **Connection Pooling**: Re-use connections and clients across invocations. Do not initialize client connections on every skill run.
2. **Authentication**: Enforce IAM-based database authentication using Application Default Credentials (ADC). Avoid embedding passwords or static tokens.
3. **Execution Context**: Skills must propagate tracing context (e.g. `traceparent` or custom trace IDs) to monitor multi-stage query latency.

---

## Database Connection & Client Guidelines

### 1. Relational Databases ([skills/db/](file:///Users/priteshjani/Documents/jetski/skills/db/))

#### A. Spanner ([spanner_skills.py](file:///Users/priteshjani/Documents/jetski/skills/skills/db/spanner_skills.py))
- **Client**: `google.cloud.spanner`
- **Transactions**: Enforce distinct read-only and read-write transaction pathways. Read-only transactions must use single-use or multi-use read-only contexts to prevent transaction locks:
  ```python
  with database.snapshot() as snapshot:
      results = snapshot.execute_sql(query, params=params, param_types=param_types)
  ```
- **Error Handling**: Handle transient errors (e.g., `Aborted` exceptions) by implementing automatic retry policies on read-write transactions.

#### B. AlloyDB ([alloydb_skills.py](file:///Users/priteshjani/Documents/jetski/skills/skills/db/alloydb_skills.py)) & CloudSQL ([cloudsql_skills.py](file:///Users/priteshjani/Documents/jetski/skills/skills/db/cloudsql_skills.py))
- **Connector**: `google.cloud.alloydb.connector.Connector` and `google.cloud.sql.connector.Connector`
- **Driver**: Use `pg8000` (Postgres) or `pymysql` (MySQL).
- **IAM Auth**: Enable IAM authentication to delegate credentials to the active service account:
  ```python
  connector.connect(
      instance_connection_string,
      "pg8000",
      user=iam_user_email,
      db=database_name,
      enable_iam_auth=True
  )
  ```
- **Pool Management**: Wrap connectors in a SQLAlchemy `QueuePool` to ensure connections are recycled and not leaked.

---

### 2. NoSQL & Caching ([skills/nosql/](file:///Users/priteshjani/Documents/jetski/skills/nosql/))

#### A. Bigtable ([bigtable_skills.py](file:///Users/priteshjani/Documents/jetski/skills/skills/nosql/bigtable_skills.py))
- **Client**: `google.cloud.bigtable`
- **Filter Optimization**: Enforce row filters (`RowFilterChain`) to retrieve only the necessary Column Families and Cells.
- **Scans**: Require a start and end row key for scans. Reject unbounded scans.

#### B. Firestore ([firestore_skills.py](file:///Users/priteshjani/Documents/jetski/skills/skills/nosql/firestore_skills.py))
- **Client**: `google.cloud.firestore`
- **Batching**: Use `WriteBatch` to group up to 500 document creations or updates into a single atomic transactional unit.
- **Transactions**: Use the `@firestore.transactional` decorator for atomic read-modify-write patterns.

#### C. Memorystore / Redis ([memorystore_skills.py](file:///Users/priteshjani/Documents/jetski/skills/skills/nosql/memorystore_skills.py))
- **Client**: `redis` (Python package)
- **Pipelines**: Group non-dependent operations in a pipeline (`redis.pipeline()`) to reduce network round-trip overhead.
- **Keyspaces**: Group cache keys using clear namespaces (e.g. `jetski:cache:{tenant_id}:{user_id}`).

---

### 3. Analytics ([skills/analytics/](file:///Users/priteshjani/Documents/jetski/skills/analytics/))

#### A. BigQuery ([bigquery_skills.py](file:///Users/priteshjani/Documents/jetski/skills/skills/analytics/bigquery_skills.py))
- **Cost Audits**: Run a dry run (`QueryJobConfig(dry_run=True)`) to inspect estimated bytes billed before running queries.
- **Partitions**: Ensure SQL queries contain filter statements on partitioned/clustered columns.

---

### 4. Data Governance & Discovery ([skills/catalog/](file:///Users/priteshjani/Documents/jetski/skills/catalog/))

#### A. Dataplex / Knowledge Catalog ([dataplex_skills.py](file:///Users/priteshjani/Documents/jetski/skills/catalog/dataplex/dataplex_skills.py))
- **Client**: `google.cloud.dataplex_v1` or `google.cloud.datacatalog_v1`
- **Search Scope**: Scope queries (e.g., `system=bigquery` or `type=table`) to filter results early.
- **Tag Validation**: Enforce validation parameters matching target tag templates before submitting attachments.
