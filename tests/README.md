# Test Organization

Backend API and service tests live in `backend/tests/` and use an isolated in-memory SQLite database. This top-level directory is reserved for cross-service integration tests when a later phase adds workflows that need them; Phase 1 does not require running the production database to test the API.
