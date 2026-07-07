# Jetski Agent Architecture: Deep Technical Guide

This document outlines the design patterns, system prompt engineering, and execution loops of the AI agents within the Jetski Framework.

## Core Architecture

Agents in this framework are built on the **ReAct (Reasoning and Acting)** and **Plan-and-Solve** design patterns. Instead of directly executing tasks, agents follow a structured, multi-turn reasoning path:

```
[User Task] ──> [Reasoning / CoT] ──> [Tool Selection] ──> [Skill Execution]
                     ▲                                             │
                     └──────────────── [Observation] ◄─────────────┘
```

1. **System Prompt Formulation**: Compiles system instructions, environment variables, active GCP credentials, and bound tools into a single prompt context.
2. **Thought (CoT)**: The agent explains its reasoning about what needs to be done.
3. **Action**: The agent decides to call a skill (tool) with specific parameters.
4. **Observation**: The system executes the skill, returning the payload back to the agent.
5. **Evaluation**: The agent checks the result, handles errors, and decides if it can complete the task or if it needs another iteration.

---

## Technical Specifications

### 1. Base Agent Interface (`base.py`)
The [BaseAgent](file:///Users/priteshjani/Documents/jetski/agents/base.py) class provides the runtime wrapper for LLM interaction:
- **State Management**: Keeps track of conversation history and system parameters.
- **Context Boundary Isolation**: Restricts tool parameters to prevent SQL injection or path traversal.
- **Cost & Token Monitoring**: Tracks input/output token usage to prevent context blowup.

### 2. Specialized Agents

#### A. Database Agent (`db_agent.py`)
- **Focus**: Transactional consistency, schema mapping, and DDL/DML execution across Spanner, AlloyDB, and CloudSQL.
- **Prompt Strategies**: Instructed to inspect system schemas, construct parameterized queries, and run pre-flight dry runs.
- **Constraints**:
  - Always enforce `LIMIT 100` for exploratory queries.
  - Require explicit verification before writing DML.
  - Fail-safe check: Catch transactional lock timeouts and advise backoffs.

#### B. NoSQL Agent (`nosql_agent.py`)
- **Focus**: Performance optimization, high-throughput key-value operations, cache invalidation, and document stores across Bigtable, Firestore, and Memorystore (Redis).
- **Prompt Strategies**: Key-design strategies, JSON payload validation, pipeline batching, and key-expiry policies.
- **Constraints**:
  - Prevent full key scans (e.g. `KEYS *` in Memorystore or missing row limits in Bigtable).
  - Enforce structured payload validation against schemas for Firestore.

#### C. Analyst Agent (`analyst_agent.py`)
- **Focus**: Multi-stage analytics, federated queries, data warehouse optimizations, and ETL pipelines in BigQuery.
- **Prompt Strategies**: Optimized partitioning, clustering, using `EXPLAIN` to diagnose query cost, and building federated queries (e.g. querying Spanner/AlloyDB external sources).
- **Constraints**:
  - Enforce partitioning filters on BigQuery queries.
  - Recommend materialized views for repetitive aggregations.

#### D. Catalog Agent (`catalog_agent.py`)
- **Focus**: Discovery, governance, classification, and tagging of Data Lakehouse assets inside GCP Knowledge Catalog (Dataplex).
- **Prompt Strategies**: Query-syntax filters to scope discovery, identifying fields containing PII or sensitive values, and attaching policy tag templates.
- **Constraints**:
  - Ensure entry paths are fully qualified before writing tag updates.

---

## Prompts & In-Context Learning (ICL) Best Practices

### System Instruction Template
When compiling prompts, use XML tags to separate instructions, context, and history:

```markdown
<system_instructions>
Define role, limits, and security constraints.
</system_instructions>

<gcp_context>
Project ID: {gcp_project_id}
Region: {gcp_region}
</gcp_context>

<available_tools>
JSON Schema of skills
</available_tools>

<conversation_history>
Previous turns
</conversation_history>
```

### Self-Correction Loop
If a skill throws an error (e.g. a syntax error in SQL), the agent should not immediately fail. The system prompt instructs the agent to:
1. Parse the error traceback.
2. Identify the parameter or syntax that caused the failure.
3. Formulate an alternative query or parameter set.
4. Retry the action up to a maximum of 3 times before raising a workflow exception.
