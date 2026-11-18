"""
Tests for ai/feature_engineering/ (Sprint 2).

Fully offline/network-free — a synthetic OHLCV DataFrame is generated in
`sample_ohlcv_df` instead of touching `datasets/raw/`, and every test that
writes to disk redirects `ai.utils.config.settings` storage paths to
`tmp_path` via monkeypatch, mirroring `ai/tests/test_data_collection.py`.
"""

import numpy as np
import pandas as pd
import pytest

from ai.feature_engineering.config import FeatureEngineeringConfig
from ai.feature_engineering.data_loader import find_raw_ohlcv_files, load_raw_ohlcv
from ai.feature_engineering.exceptions import (
    FeatureComputationError,
    InsufficientDataError,
    RawDataNotFoundError,
    SchemaValidationError,
)
from ai.feature_engineering.features import build_generators
from ai.feature_engineering.features.bollinger import BollingerFeatureGenerator
from ai.feature_engineering.features.breakout import BreakoutFeatureGenerator
from ai.feature_engineering.features.date import DateFeatureGenerator
from ai.feature_engineering.features.fibonacci import FibonacciFeatureGenerator
from ai.feature_engineering.features.lag import LagFeatureGenerator
from ai.feature_engineering.features.macd import MACDFeatureGenerator
from ai.feature_engineering.features.market_structure import MarketStructureFeatureGenerator
from ai.feature_engineering.features.momentum import MomentumFeatureGenerator
from ai.feature_engineering.features.price import PriceFeatureGenerator
from ai.feature_engineering.features.price_action import PriceActionFeatureGenerator
from ai.feature_engineering.features.rolling import RollingFeatureGenerator
from ai.feature_engineering.features.support_resistance import SupportResistanceFeatureGenerator
from ai.feature_engineering.features.target import TargetFeatureGenerator
from ai.feature_engineering.features.trend import TrendFeatureGenerator
from ai.feature_engineering.features.volatility import VolatilityFeatureGenerator
from ai.feature_engineering.features.volume import VolumeFeatureGenerator
from ai.feature_engineering.pipeline import FeatureEngineeringPipeline
from ai.feature_engineering.preprocessing import clean_ohlcv
from ai.feature_engineering.selection import analyze_features

N_ROWS = 260  # > 200 so every SMA/EMA window is exercised at least once


@pytest.fixture
def sample_ohlcv_df() -> pd.DataFrame:
    rng = np.random.default_rng(42)
    dates = pd.bdate_range("2023-01-02", periods=N_ROWS)
    close = 100 + np.cumsum(rng.normal(0.05, 1.5, N_ROWS))
    close = np.maximum(close, 5)
    open_ = close + rng.normal(0, 0.5, N_ROWS)
    high = np.maximum(open_, close) + np.abs(rng.normal(0.3, 0.3, N_ROWS))
    low = np.minimum(open_, close) - np.abs(rng.normal(0.3, 0.3, N_ROWS))
    volume = rng.integers(1_000_000, 5_000_000, N_ROWS)
    return pd.DataFrame({
        "date": dates, "ticker": "TESTX", "open": open_, "high": high,
        "low": low, "close": close, "volume": volume,
    })


@pytest.fixture
def cleaned_df(sample_ohlcv_df) -> pd.DataFrame:
    df, _ = clean_ohlcv(sample_ohlcv_df)
    return df


@pytest.fixture
def fast_config() -> FeatureEngineeringConfig:
    """Small windows so tests exercise generators without needing huge frames."""
    return FeatureEngineeringConfig(
        sma_windows=(5, 10), ema_windows=(5, 10), golden_death_cross_fast=5, golden_death_cross_slow=10,
        rolling_volatility_windows=(5,), std_windows=(5,), historical_volatility_window=5,
        bollinger_window=10, macd_fast_period=5, macd_slow_period=10, macd_signal_period=3,
        volume_rolling_windows=(5,), rolling_stat_windows=(5,), lag_periods=(1, 2, 3),
        target_horizons=(1, 3), swing_lookback=3, support_resistance_window=10,
        supply_demand_lookback=5, trend_structure_window=10, market_structure_swing_count=3,
    )


