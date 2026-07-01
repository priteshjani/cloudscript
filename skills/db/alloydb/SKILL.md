---
name: alloydb-operations
description: Run transactional SQL statements, use pgvector extension, execute AlloyDB AI search capabilities, and optimize Columnar Engine in Google Cloud AlloyDB clusters.
---
# AlloyDB Operations Skill

This skill allows the agent to execute queries, utilize the `pgvector` extension, leverage AlloyDB AI embeddings, and optimize HTAP queries using the AlloyDB Columnar Engine.

## Advanced Features & Technical Guidance

### 1. pgvector Extension & Vector Indexing
- **Concept**: AlloyDB supports standard `pgvector` features to store, index, and query embeddings. Supported index types are IVFFlat and HNSW.
- **Index Definition**: Prefer HNSW indexes for better search accuracy at scale:
  ```sql
  CREATE INDEX my_hnsw_idx ON items USING hnsw (embedding_col vector_cosine_ops);
  ```
- **Similarity Queries**: Use the cosine distance operator `<=>` (or `<->` for L2 distance) to retrieve similar rows:
  ```sql
  SELECT id, embedding_col <=> @queryEmbedding AS distance
  FROM items
  ORDER BY distance ASC
  LIMIT 5;
  ```

### 2. AlloyDB AI (Model Integration & Embedding Generation)
- **Concept**: AlloyDB integrates with Vertex AI. Using the `google_ml` extension, you can generate embeddings directly inside SQL queries using pre-registered models.
- **Query Example**:
  ```sql
  SELECT id, description, google_ml.create_embeddings('textembedding-gecko@003', description) AS embedding
  FROM products
  ```

### 3. AlloyDB Columnar Engine
- **Concept**: AlloyDB features an in-memory Columnar Engine to speed up analytical (OLAP) queries alongside transactional (OLTP) workloads on the same instance.
- **Optimization**: Ensure the engine is populated for tables/columns that are heavily queried for reports. You can force queries to run against the columnar engine, or tune the columnar threshold:
  ```sql
  -- Force populate table into Columnar Engine
  SELECT alloydb_columnar_engine.populate_relation('items');
  ```
