"""
Configuration for `ai/feature_engineering/`.

Two kinds of configuration exist in this project, deliberately kept apart:

- `ai/utils/config.py::settings` — environment-variable-backed settings
  (API keys, storage paths, log level). Every module reads from there.
- `FeatureEngineeringConfig` (this file) — non-secret, purely computational
  tunables (SMA windows, RSI period, rolling window sizes, target horizons).
  These are not secrets and change per-experiment, so they are passed as a
  plain, serializable dataclass through the pipeline instead of living in
  `.env`. This satisfies the sprint's "Configuration Driven" design
  requirement without polluting the centralized env-settings object.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class FeatureEngineeringConfig:
    """All tunable parameters for the Sprint 2 feature pipeline.

    Frozen (immutable) so a config object can be safely reused/shared across
    generators and logged verbatim as part of run metadata for reproducibility
    (mirrors ARCHITECTURE.md §2.3 — every run should be traceable).
    """

    # --- Trend (SMA / EMA) ------------------------------------------------
    sma_windows: tuple[int, ...] = (5, 10, 20, 50, 100, 200)
    ema_windows: tuple[int, ...] = (5, 10, 20, 50, 100, 200)
    golden_death_cross_fast: int = 50
    golden_death_cross_slow: int = 200

    # --- Momentum -----------------------------------------------------------
    rsi_period: int = 14
    roc_period: int = 12
    momentum_period: int = 10
    volume_momentum_period: int = 10

    # --- Volatility -----------------------------------------------------------
    atr_period: int = 14
    rolling_volatility_windows: tuple[int, ...] = (10, 20, 30)
    historical_volatility_window: int = 20
    trading_days_per_year: int = 252  # for annualizing historical volatility
    std_windows: tuple[int, ...] = (10, 20)

    # --- Bollinger Bands ------------------------------------------------------
    bollinger_window: int = 20
    bollinger_num_std: float = 2.0

    # --- MACD -----------------------------------------------------------------
    macd_fast_period: int = 12
    macd_slow_period: int = 26
    macd_signal_period: int = 9

    # --- Volume -----------------------------------------------------------------
    volume_rolling_windows: tuple[int, ...] = (10, 20)
    volume_change_period: int = 1

    # --- Rolling window statistics (generic, applied to `close`) --------------
    rolling_stat_windows: tuple[int, ...] = (5, 10, 20)

    # --- Lag features -----------------------------------------------------------
    lag_periods: tuple[int, ...] = (1, 2, 3, 5, 10, 20)

    # --- Targets ------------------------------------------------------------
    target_horizons: tuple[int, ...] = (1, 3, 5)

    # --- Phase 4: Price action / structure -------------------------------------
    swing_lookback: int = 5              # bars on each side to confirm a swing high/low
    support_resistance_window: int = 20   # window used to detect pivot-based S/R
    support_resistance_tolerance_pct: float = 0.015  # 1.5% band for level clustering
    supply_demand_lookback: int = 20
    breakout_confirmation_volume_multiplier: float = 1.5  # vs. rolling avg volume
    trend_structure_window: int = 20
    market_structure_swing_count: int = 4  # number of recent swings considered for HH/HL/LH/LL counts

    # --- Feature selection thresholds -----------------------------------------
    high_correlation_threshold: float = 0.95
    low_variance_threshold: float = 1e-6

    # --- Pipeline behavior ------------------------------------------------------
    drop_warmup_nan_rows: bool = False
    """If True, the pipeline drops leading rows that still contain NaNs from
    the largest rolling window (e.g. the first 199 rows for a 200-day SMA)
    before saving. Default False: warm-up NaNs are documented in the feature
    report instead, since dropping them discards otherwise-valid rows that
    shorter-window models could still use.
    """

    enabled_feature_groups: tuple[str, ...] = field(
        default_factory=lambda: (
            "price",
            "trend",
            "momentum",
            "volatility",
            "bollinger",
            "macd",
            "volume",
            "rolling",
            "lag",
            "date",
            "price_action",
            "support_resistance",
            "fibonacci",
            "market_structure",
            "breakout",
            "target",
        )
    )
    """Ordered list of feature-group names to run. Order matters: some groups
    (e.g. `support_resistance`, `fibonacci`, `breakout`) depend on columns
    produced by earlier groups (`price`, `trend`, `volatility`)."""


DEFAULT_CONFIG = FeatureEngineeringConfig()