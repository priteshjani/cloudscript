---
name: bigtable-operations
description: Read and write rows in Google Cloud Bigtable instances. Use when handling high-throughput, low-latency NoSQL structured data.
---
# Bigtable Operations Skill

This skill allows the agent to read and write rows from a Cloud Bigtable instance.

## When to use this skill
- Use to perform low-latency reads or single-row mutations on wide-column NoSQL databases.
- Use to fetch real-time operational dashboard stats or streaming telemetry records.

## Technical Guidance
- **Row Key Design**: Row keys dictate retrieval performance. Do not use random UUIDs; design hierarchical, lexicographically sorted row keys (e.g. `user#1290381023#metric#logins`).
- **Column Families**: Group related columns into column families to avoid retrieving unnecessary cells during row reads.
- **Row Filters**: Use filters to restrict cells to specific column families, column qualifiers, or version counts (e.g. latest cell value).
