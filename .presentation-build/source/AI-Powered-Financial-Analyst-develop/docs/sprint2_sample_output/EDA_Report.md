# EDA Report — SAMPLE
_Generated: 2026-07-12T18:38:29.701803+00:00_

## Dataset Shape
300 rows x 7 columns

## Data Types
| Field | Value |
|---|---|
| date | datetime64[us] |
| ticker | str |
| open | float64 |
| high | float64 |
| low | float64 |
| close | float64 |
| volume | int64 |

## Missing Values (raw, before cleaning)
| Field | Value |
|---|---|

## Duplicate Rows (raw)
0

## Time Series Trend
| Field | Value |
|---|---|
| first_close | 100.05184523003622 |
| last_close | 55.66122531203722 |
| net_change_pct | -44.36761742468359 |
| min_close | 46.9160302243825 |
| max_close | 100.54996353629893 |

## Data Quality Report (Phase 2 cleaning outcome)
| Field | Value |
|---|---|
| rows_in | 300 |
| rows_out | 300 |
| duplicates_removed | 0 |
| missing_values_before | {'open': 0, 'high': 0, 'low': 0, 'close': 0, 'volume': 0} |
| missing_values_filled | {} |
| invalid_rows_dropped | 0 |
| outliers_flagged | 0 |
| date_parse_failures | 0 |
| ticker_normalized | SAMPLE |

### Cleaning Notes
- None

## Summary Statistics, Price/Volume Distribution, Correlation Matrix
See the accompanying `.json` report for full numeric detail (kept out of this markdown file to stay lightweight per Sprint 2 scope).