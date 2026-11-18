# Contributing / Git Workflow

## Branch structure

- `main` — production-ready code only. Protected. No direct pushes.
- `develop` — integration branch. All feature branches merge here first.
- `feature/frontend` — frontend feature work.
- `feature/backend` — backend feature work.
- `feature/ai` — AI/ML/DL/NLP/LLM feature work.

Use scoped feature branches off these, e.g. `feature/backend/auth-jwt`,
`feature/ai/lstm-model`.

## Workflow

```
feature/* branch  →  develop  →  Testing (CI)  →  main
```

1. Branch off `develop` for any new work.
2. Open a PR back into `develop`. CI (`.github/workflows/ci.yml`) must pass:
   backend tests, ai tests, frontend lint/tests.
3. Once `develop` is stable and tested, open a PR from `develop` into `main`.
4. **Never push directly to `main`.** **Never merge without passing tests.**

## Commit messages

Use conventional, meaningful messages, e.g.:

```
feat(ai): add LSTM model for price forecasting
fix(backend): correct JWT refresh token expiry
docs(architecture): update data flow diagram
```

## Code standards

- Type hints required on all Python functions.
- One responsibility per function/module (SOLID).
- No duplicated logic — extract shared code into `utils/`.
- Every new module needs a corresponding test in the matching `tests/` folder.
- Every new top-level folder needs a `README.md` explaining its purpose.
