# Integration Tests

Cross-cutting tests that exercise backend + ai together (e.g. full pipeline:
data collection → features → prediction → decision → API response). Unit
tests for each layer live inside that layer (`backend/tests/`, `ai/tests/`).
