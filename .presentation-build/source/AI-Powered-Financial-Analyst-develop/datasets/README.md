# Datasets

Not version-controlled (see `.gitignore`) — this folder defines the expected
layout only. `.gitkeep` files preserve the empty structure in git.

| Folder | Purpose |
|---|---|
| `raw/` | Untouched data pulled directly from providers |
| `processed/` | Cleaned, feature-engineered data ready for model training |
| `external/` | Third-party reference datasets (e.g. macroeconomic indicators) |

Large or proprietary datasets should be pulled via the scripts in `scripts/`,
never committed directly.
