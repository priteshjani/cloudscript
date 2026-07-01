---
name: bigquery-operations
description: Run queries and retrieve datasets in Google Cloud BigQuery. Use when executing aggregations, SQL graph queries, geospatial partitioning, Iceberg external tables, and analytics workloads.
---
# BigQuery Operations Skill

This skill allows the agent to execute queries, leverage SQL Graph, partition tables geospatially, and query BigLake Apache Iceberg tables in BigQuery.

## Advanced Features & Technical Guidance

### 1. BigQuery Graph (SQL Graph)
- **Concept**: BigQuery allows defining Property Graph schemas over relational tables (Nodes and Edges) and querying them using Cypher-like graph syntax.
- **Querying**: Use the `GRAPH_TABLE` table function within standard SQL queries.
  ```sql
  SELECT * FROM GRAPH_TABLE(
    my_project.my_dataset.my_graph
    MATCH (s:Source)-[e:Transfers]->(t:Target)
    WHERE s.reputation < 0.2
    RETURN s.id AS src, t.id AS dest, e.amount AS value
  )
  ```

### 2. Geospatial (Geo) Partitioning
- **Concept**: Partition tables using a `GEOGRAPHY` column type. This optimizes queries that filter on geographic regions (e.g. bounding boxes or polygons).
- **Table Definition**: Establish a table with geo partitioning by specifying the partition boundaries or a spatial key (e.g., partitioning by longitude/latitude grid cells or zip boundaries).
- **Function Usage**: Use geospatial functions like `ST_CONTAINS`, `ST_DISTANCE`, and `ST_DWITHIN` in your query predicates to prune partitions.

### 3. Apache Iceberg (BigLake External Tables)
- **Concept**: Iceberg is an open table format for huge analytic datasets. BigQuery queries Iceberg tables stored in Google Cloud Storage using BigLake connection metadata, providing object store query speeds close to native storage.
- **Query Optimization**: When querying external Iceberg tables, ensure the query includes filters that match the Iceberg table partition layout to utilize Iceberg's metadata-based partition pruning directly at the object-storage level.