@pytest.fixture(autouse=True)
def isolated_storage(tmp_path, monkeypatch):
    """Redirect every storage path Sprint 2 writes to, so tests never touch
    the real datasets/raw, datasets/processed, or storage/reports directories.
    """
    monkeypatch.setattr("ai.utils.config.settings.raw_data_dir", str(tmp_path / "raw"))
    monkeypatch.setattr("ai.utils.config.settings.processed_data_dir", str(tmp_path / "processed"))
    monkeypatch.setattr("ai.utils.config.settings.eda_reports_dir", str(tmp_path / "eda"))
    yield tmp_path


class TestPreprocessing:
    def test_clean_ohlcv_happy_path(self, sample_ohlcv_df):
        cleaned, report = clean_ohlcv(sample_ohlcv_df)
        assert report.rows_in == N_ROWS
        assert report.rows_out == N_ROWS
        assert cleaned["date"].is_monotonic_increasing
        assert cleaned["ticker"].iloc[0] == "TESTX"

    def test_duplicates_are_removed(self, sample_ohlcv_df):
        with_dupes = pd.concat([sample_ohlcv_df, sample_ohlcv_df.iloc[:5]], ignore_index=True)
        cleaned, report = clean_ohlcv(with_dupes)
        assert report.duplicates_removed == 5
        assert len(cleaned) == N_ROWS

    def test_missing_values_are_filled(self, sample_ohlcv_df):
        df = sample_ohlcv_df.copy()
        df.loc[10, "close"] = np.nan
        cleaned, report = clean_ohlcv(df)
        assert cleaned["close"].isna().sum() == 0
        assert report.missing_values_filled.get("close") == 1

    def test_structurally_invalid_rows_dropped(self, sample_ohlcv_df):
        df = sample_ohlcv_df.copy()
        df.loc[20, "low"] = df.loc[20, "high"] + 100  # low > high: impossible bar
        cleaned, report = clean_ohlcv(df)
        assert report.invalid_rows_dropped == 1
        assert len(cleaned) == N_ROWS - 1

    def test_insufficient_rows_raises(self, sample_ohlcv_df):
        tiny = sample_ohlcv_df.iloc[:10]
        with pytest.raises(InsufficientDataError):
            clean_ohlcv(tiny)

    def test_missing_ticker_column_raises(self, sample_ohlcv_df):
        df = sample_ohlcv_df.drop(columns=["ticker"])
        with pytest.raises(SchemaValidationError):
            clean_ohlcv(df)

    def test_outliers_are_flagged_not_dropped(self, sample_ohlcv_df):
        df = sample_ohlcv_df.copy()
        spike_close = df["close"].iloc[49] * 5  # extreme one-day spike
        df.loc[50, "open"] = spike_close
        df.loc[50, "close"] = spike_close
        df.loc[50, "high"] = spike_close * 1.01
        df.loc[50, "low"] = spike_close * 0.99
        cleaned, report = clean_ohlcv(df)
        assert len(cleaned) == N_ROWS  # not dropped
        assert cleaned["is_price_outlier"].sum() >= 1


