# Jetski Workflow Engine: Deep Technical Guide

This document outlines the workflow execution engine, state transition mechanisms, transaction rollbacks, and frontend integration patterns inside the Jetski Framework.

## Execution Model

Workflows in the Jetski framework operate as **Stateful Orchestrators** modeled as Directed Acyclic Graphs (DAGs) or Finite State Machines (FSM). 

The orchestrator guarantees:
1. **Deterministic Execution Paths**: Workflows define explicit inputs, outputs, states, and transition rules.
2. **Context Persistence**: The shared state payload (`context`) is updated atomically at each stage boundaries.
3. **Resilience**: Workflows implement try-catch boundaries to execute transactional rollbacks or invoke Database Agents to reconcile anomalies.

---

## Technical Specifications

### 1. Workflow Orchestrator (`orchestrator.py`)
The [WorkflowOrchestrator](file:///Users/priteshjani/Documents/jetski/workflow/orchestrator.py) manages the registration and execution cycle of workflows:
- **Registry Pattern**: Workflows register their class types to the orchestrator.
- **Trace Context Routing**: Binds trace headers so all sub-operations executed under a workflow run share a unique trace ID.
- **API Boundary**: Exposes lifecycle methods (`start`, `status`, `pause`, `resume`, `abort`) that map directly to REST endpoints or WebSocket events for the React frontend.

### 2. State Machine Mechanics (`base.py`)
Every workflow inherits from [BaseWorkflow](file:///Users/priteshjani/Documents/jetski/workflow/base.py), which defines the state transition lifecycle:

```text
               ┌───────────────────────┐
               │      INITIALIZED      │
               └───────────┬───────────┘
                           │
                           ▼
               ┌───────────────────────┐
               │    RUNNING STATES     ├────────┐
               └─────┬───────────▲─────┘        │
                     │           │              ▼
                     │           │      ┌──────────────┐
                     │           │      │    PAUSED    │
                     │           │      │   (HITL UI)  │
                     │           │      └──────┬───────┘
                     │           │             │
                     ▼           └─────────────┘
               ┌───────────┐
               │ COMPLETED │ or ┌───────────┐
               └───────────┘    │  FAILED   │
                                └───────────┘
```

- **State Transition Guard**: The `set_state` method ensures that transitions only occur between valid states.
- **Atomic Context Updates**: The `update_context` method merges new data into the shared state payload using thread-safe dictionaries.

---

## Resilience & Human-In-The-Loop (HITL)

### 1. Rollback & Idempotence
When a workflow step fails, the workflow must revert system states to prevent partial updates. 
- **Compensation Steps**: Each state must define a reverse operation. For example, if a data loading step fails after a table creation step, the workflow should execute a drop table or truncate step inside its compensation block.
- **Idempotency Keys**: All write actions must include an idempotency key (e.g. transaction UUID) to allow safe retries.

### 2. Human-In-The-Loop (HITL)
For critical operations (e.g., executing a schema migration on Spanner or flushing a Memorystore instance), the workflow must support pausing execution:
1. **Transition to `PAUSED`**: The workflow updates its state, saves its context to Firestore, and emits a notification to the React frontend.
2. **Await Approval**: The execution thread blocks or yields until an external endpoint receives a POST request containing user approval.
3. **Resume Execution**: The orchestrator reloads the saved context from Firestore, transitions the state back to the active execution state, and resumes from the suspended step.

---

## Frontend Integration (React)

To provide real-time workflow visualizer feedback:
- **Websockets / SSE**: The orchestrator can emit state change events containing the current state, runtime duration, and partial logs:
  ```json
  {
    "workflow_id": "wf_1293810239",
    "workflow_name": "DBSyncWorkflow",
    "state": "WRITING_TARGET",
    "timestamp": "2026-06-30T12:42:00-07:00",
    "logs": ["Step 3: Loading records into BigQuery dataset..."]
  }
  ```
- **React Visualizer**: The frontend uses these events to render a dynamic node graph indicating successful, active, paused, or failed stages.
