---
name: dataplex-catalog-operations
description: Search, explore, and tag data assets using Google Cloud Dataplex (Knowledge Catalog) in a Data Lakehouse architecture. Use when discovering schemas, verifying asset lineage, or applying governance tags.
---
# Dataplex Catalog Operations Skill

This skill allows the agent to search for assets, retrieve schema metadata, and manage policy tags in the GCP Knowledge Catalog (Dataplex).

## When to use this skill
- Use to discover what tables or files exist in the Data Lakehouse (BigQuery, Spanner, AlloyDB, or Cloud Storage buckets).
- Use to apply business metadata or data quality tags to catalog entries.
- Use to retrieve asset descriptions and column types to build dynamic data pipelines.

## Technical Guidance
- **Catalog Search Syntax**: Use query syntax filters (e.g. `system=bigquery`, `type=table`, `parent=dataset_id`) to scope searches and avoid massive un-indexed lookups.
- **Tag Templates**: Retrieve tag templates before creating tags. A tag must match the field requirements (types like `string`, `double`, `enum`, `timestamp`) defined in its template.
- **Entry Names**: Dataplex Catalog uses fully qualified entry names (e.g., `projects/{project_id}/locations/{location}/entryGroups/{entry_group}/entries/{entry_id}`). Use these paths for tag attachments.