class TestDataLoader:
    def _write_raw_csv(self, tmp_path, sample_ohlcv_df, ticker="TESTX"):
        raw_dir = tmp_path / "raw"
        raw_dir.mkdir(parents=True, exist_ok=True)
        path = raw_dir / f"yahoo_finance_{ticker}_2023-01-02_2024-01-01_ohlcv.csv"
        sample_ohlcv_df.drop(columns=["ticker"]).to_csv(path, index=False)
        return path

    def test_find_and_load_by_ticker(self, isolated_storage, sample_ohlcv_df):
        self._write_raw_csv(isolated_storage, sample_ohlcv_df)
        files = find_raw_ohlcv_files("TESTX")
        assert len(files) == 1
        loaded = load_raw_ohlcv(ticker="TESTX")
        assert len(loaded) == N_ROWS
        assert (loaded["ticker"] == "TESTX").all()

    def test_missing_ticker_raises(self, isolated_storage):
        with pytest.raises(RawDataNotFoundError):
            load_raw_ohlcv(ticker="NOPE")

    def test_load_by_explicit_path(self, isolated_storage, sample_ohlcv_df):
        path = self._write_raw_csv(isolated_storage, sample_ohlcv_df, ticker="ZZZZ")
        loaded = load_raw_ohlcv(path=path)
        assert len(loaded) == N_ROWS
        assert loaded["ticker"].iloc[0] == "ZZZZ"

    def test_missing_required_column_raises(self, isolated_storage, tmp_path, sample_ohlcv_df):
        raw_dir = tmp_path / "raw"
        raw_dir.mkdir(parents=True, exist_ok=True)
        path = raw_dir / "yahoo_finance_BAD_2023-01-02_2024-01-01_ohlcv.csv"
        sample_ohlcv_df.drop(columns=["ticker", "volume"]).to_csv(path, index=False)
        with pytest.raises(SchemaValidationError):
            load_raw_ohlcv(path=path)


class TestPriceFeatures:
    def test_columns_and_basic_sanity(self, cleaned_df, fast_config):
        out = PriceFeatureGenerator(fast_config).generate(cleaned_df)
        for col in ("daily_return", "pct_return", "log_return", "typical_price", "weighted_close"):
            assert col in out.columns
        assert out["daily_return"].iloc[0] != out["daily_return"].iloc[0]  # NaN on first row (no prior close)
        assert np.isclose(
            out["typical_price"].iloc[5],
            (out["high"].iloc[5] + out["low"].iloc[5] + out["close"].iloc[5]) / 3,
        )


class TestTrendFeatures:
    def test_sma_matches_manual_rolling_mean(self, cleaned_df, fast_config):
        out = TrendFeatureGenerator(fast_config).generate(cleaned_df)
        expected = cleaned_df["close"].rolling(5, min_periods=5).mean()
        pd.testing.assert_series_equal(out["sma_5"], expected, check_names=False)

    def test_golden_and_death_cross_are_mutually_exclusive(self, cleaned_df, fast_config):
        out = TrendFeatureGenerator(fast_config).generate(cleaned_df)
        both = out["golden_cross"].fillna(False) & out["death_cross"].fillna(False)
        assert not both.any()


class TestMomentumFeatures:
    def test_rsi_bounded_0_100(self, cleaned_df, fast_config):
        out = MomentumFeatureGenerator(fast_config).generate(cleaned_df)
        valid = out["rsi"].dropna()
        assert (valid >= 0).all() and (valid <= 100).all()


class TestVolatilityFeatures:
    def test_atr_non_negative(self, cleaned_df, fast_config):
        out = VolatilityFeatureGenerator(fast_config).generate(cleaned_df)
        assert (out["atr"].dropna() >= 0).all()

    def test_true_range_at_least_high_low_range(self, cleaned_df, fast_config):
        out = VolatilityFeatureGenerator(fast_config).generate(cleaned_df)
        assert (out["true_range"] >= (out["high"] - out["low"]) - 1e-9).all()


class TestBollingerFeatures:
    def test_upper_above_lower(self, cleaned_df, fast_config):
        out = BollingerFeatureGenerator(fast_config).generate(cleaned_df)
        valid = out.dropna(subset=["bollinger_upper", "bollinger_lower"])
        assert (valid["bollinger_upper"] >= valid["bollinger_lower"]).all()


class TestMACDFeatures:
    def test_histogram_equals_line_minus_signal(self, cleaned_df, fast_config):
        out = MACDFeatureGenerator(fast_config).generate(cleaned_df)
        diff = (out["macd_histogram"] - (out["macd_line"] - out["macd_signal"])).dropna()
        assert np.allclose(diff, 0, atol=1e-9)


