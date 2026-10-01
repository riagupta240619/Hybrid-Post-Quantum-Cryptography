# Phase 1 Architecture

The API route layer validates HTTP input and maps service errors to HTTP responses. Services own device operations, SQLAlchemy models define persistence, and the database session dependency scopes database access to a request. Pydantic schemas define the API contract independently from ORM entities.

The browser talks to the versioned API through Vite's `/api` development proxy or the frontend Nginx reverse proxy in Compose. PostgreSQL is initialized before the API starts; the initial startup creates tables from SQLAlchemy metadata. This is intentionally small and can be replaced by Alembic migrations in Phase 2.

Backend tests override the production session dependency with a fresh in-memory SQLite database for each test. They never use the configured PostgreSQL URL.

There is no encryption, key exchange, digital signature, worker, simulator, or benchmark implementation in this phase. The `backend/app/crypto/` package is reserved for future reviewed provider integrations only.