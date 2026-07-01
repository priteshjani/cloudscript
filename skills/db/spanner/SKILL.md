---
name: spanner-operations
description: Execute queries and explore schemas on Google Cloud Spanner databases. Use when reading transactional records, running Spanner Graph queries, conducting vector searches, or executing hybrid searches.
---
# Spanner Operations Skill

This skill allows the agent to execute queries, utilize Spanner Graph, run vector similarity matches, and perform hybrid full-text/vector searches on Cloud Spanner.

## Advanced Features & Technical Guidance

### 1. Spanner Graph
- **Concept**: Cloud Spanner supports native Property Graphs within relational schemas, allowing queries to search deep network paths using standard SQL with `GRAPH_TABLE` and Cypher syntax.
- **Syntax Example**:
  ```sql
  SELECT * FROM GRAPH_TABLE(
    AccountGraph
    MATCH (a:Account)-[t:TransfersTo]->(b:Account)
    WHERE a.id = @accountId
    RETURN a.name AS sender, b.name AS recipient, t.amount AS amount
  )
  ```

### 2. Spanner Vector Search
- **Concept**: Spanner allows querying and index-searching vector embeddings. It supports standard vector distance metrics (`COSINE_DISTANCE`, `EUCLIDEAN_DISTANCE`, etc.) alongside Approximate Nearest Neighbor (ANN) index searches (`APPROX_COSINE_DISTANCE`).
- **ANN Queries**: To use index-based vector lookups, use the `APPROX_` variant of distance functions:
  ```sql
  SELECT document_id, COSINE_DISTANCE(embedding, @queryEmbedding) AS distance
  FROM documents
  ORDER BY APPROX_COSINE_DISTANCE(embedding, @queryEmbedding, @options)
  LIMIT 5
  ```

### 3. Spanner Hybrid Search
- **Concept**: Hybrid search combines full-text search (structured `SEARCH` indexes) and vector distance scores to find relevant rows using multiple criteria in a single query.
- **Structure Example**:
  ```sql
  SELECT doc_id, SCORE(search_index_col, @searchTerm) AS text_score, COSINE_DISTANCE(emb, @vector) AS vec_score
  FROM documents
  WHERE SEARCH(search_index_col, @searchTerm)
  ORDER BY vec_score ASC, text_score DESC
  LIMIT 10
  ```