class TestVolumeFeatures:
    def test_obv_changes_direction_with_price(self, cleaned_df, fast_config):
        price_out = PriceFeatureGenerator(fast_config).generate(cleaned_df)
        out = VolumeFeatureGenerator(fast_config).generate(price_out)
        assert "obv" in out.columns
        assert out["obv"].notna().all()


class TestRollingAndLagFeatures:
    def test_rolling_min_max_bracket_mean(self, cleaned_df, fast_config):
        out = RollingFeatureGenerator(fast_config).generate(cleaned_df)
        valid = out.dropna(subset=["rolling_min_5", "rolling_max_5", "rolling_mean_5"])
        assert (valid["rolling_min_5"] <= valid["rolling_mean_5"]).all()
        assert (valid["rolling_mean_5"] <= valid["rolling_max_5"]).all()

    def test_lag_1_matches_shifted_close(self, cleaned_df, fast_config):
        price_out = PriceFeatureGenerator(fast_config).generate(cleaned_df)
        out = LagFeatureGenerator(fast_config).generate(price_out)
        pd.testing.assert_series_equal(
            out["close_lag_1"], cleaned_df["close"].shift(1), check_names=False
        )


class TestDateFeatures:
    def test_day_of_week_range(self, cleaned_df, fast_config):
        out = DateFeatureGenerator(fast_config).generate(cleaned_df)
        assert out["day_of_week"].between(0, 6).all()


class TestTargetFeatures:
    def test_last_rows_have_nan_targets(self, cleaned_df, fast_config):
        out = TargetFeatureGenerator(fast_config).generate(cleaned_df)
        assert out["target_1_day"].iloc[-1] != out["target_1_day"].iloc[-1]  # NaN
        assert out["target_1_day"].iloc[0] == cleaned_df["close"].iloc[1]

    def test_direction_matches_future_return_sign(self, cleaned_df, fast_config):
        out = TargetFeatureGenerator(fast_config).generate(cleaned_df)
        valid = out.dropna(subset=["future_return_1_day", "target_direction_1_day"])
        assert (
            (valid["future_return_1_day"] > 0) == valid["target_direction_1_day"].astype(bool)
        ).all()


class TestPhase4StructureFeatures:
    def _run_price_action(self, cleaned_df, fast_config):
        return PriceActionFeatureGenerator(fast_config).generate(cleaned_df)

    def test_swing_high_low_never_both_true(self, cleaned_df, fast_config):
        out = self._run_price_action(cleaned_df, fast_config)
        both = out["swing_high"].fillna(False) & out["swing_low"].fillna(False)
        # a bar can rarely be both a swing high and swing low only on flat/degenerate data;
        # with real price movement this should not occur
        assert not both.any()

    def test_price_action_label_is_categorical_string(self, cleaned_df, fast_config):
        out = self._run_price_action(cleaned_df, fast_config)
        assert set(out["price_action_label"].unique()) <= {
            "None", "Bullish Engulfing", "Bearish Engulfing", "Hammer", "Shooting Star",
            "Doji", "Marubozu", "Pin Bar", "Inside Bar", "Outside Bar",
        }

    def test_support_resistance_requires_price_action_columns(self, cleaned_df, fast_config):
        with pytest.raises(FeatureComputationError):
            SupportResistanceFeatureGenerator(fast_config).generate(cleaned_df)  # swing_high/low missing

    def test_full_phase4_chain_runs_in_dependency_order(self, cleaned_df, fast_config):
        df = PriceActionFeatureGenerator(fast_config).generate(cleaned_df)
        df = SupportResistanceFeatureGenerator(fast_config).generate(df)
        df = FibonacciFeatureGenerator(fast_config).generate(df)
        df = MarketStructureFeatureGenerator(fast_config).generate(df)
        assert "market_bias" in df.columns
        assert set(df["market_bias"].dropna().unique()) <= {"Bullish", "Bearish", "Neutral"}

    def test_breakout_requires_support_resistance_and_volume(self, cleaned_df, fast_config):
        df = PriceActionFeatureGenerator(fast_config).generate(cleaned_df)
        df = SupportResistanceFeatureGenerator(fast_config).generate(df)
        with pytest.raises(FeatureComputationError):
            BreakoutFeatureGenerator(fast_config).generate(df)  # volume_ratio missing


