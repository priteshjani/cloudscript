---
name: cloudsql-operations
description: Run transactional SQL statements, use pgvector extension, and execute full-text / trigram searches in Google Cloud SQL instances.
---
# Cloud SQL Operations Skill

This skill allows the agent to execute queries, utilize the `pgvector` extension for semantic search, and perform advanced full-text and fuzzy searches in PostgreSQL or MySQL.

## Advanced Features & Technical Guidance

### 1. pgvector Extension (Vector Search)
- **Concept**: Cloud SQL (specifically PostgreSQL) supports the `pgvector` extension to store and search vector embeddings.
- **Index Optimization**: For faster queries on large sets, use IVFFlat or HNSW indexes.
- **Distance Metrics**: Use `<=>` for cosine distance, or `<->` for Euclidean distance:
  ```sql
  SELECT id, description, embedding <=> @queryEmbedding AS distance
  FROM products
  ORDER BY distance ASC
  LIMIT 5;
  ```

### 2. Full-Text Search (FTS)
- **Concept**: PostgreSQL features native FTS using `tsvector` and `tsquery` to match search terms with lexemes.
- **Syntax Example**:
  ```sql
  SELECT id, title, ts_rank(text_search_vector, to_tsquery('english', @query)) AS rank
  FROM documents
  WHERE text_search_vector @@ to_tsquery('english', @query)
  ORDER BY rank DESC
  LIMIT 10;
  ```

### 3. Trigram Fuzzy Search (`pg_trgm`)
- **Concept**: The `pg_trgm` extension allows search matches based on string similarity (trigrams). This is ideal for fuzzy lookups, autocorrect matching, or typo-tolerant filters.
- **Syntax Example**:
  ```sql
  -- Search for fuzzy matches
  SELECT id, username, similarity(username, @searchTerm) AS similarity_score
  FROM users
  WHERE username % @searchTerm
  ORDER BY similarity_score DESC;
  ```
