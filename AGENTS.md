# Workspace Agent Guidelines & Constraints

This document defines core constraints, coding standards, and security boundaries that all AI agents operating in the Jetski workspace must follow.

---

## 1. Code Style & Standards

- **Language**: Python 3.10+
- **Formatting**: Adhere to PEP 8 standards. Use 4 spaces for indentation.
- **Type Annotations**: Always declare input and output type hints for functions and methods (e.g. `def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:`).
- **Docstrings**: Document all classes and public methods using Google Python Style Guide docstring format.
- **Logging**: Do not use raw `print()` statements. Use standard python logging:
  ```python
  import logging
  logger = logging.getLogger(__name__)
  logger.info("Message")
  ```

---

## 2. Database Security & Operations

### A. SQL Parameterization
- **Strict Rule**: Never build SQL queries using string formatting or concats (`f"SELECT * FROM Users WHERE id = {user_id}"`).
- **Standard**: Always pass arguments through query parameters/bind variables:
  ```python
  query = "SELECT * FROM Users WHERE id = @user_id"
  params = {"user_id": user_id}
  ```

### B. Exploratory Query Limits
- **Strict Rule**: All exploratory or read-only queries executed by agents during runtime must declare an explicit `LIMIT 100` clause unless explicitly instructed otherwise.

### C. Write Boundaries (DDL/DML)
- **Production Safety**: Never run destructive statements (e.g., `DROP TABLE`, `TRUNCATE`, `DELETE` without a `WHERE` clause) on production datasets.
- **Pre-flight Checks**: Before executing DML, verify the schema layout by running a schema lookup first.

---

## 3. Caching & NoSQL Guidelines

- **TTL Enforcement**: Always declare a Time-to-Live (TTL) expiration when setting keys in Memorystore/Redis.
- **Firestore Batching**: Limit bulk writes to batches of 500 documents.
- **Bigtable Filters**: Always apply filters when reading rows to prevent over-scanning columns.

---

## 4. Error Recovery & Graceful Failures

- **Resilience**: Wrap operations in try-except blocks. Handle specific database errors (e.g., `Aborted`, `Deadlock`, `ConnectionError`) instead of catching generic exceptions when possible.
- **Self-Correction**: If a database query fails due to syntax or schema misalignment, read the error output, adjust query arguments, and retry up to 3 times before failing the workflow.
