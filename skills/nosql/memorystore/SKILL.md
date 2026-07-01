---
name: memorystore-operations
description: Set and get key-value pairs in Google Cloud Memorystore for Redis instance. Use when managing cached lookup maps, cache-aside data pipelines, or high-performance session stores.
---
# Memorystore (Redis) Operations Skill

This skill allows the agent to get, set, and invalid cache values inside a Memorystore Redis instance.

## When to use this skill
- Use to cache high-frequency SQL database query results (cache-aside pattern).
- Use to retrieve transient token flags or user session preferences.

## Technical Guidance
- **Explicit Key TTLs**: Never set a key without a TTL (Time To Live). Unbounded key storage leads to Redis Out of Memory (OOM) failures.
- **Key Namespaces**: Use standard formatting structures (`namespace:subspace:id`) to group keys and avoid overlaps.
- **Batching Operations**: Use redis pipeline (`pipeline = client.pipeline()`) when performing multiple PING, GET, or SET operations to avoid network socket round-trip delays.