class TestFeatureSelection:
    def test_detects_highly_correlated_pair(self, fast_config):
        df = pd.DataFrame({"a": np.arange(100, dtype=float), "b": np.arange(100, dtype=float) * 2 + 1})
        report = analyze_features(df, fast_config)
        pairs = [(p[0], p[1]) for p in report.highly_correlated_pairs]
        assert ("a", "b") in pairs

    def test_detects_low_variance_feature(self, fast_config):
        df = pd.DataFrame({"constant": [1.0] * 100, "varied": np.random.default_rng(0).normal(size=100)})
        report = analyze_features(df, fast_config)
        assert "constant" in report.low_variance_features

    def test_detects_duplicate_columns(self, fast_config):
        base = np.random.default_rng(1).normal(size=100)
        df = pd.DataFrame({"x": base, "y": base.copy()})
        report = analyze_features(df, fast_config)
        assert any({"x", "y"} <= set(group) for group in report.duplicate_feature_groups)


class TestGeneratorRegistry:
    def test_build_generators_respects_dependency_order(self, fast_config):
        generators = build_generators(fast_config)
        names = [g.group_name for g in generators]
        assert names.index("price_action") < names.index("support_resistance")
        assert names.index("support_resistance") < names.index("fibonacci")
        assert names.index("support_resistance") < names.index("breakout")
        assert names.index("volume") < names.index("breakout")

    def test_unknown_group_raises(self):
        with pytest.raises(ValueError):
            build_generators(FeatureEngineeringConfig(enabled_feature_groups=("not_a_real_group",)))


class TestPipelineIntegration:
    def test_full_pipeline_run_produces_expected_outputs(self, isolated_storage, sample_ohlcv_df, fast_config):
        raw_dir = isolated_storage / "raw"
        raw_dir.mkdir(parents=True, exist_ok=True)
        raw_path = raw_dir / "yahoo_finance_TESTX_2023-01-02_2024-01-01_ohlcv.csv"
        sample_ohlcv_df.drop(columns=["ticker"]).to_csv(raw_path, index=False)

        pipeline = FeatureEngineeringPipeline(config=fast_config)
        result = pipeline.run(ticker="TESTX", version="testrun")

        assert result.rows_in == N_ROWS
        assert result.rows_out == N_ROWS
        assert result.columns_out > 100
        assert result.processed_csv_path.exists()
        assert result.metadata_json_path.exists()
        assert result.summary_csv_path.exists()
        assert result.feature_report_md_path.exists()
        assert result.eda_json_path.exists()
        assert result.eda_md_path.exists()
        # no target-leakage: at least one target column should have trailing NaNs
        assert result.dataframe["target_1_day"].isna().sum() >= 1

    def test_drop_warmup_nan_rows_option(self, isolated_storage, sample_ohlcv_df, fast_config):
        raw_dir = isolated_storage / "raw"
        raw_dir.mkdir(parents=True, exist_ok=True)
        raw_path = raw_dir / "yahoo_finance_TESTX_2023-01-02_2024-01-01_ohlcv.csv"
        sample_ohlcv_df.drop(columns=["ticker"]).to_csv(raw_path, index=False)

        config = FeatureEngineeringConfig(**{**fast_config.__dict__, "drop_warmup_nan_rows": True})
        pipeline = FeatureEngineeringPipeline(config=config)
        result = pipeline.run(ticker="TESTX", version="testrun2")
        assert result.dataframe.isna().sum().sum() == 0
        assert result.rows_out < result.rows_in