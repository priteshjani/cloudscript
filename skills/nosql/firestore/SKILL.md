---
name: firestore-operations
description: Retrieve and write documents inside collections in Google Cloud Firestore database. Use when managing document schemas or flexible app metadata.
---
# Firestore Operations Skill

This skill allows the agent to fetch, write, and delete documents inside Firestore collections.

## When to use this skill
- Use to manage loose schemas, JSON configurations, user-session preferences, or hierarchical document trees.
- Use to record real-time application states or event flags.

## Technical Guidance
- **Document Path Constraints**: Ensure collection names and document IDs are parameterized. Avoid raw path concats to block traversal exploits.
- **Batching operations**: If writing multiple records (e.g. up to 500 documents), always use Firestore `WriteBatch` to execute them atomically in a single write operation.
- **Queries**: Enforce collection queries to use explicit indexes. Firestore automatically indexes single fields, but composite fields require manual index configuration.
