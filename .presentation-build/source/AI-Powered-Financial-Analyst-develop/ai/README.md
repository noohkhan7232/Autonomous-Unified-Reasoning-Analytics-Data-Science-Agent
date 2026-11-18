# AI / Research Layer

All modeling, training, and inference logic. Fully decoupled from `backend/` —
these modules take DataFrames/dicts in and return DataFrames/dicts out, with
no FastAPI or database imports, so they stay independently testable and
reusable in notebooks.

| Folder | Module | Purpose |
|---|---|---|
| `data_collection/` | Module 1 | Provider adapters (Yahoo Finance default; Alpha Vantage, Polygon, Twelve Data) |
| `feature_engineering/` | Module 2 | Technical indicators, lag features, rolling stats |
| `models/ml/` | Module 3 | Linear Regression, Random Forest, XGBoost, (LightGBM/CatBoost optional) |
| `models/time_series/` | Module 4 | ARIMA, SARIMA, Prophet |
| `models/deep_learning/` | Module 5 | LSTM, GRU, (Transformer optional) |
| `nlp/` | Module 6 | FinBERT sentiment, news classification/summarization |
| `decision_engine/` | Module 7 | Aggregates predictions + sentiment → confidence/risk/signal |
| `llm/` | Module 8 | Explanation-only layer (Gemini/Groq/OpenRouter). **Never predicts prices.** |
| `utils/` | — | Shared helpers (logging, validation) |
| `tests/` | — | Pytest suite, one test file per module |

Run tests: `pytest ai/tests`
