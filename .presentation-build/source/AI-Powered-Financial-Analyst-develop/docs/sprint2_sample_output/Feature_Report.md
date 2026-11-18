# Feature Report — SAMPLE (sample)

## price
### `daily_return`  _(Priority: Medium)_
- **Formula:** Close(t) - Close(t-1)
- **Meaning:** Absolute day-over-day price change.
- **Interpretation:** Positive = price rose today; negative = price fell.
- **Recommended for:** Machine Learning, Time Series
- **Advantages:** Simple, interpretable.
- **Limitations:** Not scale-invariant across tickers/time — use pct_return for comparisons.
- **When to use:** Feature for models trained on a single ticker over a stable price range.

### `pct_return`  _(Priority: High)_
- **Formula:** (Close(t) - Close(t-1)) / Close(t-1)
- **Meaning:** Percentage day-over-day return.
- **Interpretation:** Scale-invariant version of daily_return; comparable across tickers/time.
- **Recommended for:** Machine Learning, Time Series, Deep Learning
- **Advantages:** Stationary-ish, comparable across price levels.
- **Limitations:** Can be noisy for low-priced/illiquid tickers.
- **When to use:** Default target/feature basis for return-based modeling.

### `log_return`  _(Priority: High)_
- **Formula:** ln(Close(t) / Close(t-1))
- **Meaning:** Log return; approximately additive over time (log_return sums across days approximate the multi-day log return).
- **Interpretation:** Near-zero = flat; symmetric around 0 for up/down moves of similar magnitude.
- **Recommended for:** Time Series, Deep Learning
- **Advantages:** Time-additive, closer to normally distributed than raw pct returns; preferred by ARIMA/DL.
- **Limitations:** Less intuitive to read directly than pct_return.
- **When to use:** Time series models (ARIMA/SARIMA) and DL sequence inputs.

### `price_diff`  _(Priority: Medium)_
- **Formula:** Close - Open
- **Meaning:** Intraday price change.
- **Interpretation:** Positive = the session closed above where it opened (net buying pressure that day).
- **Recommended for:** Machine Learning

### `open_close_diff`  _(Priority: Low)_
- **Formula:** Close - Open
- **Meaning:** Alias of price_diff, kept as a distinct named column per spec for readability in reports.
- **Interpretation:** Same as price_diff.
- **Recommended for:** Machine Learning

### `high_low_diff`  _(Priority: Medium)_
- **Formula:** High - Low
- **Meaning:** Intraday trading range (absolute).
- **Interpretation:** Larger values indicate a more volatile session.
- **Recommended for:** Machine Learning, Decision Engine
- **When to use:** Cheap proxy for intraday volatility alongside ATR.

### `typical_price`  _(Priority: Medium)_
- **Formula:** (High + Low + Close) / 3
- **Meaning:** A single representative price for the session, weighting close, high and low equally.
- **Interpretation:** Commonly used as the input series for VWAP/CCI-style indicators.
- **Recommended for:** Machine Learning, Time Series

### `median_price`  _(Priority: Low)_
- **Formula:** (High + Low) / 2
- **Meaning:** Midpoint of the day's range, ignoring open/close.
- **Interpretation:** A smoother range-center reference than close alone.
- **Recommended for:** Machine Learning

### `weighted_close`  _(Priority: Low)_
- **Formula:** (High + Low + 2*Close) / 4
- **Meaning:** Typical price with double weight on the close.
- **Interpretation:** Emphasizes the closing price, which usually carries the most information.
- **Recommended for:** Machine Learning

## trend
### `sma_5`  _(Priority: Medium)_
- **Formula:** mean(Close, last 5 days)
- **Meaning:** 5-day Simple Moving Average.
- **Interpretation:** Price above SMA = uptrend bias; below = downtrend bias. Longer windows = smoother, laggier.
- **Recommended for:** Machine Learning, Time Series, Decision Engine
- **Advantages:** Simple, robust, widely understood baseline trend measure.
- **Limitations:** Lags price by ~2 days; whipsaws in sideways markets.
- **When to use:** Trend-following features, crossover signals (see golden_cross/death_cross).

### `sma_10`  _(Priority: Medium)_
- **Formula:** mean(Close, last 10 days)
- **Meaning:** 10-day Simple Moving Average.
- **Interpretation:** Price above SMA = uptrend bias; below = downtrend bias. Longer windows = smoother, laggier.
- **Recommended for:** Machine Learning, Time Series, Decision Engine
- **Advantages:** Simple, robust, widely understood baseline trend measure.
- **Limitations:** Lags price by ~5 days; whipsaws in sideways markets.
- **When to use:** Trend-following features, crossover signals (see golden_cross/death_cross).

### `sma_20`  _(Priority: High)_
- **Formula:** mean(Close, last 20 days)
- **Meaning:** 20-day Simple Moving Average.
- **Interpretation:** Price above SMA = uptrend bias; below = downtrend bias. Longer windows = smoother, laggier.
- **Recommended for:** Machine Learning, Time Series, Decision Engine
- **Advantages:** Simple, robust, widely understood baseline trend measure.
- **Limitations:** Lags price by ~10 days; whipsaws in sideways markets.
- **When to use:** Trend-following features, crossover signals (see golden_cross/death_cross).

### `sma_50`  _(Priority: High)_
- **Formula:** mean(Close, last 50 days)
- **Meaning:** 50-day Simple Moving Average.
- **Interpretation:** Price above SMA = uptrend bias; below = downtrend bias. Longer windows = smoother, laggier.
- **Recommended for:** Machine Learning, Time Series, Decision Engine
- **Advantages:** Simple, robust, widely understood baseline trend measure.
- **Limitations:** Lags price by ~25 days; whipsaws in sideways markets.
- **When to use:** Trend-following features, crossover signals (see golden_cross/death_cross).

### `sma_100`  _(Priority: Medium)_
- **Formula:** mean(Close, last 100 days)
- **Meaning:** 100-day Simple Moving Average.
- **Interpretation:** Price above SMA = uptrend bias; below = downtrend bias. Longer windows = smoother, laggier.
- **Recommended for:** Machine Learning, Time Series, Decision Engine
- **Advantages:** Simple, robust, widely understood baseline trend measure.
- **Limitations:** Lags price by ~50 days; whipsaws in sideways markets.
- **When to use:** Trend-following features, crossover signals (see golden_cross/death_cross).

### `sma_200`  _(Priority: High)_
- **Formula:** mean(Close, last 200 days)
- **Meaning:** 200-day Simple Moving Average.
- **Interpretation:** Price above SMA = uptrend bias; below = downtrend bias. Longer windows = smoother, laggier.
- **Recommended for:** Machine Learning, Time Series, Decision Engine
- **Advantages:** Simple, robust, widely understood baseline trend measure.
- **Limitations:** Lags price by ~100 days; whipsaws in sideways markets.
- **When to use:** Trend-following features, crossover signals (see golden_cross/death_cross).

### `ema_5`  _(Priority: Medium)_
- **Formula:** EWMA(Close, span=5)
- **Meaning:** 5-day Exponential Moving Average.
- **Interpretation:** Reacts faster to recent price changes than the equivalent SMA.
- **Recommended for:** Machine Learning, Deep Learning, Decision Engine
- **Advantages:** More responsive to new information than SMA; underlies MACD.
- **Limitations:** More sensitive to short-term noise/whipsaws than SMA.
- **When to use:** Faster trend signal, or as an input to MACD-style features.

### `ema_10`  _(Priority: Medium)_
- **Formula:** EWMA(Close, span=10)
- **Meaning:** 10-day Exponential Moving Average.
- **Interpretation:** Reacts faster to recent price changes than the equivalent SMA.
- **Recommended for:** Machine Learning, Deep Learning, Decision Engine
- **Advantages:** More responsive to new information than SMA; underlies MACD.
- **Limitations:** More sensitive to short-term noise/whipsaws than SMA.
- **When to use:** Faster trend signal, or as an input to MACD-style features.

### `ema_20`  _(Priority: High)_
- **Formula:** EWMA(Close, span=20)
- **Meaning:** 20-day Exponential Moving Average.
- **Interpretation:** Reacts faster to recent price changes than the equivalent SMA.
- **Recommended for:** Machine Learning, Deep Learning, Decision Engine
- **Advantages:** More responsive to new information than SMA; underlies MACD.
- **Limitations:** More sensitive to short-term noise/whipsaws than SMA.
- **When to use:** Faster trend signal, or as an input to MACD-style features.

### `ema_50`  _(Priority: High)_
- **Formula:** EWMA(Close, span=50)
- **Meaning:** 50-day Exponential Moving Average.
- **Interpretation:** Reacts faster to recent price changes than the equivalent SMA.
- **Recommended for:** Machine Learning, Deep Learning, Decision Engine
- **Advantages:** More responsive to new information than SMA; underlies MACD.
- **Limitations:** More sensitive to short-term noise/whipsaws than SMA.
- **When to use:** Faster trend signal, or as an input to MACD-style features.

### `ema_100`  _(Priority: Medium)_
- **Formula:** EWMA(Close, span=100)
- **Meaning:** 100-day Exponential Moving Average.
- **Interpretation:** Reacts faster to recent price changes than the equivalent SMA.
- **Recommended for:** Machine Learning, Deep Learning, Decision Engine
- **Advantages:** More responsive to new information than SMA; underlies MACD.
- **Limitations:** More sensitive to short-term noise/whipsaws than SMA.
- **When to use:** Faster trend signal, or as an input to MACD-style features.

### `ema_200`  _(Priority: Medium)_
- **Formula:** EWMA(Close, span=200)
- **Meaning:** 200-day Exponential Moving Average.
- **Interpretation:** Reacts faster to recent price changes than the equivalent SMA.
- **Recommended for:** Machine Learning, Deep Learning, Decision Engine
- **Advantages:** More responsive to new information than SMA; underlies MACD.
- **Limitations:** More sensitive to short-term noise/whipsaws than SMA.
- **When to use:** Faster trend signal, or as an input to MACD-style features.

### `golden_cross`  _(Priority: High)_
- **Formula:** sma_50 crosses above sma_200
- **Meaning:** Bullish long-term trend-change signal (classically 50-day crossing above 200-day).
- **Interpretation:** True on the single day the fast SMA first exceeds the slow SMA.
- **Recommended for:** Decision Engine, Machine Learning
- **Advantages:** Well-known, widely referenced signal; easy to explain to end users.
- **Limitations:** Lagging by construction (needs the crossover to already happen); frequent false signals in choppy markets.
- **When to use:** Long-horizon regime/trend-change feature, not short-term timing.

### `death_cross`  _(Priority: High)_
- **Formula:** sma_50 crosses below sma_200
- **Meaning:** Bearish long-term trend-change signal.
- **Interpretation:** True on the single day the fast SMA first drops below the slow SMA.
- **Recommended for:** Decision Engine, Machine Learning
- **Limitations:** Same lag/false-signal caveats as golden_cross.
- **When to use:** Long-horizon regime/trend-change feature.

## momentum
### `rsi`  _(Priority: High)_
- **Formula:** 100 - 100/(1 + RS), RS = Wilder-smoothed avg gain / avg loss over 14 days
- **Meaning:** Relative Strength Index — bounded 0-100 momentum oscillator.
- **Interpretation:** Traditionally >70 = overbought, <30 = oversold; divergence from price can signal reversals.
- **Recommended for:** Machine Learning, Decision Engine
- **Advantages:** Bounded scale makes it comparable across tickers/time; well-studied.
- **Limitations:** Can stay 'overbought'/'oversold' for extended periods in strong trends (false signals).
- **When to use:** Overbought/oversold screening; confirming momentum alongside MACD.

### `roc`  _(Priority: Medium)_
- **Formula:** (Close(t) - Close(t-12)) / Close(t-12) * 100
- **Meaning:** Rate of Change — percentage price change over the lookback period.
- **Interpretation:** Positive and rising = accelerating upward momentum.
- **Recommended for:** Machine Learning, Time Series
- **When to use:** Momentum feature comparable in scale across tickers.

### `momentum`  _(Priority: Medium)_
- **Formula:** Close(t) - Close(t-10)
- **Meaning:** Absolute price momentum over the lookback period.
- **Interpretation:** Magnitude and direction of the recent price move.
- **Recommended for:** Machine Learning
- **Limitations:** Not scale-invariant across tickers — prefer roc/price_momentum for cross-ticker models.

### `price_momentum`  _(Priority: Medium)_
- **Formula:** pct_change(Close, 10)
- **Meaning:** Percentage version of `momentum`.
- **Interpretation:** Scale-invariant momentum measure.
- **Recommended for:** Machine Learning, Deep Learning

### `volume_momentum`  _(Priority: Medium)_
- **Formula:** Volume(t) - Volume(t-10)
- **Meaning:** Change in trading volume over the lookback period.
- **Interpretation:** Rising volume momentum alongside price momentum supports trend conviction.
- **Recommended for:** Machine Learning, Decision Engine
- **When to use:** Confirming price moves with participation (volume) — see also breakout features.

## volatility
### `true_range`  _(Priority: Medium)_
- **Formula:** max(High-Low, |High-PrevClose|, |Low-PrevClose|)
- **Meaning:** The full price range a bar covered, including any gap from the prior close.
- **Interpretation:** Larger values indicate a more volatile session, including overnight gaps.
- **Recommended for:** Machine Learning, Decision Engine
- **When to use:** Building block for ATR; on its own, a per-bar volatility snapshot.

### `atr`  _(Priority: High)_
- **Formula:** Wilder EMA(true_range, period=14)
- **Meaning:** Average True Range — smoothed measure of typical daily trading range.
- **Interpretation:** Rising ATR = expanding volatility regime; commonly used to size stop-losses.
- **Recommended for:** Machine Learning, Decision Engine
- **Advantages:** Captures gap risk (unlike a plain High-Low range); industry-standard.
- **Limitations:** Lagging (smoothed); doesn't indicate direction, only magnitude.
- **When to use:** Risk/position-sizing features, volatility-regime detection.

### `historical_volatility`  _(Priority: High)_
- **Formula:** std(log_return, 20d) * sqrt(252)
- **Meaning:** Annualized historical volatility from log returns.
- **Interpretation:** Directly comparable across tickers and to option-implied volatility.
- **Recommended for:** Machine Learning, Decision Engine, Time Series
- **When to use:** Risk scoring, cross-ticker volatility comparison.

### `rolling_volatility_10`  _(Priority: Medium)_
- **Formula:** std(pct_return, last 10 days)
- **Meaning:** 10-day rolling standard deviation of daily percentage returns.
- **Interpretation:** Higher = choppier recent price action.
- **Recommended for:** Machine Learning, Deep Learning

### `rolling_volatility_20`  _(Priority: Medium)_
- **Formula:** std(pct_return, last 20 days)
- **Meaning:** 20-day rolling standard deviation of daily percentage returns.
- **Interpretation:** Higher = choppier recent price action.
- **Recommended for:** Machine Learning, Deep Learning

### `rolling_volatility_30`  _(Priority: Medium)_
- **Formula:** std(pct_return, last 30 days)
- **Meaning:** 30-day rolling standard deviation of daily percentage returns.
- **Interpretation:** Higher = choppier recent price action.
- **Recommended for:** Machine Learning, Deep Learning

### `std_10`  _(Priority: Low)_
- **Formula:** std(Close, last 10 days)
- **Meaning:** 10-day rolling standard deviation of raw closing price.
- **Interpretation:** Price-level dependent (not scale-invariant) — prefer rolling_volatility_* for cross-ticker comparisons.
- **Recommended for:** Machine Learning
- **Limitations:** Scale depends on the ticker's price level.

### `variance_10`  _(Priority: Low)_
- **Formula:** var(Close, last 10 days)
- **Meaning:** 10-day rolling variance of raw closing price (std_10 squared).
- **Interpretation:** Same information as std, in squared units.
- **Recommended for:** Machine Learning

### `std_20`  _(Priority: Low)_
- **Formula:** std(Close, last 20 days)
- **Meaning:** 20-day rolling standard deviation of raw closing price.
- **Interpretation:** Price-level dependent (not scale-invariant) — prefer rolling_volatility_* for cross-ticker comparisons.
- **Recommended for:** Machine Learning
- **Limitations:** Scale depends on the ticker's price level.

### `variance_20`  _(Priority: Low)_
- **Formula:** var(Close, last 20 days)
- **Meaning:** 20-day rolling variance of raw closing price (std_20 squared).
- **Interpretation:** Same information as std, in squared units.
- **Recommended for:** Machine Learning

## bollinger
### `bollinger_middle`  _(Priority: Medium)_
- **Formula:** SMA(Close, 20)
- **Meaning:** Center line of the Bollinger Bands.
- **Interpretation:** Same as sma_20 by default; the trend baseline the bands are drawn around.
- **Recommended for:** Machine Learning, Decision Engine

### `bollinger_upper`  _(Priority: High)_
- **Formula:** middle + 2.0*std(Close, 20)
- **Meaning:** Upper volatility band.
- **Interpretation:** Price reaching/exceeding this band suggests a statistically stretched move.
- **Recommended for:** Machine Learning, Decision Engine

### `bollinger_lower`  _(Priority: High)_
- **Formula:** middle - 2.0*std(Close, 20)
- **Meaning:** Lower volatility band.
- **Interpretation:** Price reaching/exceeding this band suggests a statistically stretched downside move.
- **Recommended for:** Machine Learning, Decision Engine

### `bollinger_bandwidth`  _(Priority: High)_
- **Formula:** (upper - lower) / middle
- **Meaning:** Normalized band width — a direct volatility measure.
- **Interpretation:** A tight bandwidth ('squeeze') often precedes a sharp directional move.
- **Recommended for:** Machine Learning, Decision Engine
- **When to use:** Volatility-regime / breakout-anticipation feature.

### `bollinger_percent_b`  _(Priority: High)_
- **Formula:** (Close - lower) / (upper - lower)
- **Meaning:** Where price sits within the bands, normalized 0-1 (can exceed the range on breakouts).
- **Interpretation:** %B near 1 = near the upper band; near 0 = near the lower band; >1 or <0 = outside the bands.
- **Recommended for:** Machine Learning, Decision Engine
- **Limitations:** Undefined (NaN) when the bands have zero width (flat price); guarded against divide-by-zero.

## macd
### `macd_line`  _(Priority: High)_
- **Formula:** EMA(Close, 12) - EMA(Close, 26)
- **Meaning:** Difference between the fast and slow EMA.
- **Interpretation:** Positive = fast EMA above slow EMA (bullish momentum); negative = bearish momentum.
- **Recommended for:** Machine Learning, Decision Engine
- **Advantages:** Combines trend and momentum in one line; widely used and well understood.
- **Limitations:** Lagging (built from EMAs); less useful in strongly sideways/choppy markets.
- **When to use:** Trend-momentum confirmation alongside RSI.

### `macd_signal`  _(Priority: High)_
- **Formula:** EMA(macd_line, 9)
- **Meaning:** Smoothed trigger line for the MACD line.
- **Interpretation:** Crossovers of macd_line above/below macd_signal are classic buy/sell triggers.
- **Recommended for:** Machine Learning, Decision Engine

### `macd_histogram`  _(Priority: High)_
- **Formula:** macd_line - macd_signal
- **Meaning:** Distance between the MACD line and its signal line.
- **Interpretation:** Sign shows which side of the crossover price is on; magnitude shows momentum strength; shrinking histogram often precedes a crossover.
- **Recommended for:** Machine Learning, Deep Learning, Decision Engine
- **When to use:** Early-warning feature for upcoming MACD crossovers.

## volume
### `volume_rolling_mean_10`  _(Priority: Medium)_
- **Formula:** mean(Volume, last 10 days)
- **Meaning:** 10-day average trading volume.
- **Interpretation:** Baseline 'normal' volume for the ticker; compare current volume against it.
- **Recommended for:** Machine Learning, Decision Engine

### `volume_rolling_std_10`  _(Priority: Low)_
- **Formula:** std(Volume, last 10 days)
- **Meaning:** 10-day volume volatility.
- **Interpretation:** High values indicate erratic/event-driven trading activity.
- **Recommended for:** Machine Learning

### `volume_rolling_mean_20`  _(Priority: Medium)_
- **Formula:** mean(Volume, last 20 days)
- **Meaning:** 20-day average trading volume.
- **Interpretation:** Baseline 'normal' volume for the ticker; compare current volume against it.
- **Recommended for:** Machine Learning, Decision Engine

### `volume_rolling_std_20`  _(Priority: Low)_
- **Formula:** std(Volume, last 20 days)
- **Meaning:** 20-day volume volatility.
- **Interpretation:** High values indicate erratic/event-driven trading activity.
- **Recommended for:** Machine Learning

### `volume_change`  _(Priority: Medium)_
- **Formula:** pct_change(Volume, 1)
- **Meaning:** Day-over-day percentage change in volume.
- **Interpretation:** Spikes often coincide with news/earnings events.
- **Recommended for:** Machine Learning, Decision Engine

### `volume_ratio`  _(Priority: High)_
- **Formula:** Volume(t) / volume_rolling_mean_10
- **Meaning:** Today's volume relative to its recent average.
- **Interpretation:** Ratio > 1.5-2x is commonly used as a 'high conviction' participation threshold (see breakout features).
- **Recommended for:** Machine Learning, Decision Engine

### `vwap`  _(Priority: Medium)_
- **Formula:** cumsum(typical_price * Volume) / cumsum(Volume)
- **Meaning:** Volume-Weighted Average Price, cumulative from the start of the loaded series.
- **Interpretation:** Price above VWAP suggests buyers are in control on average; a common institutional execution benchmark.
- **Recommended for:** Machine Learning, Decision Engine
- **Limitations:** Cumulative-from-series-start VWAP is most meaningful intraday; for daily bars, treat it as a long-run reference line rather than a session VWAP.
- **When to use:** Reference level for whether current price is 'expensive' or 'cheap' relative to volume-weighted history.

### `obv`  _(Priority: Medium)_
- **Formula:** cumsum(sign(Close change) * Volume)
- **Meaning:** On-Balance Volume — running total that adds volume on up days and subtracts it on down days.
- **Interpretation:** Rising OBV alongside rising price confirms the trend; OBV diverging from price can flag weakening trends.
- **Recommended for:** Machine Learning, Decision Engine
- **Limitations:** A cumulative indicator — its absolute level is arbitrary; only its slope/divergence from price is meaningful.

## rolling
### `rolling_mean_5`  _(Priority: Medium)_
- **Formula:** average(Close, last 5 days)
- **Meaning:** Rolling 5-day average of closing price.
- **Interpretation:** General-purpose descriptive statistic; combined with the current close it lets a model infer relative positioning cheaply.
- **Recommended for:** Machine Learning
- **When to use:** Feed as raw model-agnostic inputs to tree-based ML (Random Forest / XGBoost), which can learn nonlinear combinations on its own.

### `rolling_median_5`  _(Priority: Low)_
- **Formula:** median(Close, last 5 days)
- **Meaning:** Rolling 5-day median of closing price.
- **Interpretation:** General-purpose descriptive statistic; combined with the current close it lets a model infer relative positioning cheaply.
- **Recommended for:** Machine Learning
- **When to use:** Feed as raw model-agnostic inputs to tree-based ML (Random Forest / XGBoost), which can learn nonlinear combinations on its own.

### `rolling_max_5`  _(Priority: Low)_
- **Formula:** maximum(Close, last 5 days)
- **Meaning:** Rolling 5-day maximum of closing price.
- **Interpretation:** General-purpose descriptive statistic; combined with the current close it lets a model infer relative positioning cheaply.
- **Recommended for:** Machine Learning
- **When to use:** Feed as raw model-agnostic inputs to tree-based ML (Random Forest / XGBoost), which can learn nonlinear combinations on its own.

### `rolling_min_5`  _(Priority: Low)_
- **Formula:** minimum(Close, last 5 days)
- **Meaning:** Rolling 5-day minimum of closing price.
- **Interpretation:** General-purpose descriptive statistic; combined with the current close it lets a model infer relative positioning cheaply.
- **Recommended for:** Machine Learning
- **When to use:** Feed as raw model-agnostic inputs to tree-based ML (Random Forest / XGBoost), which can learn nonlinear combinations on its own.

### `rolling_std_5`  _(Priority: Medium)_
- **Formula:** standard deviation(Close, last 5 days)
- **Meaning:** Rolling 5-day standard deviation of closing price.
- **Interpretation:** General-purpose descriptive statistic; combined with the current close it lets a model infer relative positioning cheaply.
- **Recommended for:** Machine Learning
- **When to use:** Feed as raw model-agnostic inputs to tree-based ML (Random Forest / XGBoost), which can learn nonlinear combinations on its own.

### `rolling_var_5`  _(Priority: Low)_
- **Formula:** variance(Close, last 5 days)
- **Meaning:** Rolling 5-day variance of closing price.
- **Interpretation:** General-purpose descriptive statistic; combined with the current close it lets a model infer relative positioning cheaply.
- **Recommended for:** Machine Learning
- **When to use:** Feed as raw model-agnostic inputs to tree-based ML (Random Forest / XGBoost), which can learn nonlinear combinations on its own.

### `rolling_mean_10`  _(Priority: Medium)_
- **Formula:** average(Close, last 10 days)
- **Meaning:** Rolling 10-day average of closing price.
- **Interpretation:** General-purpose descriptive statistic; combined with the current close it lets a model infer relative positioning cheaply.
- **Recommended for:** Machine Learning
- **When to use:** Feed as raw model-agnostic inputs to tree-based ML (Random Forest / XGBoost), which can learn nonlinear combinations on its own.

### `rolling_median_10`  _(Priority: Low)_
- **Formula:** median(Close, last 10 days)
- **Meaning:** Rolling 10-day median of closing price.
- **Interpretation:** General-purpose descriptive statistic; combined with the current close it lets a model infer relative positioning cheaply.
- **Recommended for:** Machine Learning
- **When to use:** Feed as raw model-agnostic inputs to tree-based ML (Random Forest / XGBoost), which can learn nonlinear combinations on its own.

### `rolling_max_10`  _(Priority: Low)_
- **Formula:** maximum(Close, last 10 days)
- **Meaning:** Rolling 10-day maximum of closing price.
- **Interpretation:** General-purpose descriptive statistic; combined with the current close it lets a model infer relative positioning cheaply.
- **Recommended for:** Machine Learning
- **When to use:** Feed as raw model-agnostic inputs to tree-based ML (Random Forest / XGBoost), which can learn nonlinear combinations on its own.

### `rolling_min_10`  _(Priority: Low)_
- **Formula:** minimum(Close, last 10 days)
- **Meaning:** Rolling 10-day minimum of closing price.
- **Interpretation:** General-purpose descriptive statistic; combined with the current close it lets a model infer relative positioning cheaply.
- **Recommended for:** Machine Learning
- **When to use:** Feed as raw model-agnostic inputs to tree-based ML (Random Forest / XGBoost), which can learn nonlinear combinations on its own.

### `rolling_std_10`  _(Priority: Medium)_
- **Formula:** standard deviation(Close, last 10 days)
- **Meaning:** Rolling 10-day standard deviation of closing price.
- **Interpretation:** General-purpose descriptive statistic; combined with the current close it lets a model infer relative positioning cheaply.
- **Recommended for:** Machine Learning
- **When to use:** Feed as raw model-agnostic inputs to tree-based ML (Random Forest / XGBoost), which can learn nonlinear combinations on its own.

### `rolling_var_10`  _(Priority: Low)_
- **Formula:** variance(Close, last 10 days)
- **Meaning:** Rolling 10-day variance of closing price.
- **Interpretation:** General-purpose descriptive statistic; combined with the current close it lets a model infer relative positioning cheaply.
- **Recommended for:** Machine Learning
- **When to use:** Feed as raw model-agnostic inputs to tree-based ML (Random Forest / XGBoost), which can learn nonlinear combinations on its own.

### `rolling_mean_20`  _(Priority: Medium)_
- **Formula:** average(Close, last 20 days)
- **Meaning:** Rolling 20-day average of closing price.
- **Interpretation:** General-purpose descriptive statistic; combined with the current close it lets a model infer relative positioning cheaply.
- **Recommended for:** Machine Learning
- **When to use:** Feed as raw model-agnostic inputs to tree-based ML (Random Forest / XGBoost), which can learn nonlinear combinations on its own.

### `rolling_median_20`  _(Priority: Low)_
- **Formula:** median(Close, last 20 days)
- **Meaning:** Rolling 20-day median of closing price.
- **Interpretation:** General-purpose descriptive statistic; combined with the current close it lets a model infer relative positioning cheaply.
- **Recommended for:** Machine Learning
- **When to use:** Feed as raw model-agnostic inputs to tree-based ML (Random Forest / XGBoost), which can learn nonlinear combinations on its own.

### `rolling_max_20`  _(Priority: Low)_
- **Formula:** maximum(Close, last 20 days)
- **Meaning:** Rolling 20-day maximum of closing price.
- **Interpretation:** General-purpose descriptive statistic; combined with the current close it lets a model infer relative positioning cheaply.
- **Recommended for:** Machine Learning
- **When to use:** Feed as raw model-agnostic inputs to tree-based ML (Random Forest / XGBoost), which can learn nonlinear combinations on its own.

### `rolling_min_20`  _(Priority: Low)_
- **Formula:** minimum(Close, last 20 days)
- **Meaning:** Rolling 20-day minimum of closing price.
- **Interpretation:** General-purpose descriptive statistic; combined with the current close it lets a model infer relative positioning cheaply.
- **Recommended for:** Machine Learning
- **When to use:** Feed as raw model-agnostic inputs to tree-based ML (Random Forest / XGBoost), which can learn nonlinear combinations on its own.

### `rolling_std_20`  _(Priority: Medium)_
- **Formula:** standard deviation(Close, last 20 days)
- **Meaning:** Rolling 20-day standard deviation of closing price.
- **Interpretation:** General-purpose descriptive statistic; combined with the current close it lets a model infer relative positioning cheaply.
- **Recommended for:** Machine Learning
- **When to use:** Feed as raw model-agnostic inputs to tree-based ML (Random Forest / XGBoost), which can learn nonlinear combinations on its own.

### `rolling_var_20`  _(Priority: Low)_
- **Formula:** variance(Close, last 20 days)
- **Meaning:** Rolling 20-day variance of closing price.
- **Interpretation:** General-purpose descriptive statistic; combined with the current close it lets a model infer relative positioning cheaply.
- **Recommended for:** Machine Learning
- **When to use:** Feed as raw model-agnostic inputs to tree-based ML (Random Forest / XGBoost), which can learn nonlinear combinations on its own.

## lag
### `close_lag_1`  _(Priority: High)_
- **Formula:** Close(t - 1)
- **Meaning:** Close value from 1 day(s) ago.
- **Interpretation:** Gives non-sequential models (e.g. Random Forest) direct access to recent history.
- **Recommended for:** Machine Learning
- **Limitations:** Redundant for LSTM/GRU, which already consume sequences (FR-5.4) — only needed for non-sequential models.
- **When to use:** Tabular ML models (Random Forest, XGBoost, Linear Regression).

### `close_lag_2`  _(Priority: High)_
- **Formula:** Close(t - 2)
- **Meaning:** Close value from 2 day(s) ago.
- **Interpretation:** Gives non-sequential models (e.g. Random Forest) direct access to recent history.
- **Recommended for:** Machine Learning
- **Limitations:** Redundant for LSTM/GRU, which already consume sequences (FR-5.4) — only needed for non-sequential models.
- **When to use:** Tabular ML models (Random Forest, XGBoost, Linear Regression).

### `close_lag_3`  _(Priority: High)_
- **Formula:** Close(t - 3)
- **Meaning:** Close value from 3 day(s) ago.
- **Interpretation:** Gives non-sequential models (e.g. Random Forest) direct access to recent history.
- **Recommended for:** Machine Learning
- **Limitations:** Redundant for LSTM/GRU, which already consume sequences (FR-5.4) — only needed for non-sequential models.
- **When to use:** Tabular ML models (Random Forest, XGBoost, Linear Regression).

### `close_lag_5`  _(Priority: Medium)_
- **Formula:** Close(t - 5)
- **Meaning:** Close value from 5 day(s) ago.
- **Interpretation:** Gives non-sequential models (e.g. Random Forest) direct access to recent history.
- **Recommended for:** Machine Learning
- **Limitations:** Redundant for LSTM/GRU, which already consume sequences (FR-5.4) — only needed for non-sequential models.
- **When to use:** Tabular ML models (Random Forest, XGBoost, Linear Regression).

### `close_lag_10`  _(Priority: Medium)_
- **Formula:** Close(t - 10)
- **Meaning:** Close value from 10 day(s) ago.
- **Interpretation:** Gives non-sequential models (e.g. Random Forest) direct access to recent history.
- **Recommended for:** Machine Learning
- **Limitations:** Redundant for LSTM/GRU, which already consume sequences (FR-5.4) — only needed for non-sequential models.
- **When to use:** Tabular ML models (Random Forest, XGBoost, Linear Regression).

### `close_lag_20`  _(Priority: Medium)_
- **Formula:** Close(t - 20)
- **Meaning:** Close value from 20 day(s) ago.
- **Interpretation:** Gives non-sequential models (e.g. Random Forest) direct access to recent history.
- **Recommended for:** Machine Learning
- **Limitations:** Redundant for LSTM/GRU, which already consume sequences (FR-5.4) — only needed for non-sequential models.
- **When to use:** Tabular ML models (Random Forest, XGBoost, Linear Regression).

### `open_lag_1`  _(Priority: High)_
- **Formula:** Open(t - 1)
- **Meaning:** Open value from 1 day(s) ago.
- **Interpretation:** Gives non-sequential models (e.g. Random Forest) direct access to recent history.
- **Recommended for:** Machine Learning
- **Limitations:** Redundant for LSTM/GRU, which already consume sequences (FR-5.4) — only needed for non-sequential models.
- **When to use:** Tabular ML models (Random Forest, XGBoost, Linear Regression).

### `open_lag_2`  _(Priority: High)_
- **Formula:** Open(t - 2)
- **Meaning:** Open value from 2 day(s) ago.
- **Interpretation:** Gives non-sequential models (e.g. Random Forest) direct access to recent history.
- **Recommended for:** Machine Learning
- **Limitations:** Redundant for LSTM/GRU, which already consume sequences (FR-5.4) — only needed for non-sequential models.
- **When to use:** Tabular ML models (Random Forest, XGBoost, Linear Regression).

### `open_lag_3`  _(Priority: High)_
- **Formula:** Open(t - 3)
- **Meaning:** Open value from 3 day(s) ago.
- **Interpretation:** Gives non-sequential models (e.g. Random Forest) direct access to recent history.
- **Recommended for:** Machine Learning
- **Limitations:** Redundant for LSTM/GRU, which already consume sequences (FR-5.4) — only needed for non-sequential models.
- **When to use:** Tabular ML models (Random Forest, XGBoost, Linear Regression).

### `open_lag_5`  _(Priority: Medium)_
- **Formula:** Open(t - 5)
- **Meaning:** Open value from 5 day(s) ago.
- **Interpretation:** Gives non-sequential models (e.g. Random Forest) direct access to recent history.
- **Recommended for:** Machine Learning
- **Limitations:** Redundant for LSTM/GRU, which already consume sequences (FR-5.4) — only needed for non-sequential models.
- **When to use:** Tabular ML models (Random Forest, XGBoost, Linear Regression).

### `open_lag_10`  _(Priority: Medium)_
- **Formula:** Open(t - 10)
- **Meaning:** Open value from 10 day(s) ago.
- **Interpretation:** Gives non-sequential models (e.g. Random Forest) direct access to recent history.
- **Recommended for:** Machine Learning
- **Limitations:** Redundant for LSTM/GRU, which already consume sequences (FR-5.4) — only needed for non-sequential models.
- **When to use:** Tabular ML models (Random Forest, XGBoost, Linear Regression).

### `open_lag_20`  _(Priority: Medium)_
- **Formula:** Open(t - 20)
- **Meaning:** Open value from 20 day(s) ago.
- **Interpretation:** Gives non-sequential models (e.g. Random Forest) direct access to recent history.
- **Recommended for:** Machine Learning
- **Limitations:** Redundant for LSTM/GRU, which already consume sequences (FR-5.4) — only needed for non-sequential models.
- **When to use:** Tabular ML models (Random Forest, XGBoost, Linear Regression).

### `high_lag_1`  _(Priority: High)_
- **Formula:** High(t - 1)
- **Meaning:** High value from 1 day(s) ago.
- **Interpretation:** Gives non-sequential models (e.g. Random Forest) direct access to recent history.
- **Recommended for:** Machine Learning
- **Limitations:** Redundant for LSTM/GRU, which already consume sequences (FR-5.4) — only needed for non-sequential models.
- **When to use:** Tabular ML models (Random Forest, XGBoost, Linear Regression).

### `high_lag_2`  _(Priority: High)_
- **Formula:** High(t - 2)
- **Meaning:** High value from 2 day(s) ago.
- **Interpretation:** Gives non-sequential models (e.g. Random Forest) direct access to recent history.
- **Recommended for:** Machine Learning
- **Limitations:** Redundant for LSTM/GRU, which already consume sequences (FR-5.4) — only needed for non-sequential models.
- **When to use:** Tabular ML models (Random Forest, XGBoost, Linear Regression).

### `high_lag_3`  _(Priority: High)_
- **Formula:** High(t - 3)
- **Meaning:** High value from 3 day(s) ago.
- **Interpretation:** Gives non-sequential models (e.g. Random Forest) direct access to recent history.
- **Recommended for:** Machine Learning
- **Limitations:** Redundant for LSTM/GRU, which already consume sequences (FR-5.4) — only needed for non-sequential models.
- **When to use:** Tabular ML models (Random Forest, XGBoost, Linear Regression).

### `high_lag_5`  _(Priority: Medium)_
- **Formula:** High(t - 5)
- **Meaning:** High value from 5 day(s) ago.
- **Interpretation:** Gives non-sequential models (e.g. Random Forest) direct access to recent history.
- **Recommended for:** Machine Learning
- **Limitations:** Redundant for LSTM/GRU, which already consume sequences (FR-5.4) — only needed for non-sequential models.
- **When to use:** Tabular ML models (Random Forest, XGBoost, Linear Regression).

### `high_lag_10`  _(Priority: Medium)_
- **Formula:** High(t - 10)
- **Meaning:** High value from 10 day(s) ago.
- **Interpretation:** Gives non-sequential models (e.g. Random Forest) direct access to recent history.
- **Recommended for:** Machine Learning
- **Limitations:** Redundant for LSTM/GRU, which already consume sequences (FR-5.4) — only needed for non-sequential models.
- **When to use:** Tabular ML models (Random Forest, XGBoost, Linear Regression).

### `high_lag_20`  _(Priority: Medium)_
- **Formula:** High(t - 20)
- **Meaning:** High value from 20 day(s) ago.
- **Interpretation:** Gives non-sequential models (e.g. Random Forest) direct access to recent history.
- **Recommended for:** Machine Learning
- **Limitations:** Redundant for LSTM/GRU, which already consume sequences (FR-5.4) — only needed for non-sequential models.
- **When to use:** Tabular ML models (Random Forest, XGBoost, Linear Regression).

### `low_lag_1`  _(Priority: High)_
- **Formula:** Low(t - 1)
- **Meaning:** Low value from 1 day(s) ago.
- **Interpretation:** Gives non-sequential models (e.g. Random Forest) direct access to recent history.
- **Recommended for:** Machine Learning
- **Limitations:** Redundant for LSTM/GRU, which already consume sequences (FR-5.4) — only needed for non-sequential models.
- **When to use:** Tabular ML models (Random Forest, XGBoost, Linear Regression).

### `low_lag_2`  _(Priority: High)_
- **Formula:** Low(t - 2)
- **Meaning:** Low value from 2 day(s) ago.
- **Interpretation:** Gives non-sequential models (e.g. Random Forest) direct access to recent history.
- **Recommended for:** Machine Learning
- **Limitations:** Redundant for LSTM/GRU, which already consume sequences (FR-5.4) — only needed for non-sequential models.
- **When to use:** Tabular ML models (Random Forest, XGBoost, Linear Regression).

### `low_lag_3`  _(Priority: High)_
- **Formula:** Low(t - 3)
- **Meaning:** Low value from 3 day(s) ago.
- **Interpretation:** Gives non-sequential models (e.g. Random Forest) direct access to recent history.
- **Recommended for:** Machine Learning
- **Limitations:** Redundant for LSTM/GRU, which already consume sequences (FR-5.4) — only needed for non-sequential models.
- **When to use:** Tabular ML models (Random Forest, XGBoost, Linear Regression).

### `low_lag_5`  _(Priority: Medium)_
- **Formula:** Low(t - 5)
- **Meaning:** Low value from 5 day(s) ago.
- **Interpretation:** Gives non-sequential models (e.g. Random Forest) direct access to recent history.
- **Recommended for:** Machine Learning
- **Limitations:** Redundant for LSTM/GRU, which already consume sequences (FR-5.4) — only needed for non-sequential models.
- **When to use:** Tabular ML models (Random Forest, XGBoost, Linear Regression).

### `low_lag_10`  _(Priority: Medium)_
- **Formula:** Low(t - 10)
- **Meaning:** Low value from 10 day(s) ago.
- **Interpretation:** Gives non-sequential models (e.g. Random Forest) direct access to recent history.
- **Recommended for:** Machine Learning
- **Limitations:** Redundant for LSTM/GRU, which already consume sequences (FR-5.4) — only needed for non-sequential models.
- **When to use:** Tabular ML models (Random Forest, XGBoost, Linear Regression).

### `low_lag_20`  _(Priority: Medium)_
- **Formula:** Low(t - 20)
- **Meaning:** Low value from 20 day(s) ago.
- **Interpretation:** Gives non-sequential models (e.g. Random Forest) direct access to recent history.
- **Recommended for:** Machine Learning
- **Limitations:** Redundant for LSTM/GRU, which already consume sequences (FR-5.4) — only needed for non-sequential models.
- **When to use:** Tabular ML models (Random Forest, XGBoost, Linear Regression).

### `volume_lag_1`  _(Priority: High)_
- **Formula:** Volume(t - 1)
- **Meaning:** Volume value from 1 day(s) ago.
- **Interpretation:** Gives non-sequential models (e.g. Random Forest) direct access to recent history.
- **Recommended for:** Machine Learning
- **Limitations:** Redundant for LSTM/GRU, which already consume sequences (FR-5.4) — only needed for non-sequential models.
- **When to use:** Tabular ML models (Random Forest, XGBoost, Linear Regression).

### `volume_lag_2`  _(Priority: High)_
- **Formula:** Volume(t - 2)
- **Meaning:** Volume value from 2 day(s) ago.
- **Interpretation:** Gives non-sequential models (e.g. Random Forest) direct access to recent history.
- **Recommended for:** Machine Learning
- **Limitations:** Redundant for LSTM/GRU, which already consume sequences (FR-5.4) — only needed for non-sequential models.
- **When to use:** Tabular ML models (Random Forest, XGBoost, Linear Regression).

### `volume_lag_3`  _(Priority: High)_
- **Formula:** Volume(t - 3)
- **Meaning:** Volume value from 3 day(s) ago.
- **Interpretation:** Gives non-sequential models (e.g. Random Forest) direct access to recent history.
- **Recommended for:** Machine Learning
- **Limitations:** Redundant for LSTM/GRU, which already consume sequences (FR-5.4) — only needed for non-sequential models.
- **When to use:** Tabular ML models (Random Forest, XGBoost, Linear Regression).

### `volume_lag_5`  _(Priority: Medium)_
- **Formula:** Volume(t - 5)
- **Meaning:** Volume value from 5 day(s) ago.
- **Interpretation:** Gives non-sequential models (e.g. Random Forest) direct access to recent history.
- **Recommended for:** Machine Learning
- **Limitations:** Redundant for LSTM/GRU, which already consume sequences (FR-5.4) — only needed for non-sequential models.
- **When to use:** Tabular ML models (Random Forest, XGBoost, Linear Regression).

### `volume_lag_10`  _(Priority: Medium)_
- **Formula:** Volume(t - 10)
- **Meaning:** Volume value from 10 day(s) ago.
- **Interpretation:** Gives non-sequential models (e.g. Random Forest) direct access to recent history.
- **Recommended for:** Machine Learning
- **Limitations:** Redundant for LSTM/GRU, which already consume sequences (FR-5.4) — only needed for non-sequential models.
- **When to use:** Tabular ML models (Random Forest, XGBoost, Linear Regression).

### `volume_lag_20`  _(Priority: Medium)_
- **Formula:** Volume(t - 20)
- **Meaning:** Volume value from 20 day(s) ago.
- **Interpretation:** Gives non-sequential models (e.g. Random Forest) direct access to recent history.
- **Recommended for:** Machine Learning
- **Limitations:** Redundant for LSTM/GRU, which already consume sequences (FR-5.4) — only needed for non-sequential models.
- **When to use:** Tabular ML models (Random Forest, XGBoost, Linear Regression).

### `return_lag_1`  _(Priority: High)_
- **Formula:** pct_return(t - 1)
- **Meaning:** Percentage return from 1 day(s) ago.
- **Interpretation:** Lets a model see recent return momentum/mean-reversion patterns directly.
- **Recommended for:** Machine Learning

### `return_lag_2`  _(Priority: High)_
- **Formula:** pct_return(t - 2)
- **Meaning:** Percentage return from 2 day(s) ago.
- **Interpretation:** Lets a model see recent return momentum/mean-reversion patterns directly.
- **Recommended for:** Machine Learning

### `return_lag_3`  _(Priority: High)_
- **Formula:** pct_return(t - 3)
- **Meaning:** Percentage return from 3 day(s) ago.
- **Interpretation:** Lets a model see recent return momentum/mean-reversion patterns directly.
- **Recommended for:** Machine Learning

### `return_lag_5`  _(Priority: Medium)_
- **Formula:** pct_return(t - 5)
- **Meaning:** Percentage return from 5 day(s) ago.
- **Interpretation:** Lets a model see recent return momentum/mean-reversion patterns directly.
- **Recommended for:** Machine Learning

### `return_lag_10`  _(Priority: Medium)_
- **Formula:** pct_return(t - 10)
- **Meaning:** Percentage return from 10 day(s) ago.
- **Interpretation:** Lets a model see recent return momentum/mean-reversion patterns directly.
- **Recommended for:** Machine Learning

### `return_lag_20`  _(Priority: Medium)_
- **Formula:** pct_return(t - 20)
- **Meaning:** Percentage return from 20 day(s) ago.
- **Interpretation:** Lets a model see recent return momentum/mean-reversion patterns directly.
- **Recommended for:** Machine Learning

## date
### `year`  _(Priority: Low)_
- **Formula:** Date.year
- **Meaning:** Calendar year.
- **Interpretation:** Lets a model learn long-run/macro regime effects.
- **Recommended for:** Machine Learning

### `quarter`  _(Priority: Low)_
- **Formula:** Date.quarter
- **Meaning:** Calendar quarter (1-4).
- **Interpretation:** Captures earnings-season/quarter-end effects.
- **Recommended for:** Machine Learning

### `month`  _(Priority: Low)_
- **Formula:** Date.month
- **Meaning:** Calendar month (1-12).
- **Interpretation:** Captures seasonal patterns (e.g. 'January effect').
- **Recommended for:** Machine Learning

### `week`  _(Priority: Low)_
- **Formula:** Date.isocalendar().week
- **Meaning:** ISO calendar week number.
- **Interpretation:** Finer-grained seasonality than month.
- **Recommended for:** Machine Learning

### `day`  _(Priority: Low)_
- **Formula:** Date.day
- **Meaning:** Day of month (1-31).
- **Interpretation:** Captures monthly cyclicality (e.g. payday effects).
- **Recommended for:** Machine Learning

### `day_of_week`  _(Priority: Medium)_
- **Formula:** Date.dayofweek (0=Mon)
- **Meaning:** Day of the trading week.
- **Interpretation:** Captures day-of-week effects (e.g. 'Monday effect').
- **Recommended for:** Machine Learning

### `is_month_end`  _(Priority: Low)_
- **Formula:** Date.is_month_end
- **Meaning:** True on the last calendar day of the month.
- **Interpretation:** Flags potential month-end rebalancing flow.
- **Recommended for:** Machine Learning

### `is_month_start`  _(Priority: Low)_
- **Formula:** Date.is_month_start
- **Meaning:** True on the first calendar day of the month.
- **Interpretation:** Flags potential start-of-month flow.
- **Recommended for:** Machine Learning

### `is_quarter_end`  _(Priority: Medium)_
- **Formula:** Date.is_quarter_end
- **Meaning:** True on the last calendar day of the quarter.
- **Interpretation:** Flags potential quarter-end/earnings-adjacent effects.
- **Recommended for:** Machine Learning, Decision Engine

## price_action
### `higher_high`  _(Priority: Medium)_
- **Formula:** High(t) > High(t-1)
- **Meaning:** Today's high exceeded yesterday's high.
- **Interpretation:** Building block of uptrend structure.
- **Recommended for:** Machine Learning, Decision Engine

### `higher_low`  _(Priority: Medium)_
- **Formula:** Low(t) > Low(t-1)
- **Meaning:** Today's low exceeded yesterday's low.
- **Interpretation:** Building block of uptrend structure.
- **Recommended for:** Machine Learning, Decision Engine

### `lower_high`  _(Priority: Medium)_
- **Formula:** High(t) < High(t-1)
- **Meaning:** Today's high is below yesterday's high.
- **Interpretation:** Building block of downtrend structure.
- **Recommended for:** Machine Learning, Decision Engine

### `lower_low`  _(Priority: Medium)_
- **Formula:** Low(t) < Low(t-1)
- **Meaning:** Today's low is below yesterday's low.
- **Interpretation:** Building block of downtrend structure.
- **Recommended for:** Machine Learning, Decision Engine

### `inside_bar`  _(Priority: Medium)_
- **Formula:** High(t)<High(t-1) and Low(t)>Low(t-1)
- **Meaning:** Today's range is fully contained within yesterday's range.
- **Interpretation:** Often signals consolidation/indecision before a breakout.
- **Recommended for:** Machine Learning, Decision Engine

### `outside_bar`  _(Priority: Medium)_
- **Formula:** High(t)>High(t-1) and Low(t)<Low(t-1)
- **Meaning:** Today's range fully engulfs yesterday's range.
- **Interpretation:** Signals a volatility expansion / potential reversal bar.
- **Recommended for:** Machine Learning, Decision Engine

### `is_doji`  _(Priority: Medium)_
- **Formula:** |Close-Open| <= 10% of (High-Low)
- **Meaning:** Open and close are nearly equal.
- **Interpretation:** Indecision; often precedes a reversal, especially after a strong trend.
- **Recommended for:** Machine Learning, Decision Engine

### `is_bullish_engulfing`  _(Priority: High)_
- **Formula:** Bearish candle followed by a bullish candle whose body engulfs it
- **Meaning:** Two-candle bullish reversal pattern.
- **Interpretation:** Stronger when it occurs after a downtrend / at support.
- **Recommended for:** Machine Learning, Decision Engine

### `is_bearish_engulfing`  _(Priority: High)_
- **Formula:** Bullish candle followed by a bearish candle whose body engulfs it
- **Meaning:** Two-candle bearish reversal pattern.
- **Interpretation:** Stronger when it occurs after an uptrend / at resistance.
- **Recommended for:** Machine Learning, Decision Engine

### `is_pin_bar`  _(Priority: Medium)_
- **Formula:** One wick >= 2x body and the opposite wick <= body
- **Meaning:** Long single-sided wick, small body/opposite wick.
- **Interpretation:** Rejection of price at the wick's extreme; potential reversal.
- **Recommended for:** Machine Learning, Decision Engine

### `is_hammer`  _(Priority: High)_
- **Formula:** Long lower wick >= 2x body, small/no upper wick
- **Meaning:** Bullish reversal candle after a decline.
- **Interpretation:** Buyers rejected lower prices within the session.
- **Recommended for:** Machine Learning, Decision Engine

### `is_shooting_star`  _(Priority: High)_
- **Formula:** Long upper wick >= 2x body, small/no lower wick
- **Meaning:** Bearish reversal candle after an advance.
- **Interpretation:** Sellers rejected higher prices within the session.
- **Recommended for:** Machine Learning, Decision Engine

### `is_marubozu`  _(Priority: Medium)_
- **Formula:** Wicks <= 5% of the candle's range on both ends
- **Meaning:** Full-bodied candle with virtually no wicks.
- **Interpretation:** Strong one-sided conviction for the full session.
- **Recommended for:** Machine Learning, Decision Engine

### `trend_strength`  _(Priority: Medium)_
- **Formula:** sign(Close-Open) * body / (High-Low)
- **Meaning:** Signed fraction of the day's range captured by the candle body.
- **Interpretation:** Near +1/-1 = strong directional conviction; near 0 = indecisive session.
- **Recommended for:** Machine Learning

### `swing_high`  _(Priority: High)_
- **Formula:** High(t) is the max High within +/-5 bars
- **Meaning:** Local price peak (fractal high).
- **Interpretation:** Used as pivot points for support/resistance and structure features.
- **Recommended for:** Machine Learning, Decision Engine
- **Limitations:** Repaints: only confirmed once the trailing lookback window of future bars exists.
- **When to use:** Offline feature engineering / backtesting, not real-time signal generation without an added lag.

### `swing_low`  _(Priority: High)_
- **Formula:** Low(t) is the min Low within +/-5 bars
- **Meaning:** Local price trough (fractal low).
- **Interpretation:** Used as pivot points for support/resistance and structure features.
- **Recommended for:** Machine Learning, Decision Engine
- **Limitations:** Repaints (see swing_high).
- **When to use:** Offline feature engineering / backtesting.

### `break_of_structure_up`  _(Priority: High)_
- **Formula:** Close(t) > most recent confirmed swing_high
- **Meaning:** Price broke above the last significant swing high.
- **Interpretation:** Continuation signal in an uptrend.
- **Recommended for:** Machine Learning, Decision Engine

### `break_of_structure_down`  _(Priority: High)_
- **Formula:** Close(t) < most recent confirmed swing_low
- **Meaning:** Price broke below the last significant swing low.
- **Interpretation:** Continuation signal in a downtrend.
- **Recommended for:** Machine Learning, Decision Engine

### `change_of_character`  _(Priority: High)_
- **Formula:** A break-of-structure opposite to the prevailing BOS direction
- **Meaning:** First structural break against the prevailing trend.
- **Interpretation:** Early warning of a potential trend reversal.
- **Recommended for:** Decision Engine, Machine Learning

### `price_action_label`  _(Priority: Medium)_
- **Formula:** first matching candlestick pattern in priority order, else 'None'
- **Meaning:** Single human-readable label summarizing today's candlestick pattern.
- **Interpretation:** Convenience categorical for reports/dashboards; the underlying boolean columns are more precise for modeling.
- **Recommended for:** Decision Engine

## support_resistance
### `static_support`  _(Priority: High)_
- **Formula:** min(Low, last 20 days)
- **Meaning:** Simple rolling floor of recent price action.
- **Interpretation:** A break below this level suggests the recent trading range has failed.
- **Recommended for:** Machine Learning, Decision Engine

### `static_resistance`  _(Priority: High)_
- **Formula:** max(High, last 20 days)
- **Meaning:** Simple rolling ceiling of recent price action.
- **Interpretation:** A break above this level suggests the recent trading range has failed to the upside.
- **Recommended for:** Machine Learning, Decision Engine

### `dynamic_support`  _(Priority: High)_
- **Formula:** Price of the most recent confirmed swing_low
- **Meaning:** Structure-based (fractal) support level.
- **Interpretation:** More reactive than static_support to the most recent meaningful pivot.
- **Recommended for:** Machine Learning, Decision Engine

### `dynamic_resistance`  _(Priority: High)_
- **Formula:** Price of the most recent confirmed swing_high
- **Meaning:** Structure-based (fractal) resistance level.
- **Interpretation:** More reactive than static_resistance to the most recent meaningful pivot.
- **Recommended for:** Machine Learning, Decision Engine

### `nearest_support`  _(Priority: High)_
- **Formula:** = dynamic_support
- **Meaning:** Alias exposed under the spec's requested column name.
- **Interpretation:** See dynamic_support.
- **Recommended for:** Machine Learning, Decision Engine

### `nearest_resistance`  _(Priority: High)_
- **Formula:** = dynamic_resistance
- **Meaning:** Alias exposed under the spec's requested column name.
- **Interpretation:** See dynamic_resistance.
- **Recommended for:** Machine Learning, Decision Engine

### `support_distance`  _(Priority: High)_
- **Formula:** (Close - nearest_support) / Close
- **Meaning:** Normalized distance from price to the nearest support.
- **Interpretation:** Small/near-zero = price is testing support right now (elevated bounce-or-break risk).
- **Recommended for:** Machine Learning, Decision Engine

### `resistance_distance`  _(Priority: High)_
- **Formula:** (nearest_resistance - Close) / Close
- **Meaning:** Normalized distance from price to the nearest resistance.
- **Interpretation:** Small/near-zero = price is testing resistance right now.
- **Recommended for:** Machine Learning, Decision Engine

### `swing_zone_width`  _(Priority: Medium)_
- **Formula:** (dynamic_resistance - dynamic_support) / Close
- **Meaning:** Width of the current support-resistance trading range, normalized by price.
- **Interpretation:** Narrow = tight range (potential breakout setup); wide = range-bound with room to move.
- **Recommended for:** Machine Learning, Decision Engine

### `demand_zone`  _(Priority: Medium)_
- **Formula:** swing_low followed by a strong up-move within the lookback window (see module docstring)
- **Meaning:** Origin bar of a fresh institutional-style demand (buy-side) zone.
- **Interpretation:** Price returning to this zone is expected to find buying interest.
- **Recommended for:** Machine Learning, Decision Engine
- **Limitations:** Heuristic, not a formally standardized indicator; forward-looking by construction (repaints).

### `supply_zone`  _(Priority: Medium)_
- **Formula:** swing_high followed by a strong down-move within the lookback window
- **Meaning:** Origin bar of a fresh supply (sell-side) zone.
- **Interpretation:** Price returning to this zone is expected to find selling interest.
- **Recommended for:** Machine Learning, Decision Engine
- **Limitations:** Heuristic; repaints (see demand_zone).

### `demand_zone_strength`  _(Priority: Medium)_
- **Formula:** Forward % move away from the demand zone origin
- **Meaning:** How strong the reaction away from the zone was.
- **Interpretation:** Larger = more significant zone.
- **Recommended for:** Machine Learning, Decision Engine

### `supply_zone_strength`  _(Priority: Medium)_
- **Formula:** Forward % move away from the supply zone origin
- **Meaning:** How strong the reaction away from the zone was.
- **Interpretation:** Larger = more significant zone.
- **Recommended for:** Machine Learning, Decision Engine

### `zone_width`  _(Priority: Medium)_
- **Formula:** High - Low of the zone origin bar
- **Meaning:** Price band width of the zone.
- **Interpretation:** Narrower zones are considered more precise reaction levels.
- **Recommended for:** Machine Learning, Decision Engine

### `demand_zone_age`  _(Priority: Low)_
- **Formula:** bars since the last demand_zone bar
- **Meaning:** Recency of the most recent demand zone.
- **Interpretation:** Smaller = more recently formed.
- **Recommended for:** Machine Learning

### `supply_zone_age`  _(Priority: Low)_
- **Formula:** bars since the last supply_zone bar
- **Meaning:** Recency of the most recent supply zone.
- **Interpretation:** Smaller = more recently formed.
- **Recommended for:** Machine Learning

### `fresh_demand_zone`  _(Priority: Medium)_
- **Formula:** demand_zone_age <= 20
- **Meaning:** Whether the nearest demand zone is still considered 'fresh' (untested).
- **Interpretation:** Fresh zones are traditionally considered more reliable than repeatedly-tested ones.
- **Recommended for:** Machine Learning, Decision Engine

### `fresh_supply_zone`  _(Priority: Medium)_
- **Formula:** supply_zone_age <= 20
- **Meaning:** Whether the nearest supply zone is still considered 'fresh' (untested).
- **Interpretation:** See fresh_demand_zone.
- **Recommended for:** Machine Learning, Decision Engine

### `nearest_demand_zone`  _(Priority: Medium)_
- **Formula:** Low of the most recent demand_zone origin bar
- **Meaning:** Price level of the nearest demand zone floor.
- **Interpretation:** Reference level for support-style reactions.
- **Recommended for:** Machine Learning, Decision Engine

### `nearest_supply_zone`  _(Priority: Medium)_
- **Formula:** High of the most recent supply_zone origin bar
- **Meaning:** Price level of the nearest supply zone ceiling.
- **Interpretation:** Reference level for resistance-style reactions.
- **Recommended for:** Machine Learning, Decision Engine

### `demand_zone_retested`  _(Priority: Medium)_
- **Formula:** price re-enters the demand zone band after formation
- **Meaning:** Whether today's bar dipped back into an existing demand zone.
- **Interpretation:** A retest that holds strengthens the zone; a retest that fails (closes through) invalidates it.
- **Recommended for:** Machine Learning, Decision Engine

### `supply_zone_retested`  _(Priority: Medium)_
- **Formula:** price re-enters the supply zone band after formation
- **Meaning:** Whether today's bar pushed back into an existing supply zone.
- **Interpretation:** See demand_zone_retested.
- **Recommended for:** Machine Learning, Decision Engine

## fibonacci
### `fib_236`  _(Priority: Medium)_
- **Formula:** dynamic_support + 0.236 * (dynamic_resistance - dynamic_support)
- **Meaning:** 23.6% Fibonacci retracement level of the current swing range.
- **Interpretation:** A common area for a pullback within the prevailing trend to find support/resistance.
- **Recommended for:** Machine Learning, Decision Engine
- **Limitations:** Only as reliable as the underlying swing points (dynamic_support/dynamic_resistance), which repaint.

### `fib_382`  _(Priority: Medium)_
- **Formula:** dynamic_support + 0.382 * (dynamic_resistance - dynamic_support)
- **Meaning:** 38.2% Fibonacci retracement level of the current swing range.
- **Interpretation:** A common area for a pullback within the prevailing trend to find support/resistance.
- **Recommended for:** Machine Learning, Decision Engine
- **Limitations:** Only as reliable as the underlying swing points (dynamic_support/dynamic_resistance), which repaint.

### `fib_50`  _(Priority: Medium)_
- **Formula:** dynamic_support + 0.5 * (dynamic_resistance - dynamic_support)
- **Meaning:** 50.0% Fibonacci retracement level of the current swing range.
- **Interpretation:** A common area for a pullback within the prevailing trend to find support/resistance.
- **Recommended for:** Machine Learning, Decision Engine
- **Limitations:** Only as reliable as the underlying swing points (dynamic_support/dynamic_resistance), which repaint.

### `fib_618`  _(Priority: Medium)_
- **Formula:** dynamic_support + 0.618 * (dynamic_resistance - dynamic_support)
- **Meaning:** 61.8% Fibonacci retracement level of the current swing range.
- **Interpretation:** A common area for a pullback within the prevailing trend to find support/resistance.
- **Recommended for:** Machine Learning, Decision Engine
- **Limitations:** Only as reliable as the underlying swing points (dynamic_support/dynamic_resistance), which repaint.

### `fib_786`  _(Priority: Medium)_
- **Formula:** dynamic_support + 0.786 * (dynamic_resistance - dynamic_support)
- **Meaning:** 78.6% Fibonacci retracement level of the current swing range.
- **Interpretation:** A common area for a pullback within the prevailing trend to find support/resistance.
- **Recommended for:** Machine Learning, Decision Engine
- **Limitations:** Only as reliable as the underlying swing points (dynamic_support/dynamic_resistance), which repaint.

### `fib_1272`  _(Priority: Low)_
- **Formula:** dynamic_support + 1.272 * (dynamic_resistance - dynamic_support)
- **Meaning:** 1.272 Fibonacci extension level beyond the current swing range.
- **Interpretation:** A common projected target if the prevailing trend continues past the recent swing high.
- **Recommended for:** Machine Learning, Decision Engine

### `fib_1618`  _(Priority: Low)_
- **Formula:** dynamic_support + 1.618 * (dynamic_resistance - dynamic_support)
- **Meaning:** 1.618 Fibonacci extension level beyond the current swing range.
- **Interpretation:** A common projected target if the prevailing trend continues past the recent swing high.
- **Recommended for:** Machine Learning, Decision Engine

### `fib_2618`  _(Priority: Low)_
- **Formula:** dynamic_support + 2.618 * (dynamic_resistance - dynamic_support)
- **Meaning:** 2.618 Fibonacci extension level beyond the current swing range.
- **Interpretation:** A common projected target if the prevailing trend continues past the recent swing high.
- **Recommended for:** Machine Learning, Decision Engine

### `distance_from_fibonacci`  _(Priority: Medium)_
- **Formula:** min(|Close - each fib level|) / Close
- **Meaning:** Normalized distance from price to the nearest Fibonacci level.
- **Interpretation:** Near zero = price is sitting right on a Fibonacci level.
- **Recommended for:** Machine Learning

### `closest_fibonacci_level`  _(Priority: Low)_
- **Formula:** argmin(|Close - each fib level|)
- **Meaning:** Name of the nearest Fibonacci level.
- **Interpretation:** Categorical feature identifying which level price is currently reacting to.
- **Recommended for:** Machine Learning

### `fibonacci_confluence`  _(Priority: High)_
- **Formula:** any fib level within 1.5% of static_support/static_resistance
- **Meaning:** A Fibonacci level lines up with an independent support/resistance level.
- **Interpretation:** Confluence of multiple methods at the same price is traditionally considered a stronger level.
- **Recommended for:** Decision Engine, Machine Learning

## market_structure
### `trend_score`  _(Priority: High)_
- **Formula:** OLS slope of Close over last 20 bars * window, in rolling-std units
- **Meaning:** Normalized trend strength and direction.
- **Interpretation:** Positive = uptrend, negative = downtrend; magnitude = conviction, comparable across tickers.
- **Recommended for:** Machine Learning, Decision Engine
- **Limitations:** A regression slope treats the window as linear — doesn't capture curvature/acceleration.

### `trend_label`  _(Priority: High)_
- **Formula:** Uptrend if trend_score > 1, Downtrend if < -1, else Sideways
- **Meaning:** Categorical trend regime.
- **Interpretation:** Direct, human-readable trend classification.
- **Recommended for:** Decision Engine, Machine Learning

### `is_uptrend`  _(Priority: Medium)_
- **Formula:** trend_label == 'Uptrend'
- **Meaning:** Boolean uptrend flag.
- **Interpretation:** One-hot-style flag for tree models.
- **Recommended for:** Machine Learning

### `is_downtrend`  _(Priority: Medium)_
- **Formula:** trend_label == 'Downtrend'
- **Meaning:** Boolean downtrend flag.
- **Interpretation:** One-hot-style flag for tree models.
- **Recommended for:** Machine Learning

### `is_sideways`  _(Priority: Medium)_
- **Formula:** trend_label == 'Sideways'
- **Meaning:** Boolean sideways/range-bound flag.
- **Interpretation:** One-hot-style flag for tree models.
- **Recommended for:** Machine Learning

### `trend_reversal_signal`  _(Priority: High)_
- **Formula:** trend_label flips between Uptrend and Downtrend, or change_of_character is True
- **Meaning:** A structural or regression-based trend change just occurred.
- **Interpretation:** Early-warning flag; combine with volume confirmation before acting on it.
- **Recommended for:** Decision Engine, Machine Learning

### `higher_high_count`  _(Priority: Medium)_
- **Formula:** count of Higher Highs among the last 4 confirmed swing highs
- **Meaning:** How many of the recent swing highs were higher than the swing high before them.
- **Interpretation:** Higher counts support an uptrend classification (Dow Theory).
- **Recommended for:** Machine Learning, Decision Engine

### `lower_high_count`  _(Priority: Medium)_
- **Formula:** count of Lower Highs among the last 4 confirmed swing highs
- **Meaning:** How many recent swing highs were lower than the one before them.
- **Interpretation:** Higher counts support a downtrend classification.
- **Recommended for:** Machine Learning, Decision Engine

### `higher_low_count`  _(Priority: Medium)_
- **Formula:** count of Higher Lows among the last 4 confirmed swing lows
- **Meaning:** How many recent swing lows were higher than the one before them.
- **Interpretation:** Higher counts support an uptrend classification.
- **Recommended for:** Machine Learning, Decision Engine

### `lower_low_count`  _(Priority: Medium)_
- **Formula:** count of Lower Lows among the last 4 confirmed swing lows
- **Meaning:** How many recent swing lows were lower than the one before them.
- **Interpretation:** Higher counts support a downtrend classification.
- **Recommended for:** Machine Learning, Decision Engine

### `bullish_structure`  _(Priority: High)_
- **Formula:** most recent swing is both a Higher High and a Higher Low
- **Meaning:** Textbook Dow Theory uptrend confirmation.
- **Interpretation:** True = structure currently supports an uptrend read.
- **Recommended for:** Decision Engine, Machine Learning

### `bearish_structure`  _(Priority: High)_
- **Formula:** most recent swing is both a Lower High and a Lower Low
- **Meaning:** Textbook Dow Theory downtrend confirmation.
- **Interpretation:** True = structure currently supports a downtrend read.
- **Recommended for:** Decision Engine, Machine Learning

### `market_bias`  _(Priority: High)_
- **Formula:** Bullish if bullish_structure, Bearish if bearish_structure, else Neutral
- **Meaning:** Categorical summary of current market structure.
- **Interpretation:** Human-readable structure-based bias, independent of trend_label's regression approach.
- **Recommended for:** Decision Engine

### `market_structure`  _(Priority: Medium)_
- **Formula:** = market_bias
- **Meaning:** Alias exposed under the spec's requested column name.
- **Interpretation:** See market_bias.
- **Recommended for:** Decision Engine

## breakout
### `breakout_above_resistance`  _(Priority: High)_
- **Formula:** Close(t) > static_resistance(t-1)
- **Meaning:** Price closed above the prior rolling resistance level.
- **Interpretation:** Potential start of a new upward move.
- **Recommended for:** Decision Engine, Machine Learning
- **Limitations:** A single close above resistance is a weak signal alone — check volume_confirmation.

### `breakdown_below_support`  _(Priority: High)_
- **Formula:** Close(t) < static_support(t-1)
- **Meaning:** Price closed below the prior rolling support level.
- **Interpretation:** Potential start of a new downward move.
- **Recommended for:** Decision Engine, Machine Learning

### `volume_confirmation`  _(Priority: High)_
- **Formula:** volume_ratio >= 1.5
- **Meaning:** Whether today's volume was elevated enough to trust a breakout.
- **Interpretation:** True = the move had above-average participation.
- **Recommended for:** Decision Engine, Machine Learning

### `fake_breakout`  _(Priority: High)_
- **Formula:** breakout occurred but the very next close fell back inside the level
- **Meaning:** A breakout that failed to hold.
- **Interpretation:** Common trap for naive breakout strategies; finalizes one bar after the breakout bar.
- **Recommended for:** Decision Engine, Machine Learning
- **Limitations:** Uses the next bar's close, so this label is only known one day later — not usable as a same-day live feature.

### `breakout_label`  _(Priority: Medium)_
- **Formula:** categorical combination of breakout direction + volume_confirmation + fake_breakout
- **Meaning:** Human-readable summary of the day's breakout status.
- **Interpretation:** One of: None, Confirmed/Unconfirmed Breakout Up, Confirmed/Unconfirmed Breakdown, Fake Breakout.
- **Recommended for:** Decision Engine

### `support_bounce`  _(Priority: Medium)_
- **Formula:** price within 1.5% of static_support and closed bullish, without breaking down
- **Meaning:** Price tested support and reacted upward.
- **Interpretation:** Supports a 'buy the dip' read at a known level.
- **Recommended for:** Decision Engine, Machine Learning

### `resistance_rejection`  _(Priority: Medium)_
- **Formula:** price within 1.5% of static_resistance and closed bearish, without breaking out
- **Meaning:** Price tested resistance and reacted downward.
- **Interpretation:** Supports a 'fade the rally' read at a known level.
- **Recommended for:** Decision Engine, Machine Learning

### `demand_zone_bounce`  _(Priority: Medium)_
- **Formula:** Low dipped into the nearest demand zone and the bar closed bullish
- **Meaning:** Price reacted upward from a demand zone.
- **Interpretation:** Zone-based analogue of support_bounce.
- **Recommended for:** Decision Engine, Machine Learning

### `supply_zone_rejection`  _(Priority: Medium)_
- **Formula:** High pushed into the nearest supply zone and the bar closed bearish
- **Meaning:** Price reacted downward from a supply zone.
- **Interpretation:** Zone-based analogue of resistance_rejection.
- **Recommended for:** Decision Engine, Machine Learning

## target
### `target_1_day`  _(Priority: High)_
- **Formula:** Close(t + 1)
- **Meaning:** Raw future closing price 1 day(s) ahead.
- **Interpretation:** Regression label; NaN for the last few rows where the future isn't known yet.
- **Recommended for:** Machine Learning, Time Series, Deep Learning
- **When to use:** Direct regression target for price-level prediction models.

### `future_return_1_day`  _(Priority: High)_
- **Formula:** (Close(t+1) - Close(t)) / Close(t)
- **Meaning:** Percentage return over the next 1 day(s).
- **Interpretation:** Scale-invariant regression label, comparable across tickers.
- **Recommended for:** Machine Learning, Deep Learning
- **When to use:** Preferred regression target over raw price for cross-ticker models.

### `target_direction_1_day`  _(Priority: High)_
- **Formula:** Close(t+1) > Close(t)
- **Meaning:** Binary up/down direction over the next 1 day(s).
- **Interpretation:** True = price rose; False = price fell or was flat.
- **Recommended for:** Machine Learning, Decision Engine
- **When to use:** Classification target for Buy/Hold/Sell-style signal models.

### `target_regression_1_day`  _(Priority: Medium)_
- **Formula:** future_return_1_day
- **Meaning:** Alias of future_return, named explicitly as the regression target per spec.
- **Interpretation:** Identical values to future_return_*_day.
- **Recommended for:** Machine Learning

### `target_3_day`  _(Priority: High)_
- **Formula:** Close(t + 3)
- **Meaning:** Raw future closing price 3 day(s) ahead.
- **Interpretation:** Regression label; NaN for the last few rows where the future isn't known yet.
- **Recommended for:** Machine Learning, Time Series, Deep Learning
- **When to use:** Direct regression target for price-level prediction models.

### `future_return_3_day`  _(Priority: High)_
- **Formula:** (Close(t+3) - Close(t)) / Close(t)
- **Meaning:** Percentage return over the next 3 day(s).
- **Interpretation:** Scale-invariant regression label, comparable across tickers.
- **Recommended for:** Machine Learning, Deep Learning
- **When to use:** Preferred regression target over raw price for cross-ticker models.

### `target_direction_3_day`  _(Priority: High)_
- **Formula:** Close(t+3) > Close(t)
- **Meaning:** Binary up/down direction over the next 3 day(s).
- **Interpretation:** True = price rose; False = price fell or was flat.
- **Recommended for:** Machine Learning, Decision Engine
- **When to use:** Classification target for Buy/Hold/Sell-style signal models.

### `target_regression_3_day`  _(Priority: Medium)_
- **Formula:** future_return_3_day
- **Meaning:** Alias of future_return, named explicitly as the regression target per spec.
- **Interpretation:** Identical values to future_return_*_day.
- **Recommended for:** Machine Learning

### `target_5_day`  _(Priority: High)_
- **Formula:** Close(t + 5)
- **Meaning:** Raw future closing price 5 day(s) ahead.
- **Interpretation:** Regression label; NaN for the last few rows where the future isn't known yet.
- **Recommended for:** Machine Learning, Time Series, Deep Learning
- **When to use:** Direct regression target for price-level prediction models.

### `future_return_5_day`  _(Priority: High)_
- **Formula:** (Close(t+5) - Close(t)) / Close(t)
- **Meaning:** Percentage return over the next 5 day(s).
- **Interpretation:** Scale-invariant regression label, comparable across tickers.
- **Recommended for:** Machine Learning, Deep Learning
- **When to use:** Preferred regression target over raw price for cross-ticker models.

### `target_direction_5_day`  _(Priority: High)_
- **Formula:** Close(t+5) > Close(t)
- **Meaning:** Binary up/down direction over the next 5 day(s).
- **Interpretation:** True = price rose; False = price fell or was flat.
- **Recommended for:** Machine Learning, Decision Engine
- **When to use:** Classification target for Buy/Hold/Sell-style signal models.

### `target_regression_5_day`  _(Priority: Medium)_
- **Formula:** future_return_5_day
- **Meaning:** Alias of future_return, named explicitly as the regression target per spec.
- **Interpretation:** Identical values to future_return_*_day.
- **Recommended for:** Machine Learning

## Feature Selection Analysis

### Highly Correlated Pairs (>= threshold)
| Feature A | Feature B | Correlation |
|---|---|---|
| price_diff | open_close_diff | 1.0000 |
| sma_20 | bollinger_middle | 1.0000 |
| sma_5 | rolling_mean_5 | 1.0000 |
| sma_10 | rolling_mean_10 | 1.0000 |
| std_10 | rolling_std_10 | 1.0000 |
| variance_10 | rolling_var_10 | 1.0000 |
| sma_20 | rolling_mean_20 | 1.0000 |
| bollinger_middle | rolling_mean_20 | 1.0000 |
| std_20 | rolling_std_20 | 1.0000 |
| variance_20 | rolling_var_20 | 1.0000 |
| dynamic_support | nearest_support | 1.0000 |
| dynamic_resistance | nearest_resistance | 1.0000 |
| high_low_diff | zone_width | 1.0000 |
| change_of_character | trend_reversal_signal | 1.0000 |
| typical_price | weighted_close | 1.0000 |
| typical_price | median_price | 1.0000 |
| dynamic_resistance | nearest_supply_zone | 1.0000 |
| nearest_resistance | nearest_supply_zone | 1.0000 |
| median_price | weighted_close | 0.9999 |
| close | weighted_close | 0.9999 |
| close | typical_price | 0.9999 |
| high | median_price | 0.9999 |
| low | median_price | 0.9999 |
| high | typical_price | 0.9998 |
| pct_return | log_return | 0.9998 |
| low | typical_price | 0.9998 |
| high | weighted_close | 0.9998 |
| low | weighted_close | 0.9998 |
| close | median_price | 0.9998 |
| open | median_price | 0.9998 |
| rolling_max_20 | static_resistance | 0.9997 |
| rolling_min_20 | static_support | 0.9997 |
| open | typical_price | 0.9997 |
| rolling_volatility_20 | historical_volatility | 0.9997 |
| close_lag_1 | high_lag_1 | 0.9997 |
| high | close | 0.9997 |
| close_lag_3 | high_lag_3 | 0.9997 |
| close_lag_2 | high_lag_2 | 0.9997 |
| close_lag_5 | high_lag_5 | 0.9997 |
| close_lag_10 | high_lag_10 | 0.9997 |
| open | weighted_close | 0.9996 |
| close_lag_20 | high_lag_20 | 0.9996 |
| open | high | 0.9996 |
| open_lag_1 | high_lag_1 | 0.9996 |
| open_lag_2 | high_lag_2 | 0.9996 |
| open_lag_3 | high_lag_3 | 0.9996 |
| open | low | 0.9996 |
| open_lag_5 | high_lag_5 | 0.9996 |
| open_lag_5 | low_lag_5 | 0.9996 |
| open_lag_1 | low_lag_1 | 0.9996 |
| open_lag_2 | low_lag_2 | 0.9996 |
| open_lag_10 | low_lag_10 | 0.9996 |
| open_lag_3 | low_lag_3 | 0.9996 |
| open_lag_10 | high_lag_10 | 0.9996 |
| close_lag_1 | low_lag_1 | 0.9996 |
| low | close | 0.9996 |
| close_lag_2 | low_lag_2 | 0.9996 |
| close_lag_3 | low_lag_3 | 0.9996 |
| close_lag_5 | low_lag_5 | 0.9996 |
| close_lag_10 | low_lag_10 | 0.9996 |
| open_lag_20 | low_lag_20 | 0.9996 |
| open_lag_20 | high_lag_20 | 0.9996 |
| close_lag_20 | low_lag_20 | 0.9996 |
| sma_5 | ema_5 | 0.9996 |
| ema_5 | rolling_mean_5 | 0.9996 |
| sma_5 | rolling_median_5 | 0.9995 |
| rolling_mean_5 | rolling_median_5 | 0.9995 |
| high | low | 0.9995 |
| high_lag_1 | low_lag_1 | 0.9995 |
| high_lag_3 | low_lag_3 | 0.9995 |
| high_lag_2 | low_lag_2 | 0.9995 |
| high_lag_5 | low_lag_5 | 0.9995 |
| high_lag_10 | low_lag_10 | 0.9994 |
| open | close | 0.9994 |
| close_lag_1 | open_lag_1 | 0.9994 |
| close_lag_2 | open_lag_2 | 0.9994 |
| high_lag_20 | low_lag_20 | 0.9994 |
| close_lag_3 | open_lag_3 | 0.9994 |
| close_lag_5 | open_lag_5 | 0.9994 |
| close_lag_10 | open_lag_10 | 0.9994 |
| close_lag_20 | open_lag_20 | 0.9994 |
| ema_200 | vwap | 0.9993 |
| sma_10 | rolling_median_10 | 0.9992 |
| rolling_mean_10 | rolling_median_10 | 0.9992 |
| sma_10 | ema_10 | 0.9991 |
| ema_10 | rolling_mean_10 | 0.9991 |
| fib_382 | fib_50 | 0.9989 |
| fib_50 | fib_618 | 0.9989 |
| ema_5 | rolling_median_5 | 0.9988 |
| fib_236 | fib_382 | 0.9985 |
| rolling_median_5 | close_lag_2 | 0.9983 |
| sma_20 | rolling_median_20 | 0.9982 |
| bollinger_middle | rolling_median_20 | 0.9982 |
| rolling_mean_20 | rolling_median_20 | 0.9982 |
| ema_5 | rolling_min_5 | 0.9980 |
| rolling_median_5 | high_lag_2 | 0.9980 |
| ema_10 | rolling_median_10 | 0.9980 |
| rolling_median_5 | low_lag_2 | 0.9979 |
| rolling_median_5 | open_lag_2 | 0.9978 |
| sma_5 | rolling_min_5 | 0.9978 |
| rolling_mean_5 | rolling_min_5 | 0.9978 |
| sma_5 | rolling_max_5 | 0.9978 |
| rolling_mean_5 | rolling_max_5 | 0.9978 |
| sma_5 | close_lag_2 | 0.9978 |
| rolling_mean_5 | close_lag_2 | 0.9978 |
| fib_618 | fib_786 | 0.9976 |
| sma_5 | high_lag_2 | 0.9976 |
| rolling_mean_5 | high_lag_2 | 0.9976 |
| sma_5 | low_lag_2 | 0.9974 |
| rolling_mean_5 | low_lag_2 | 0.9974 |
| ema_100 | vwap | 0.9974 |
| sma_20 | ema_20 | 0.9973 |
| ema_20 | bollinger_middle | 0.9973 |
| ema_20 | rolling_mean_20 | 0.9973 |
| ema_5 | close_lag_1 | 0.9973 |
| sma_5 | open_lag_2 | 0.9973 |
| rolling_mean_5 | open_lag_2 | 0.9973 |
| ema_100 | ema_200 | 0.9971 |
| ema_5 | ema_10 | 0.9971 |
| ema_5 | high_lag_1 | 0.9971 |
| ema_5 | rolling_max_5 | 0.9971 |
| ema_5 | low_lag_1 | 0.9970 |
| sma_100 | ema_200 | 0.9970 |
| ema_5 | close_lag_2 | 0.9968 |
| ema_5 | open_lag_1 | 0.9968 |
| rolling_median_5 | rolling_max_5 | 0.9968 |
| sma_5 | close_lag_3 | 0.9967 |
| rolling_mean_5 | close_lag_3 | 0.9967 |
| rolling_median_5 | rolling_min_5 | 0.9967 |
| sma_5 | ema_10 | 0.9967 |
| ema_10 | rolling_mean_5 | 0.9967 |
| ema_5 | high_lag_2 | 0.9966 |
| sma_5 | close_lag_1 | 0.9966 |
| rolling_mean_5 | close_lag_1 | 0.9966 |
| dynamic_support | nearest_demand_zone | 0.9965 |
| nearest_support | nearest_demand_zone | 0.9965 |
| sma_5 | high_lag_3 | 0.9965 |
| rolling_mean_5 | high_lag_3 | 0.9965 |
| ema_5 | low_lag_2 | 0.9964 |
| rolling_median_10 | close_lag_5 | 0.9964 |
| rolling_median_5 | close_lag_3 | 0.9964 |
| sma_5 | high_lag_1 | 0.9964 |
| rolling_mean_5 | high_lag_1 | 0.9964 |
| ema_5 | open_lag_2 | 0.9964 |
| dynamic_support | fib_236 | 0.9964 |
| nearest_support | fib_236 | 0.9964 |
| sma_5 | low_lag_1 | 0.9963 |
| rolling_mean_5 | low_lag_1 | 0.9963 |
| rolling_median_10 | high_lag_5 | 0.9962 |
| sma_5 | low_lag_3 | 0.9962 |
| rolling_mean_5 | low_lag_3 | 0.9962 |
| sma_5 | open_lag_3 | 0.9962 |
| rolling_mean_5 | open_lag_3 | 0.9962 |
| ema_10 | rolling_min_10 | 0.9962 |
| sma_200 | vwap | 0.9961 |
| rolling_median_5 | close_lag_1 | 0.9961 |
| rolling_median_10 | open_lag_5 | 0.9961 |
| nearest_supply_zone | fib_786 | 0.9961 |
| rolling_median_10 | low_lag_5 | 0.9961 |
| rolling_median_5 | high_lag_3 | 0.9961 |
| sma_5 | open_lag_1 | 0.9961 |
| rolling_mean_5 | open_lag_1 | 0.9961 |
| dynamic_resistance | fib_786 | 0.9960 |
| nearest_resistance | fib_786 | 0.9960 |
| rolling_median_5 | low_lag_3 | 0.9959 |
| rolling_median_5 | high_lag_1 | 0.9959 |
| ema_10 | rolling_median_5 | 0.9959 |
| rolling_median_5 | open_lag_3 | 0.9959 |
| rolling_median_5 | low_lag_1 | 0.9958 |
| sma_100 | vwap | 0.9958 |
| rolling_min_5 | close_lag_1 | 0.9957 |
| fib_382 | fib_618 | 0.9956 |
| rolling_median_5 | open_lag_1 | 0.9955 |
| rolling_max_5 | close_lag_3 | 0.9955 |
| rolling_min_5 | low_lag_1 | 0.9955 |
| rolling_min_5 | high_lag_1 | 0.9954 |
| weighted_close | ema_5 | 0.9953 |
| rolling_min_5 | open_lag_1 | 0.9953 |
| typical_price | ema_5 | 0.9953 |
| rolling_min_5 | rolling_min_10 | 0.9953 |
| median_price | ema_5 | 0.9953 |
| close | ema_5 | 0.9953 |
| rolling_max_5 | high_lag_3 | 0.9953 |
| sma_10 | close_lag_5 | 0.9952 |
| rolling_mean_10 | close_lag_5 | 0.9952 |
| high | ema_5 | 0.9952 |
| low | ema_5 | 0.9952 |
| ema_5 | rolling_min_10 | 0.9951 |
| rolling_min_5 | close_lag_2 | 0.9951 |
| ema_10 | rolling_max_5 | 0.9950 |
| rolling_min_5 | high_lag_2 | 0.9950 |
| sma_10 | high_lag_5 | 0.9950 |
| rolling_mean_10 | high_lag_5 | 0.9950 |
| rolling_min_5 | open_lag_2 | 0.9949 |
| ema_50 | ema_100 | 0.9949 |
| rolling_max_5 | low_lag_3 | 0.9949 |
| rolling_max_5 | close_lag_2 | 0.9949 |
| rolling_min_5 | low_lag_2 | 0.9949 |
| fib_236 | fib_50 | 0.9948 |
| sma_10 | low_lag_5 | 0.9948 |
| rolling_mean_10 | low_lag_5 | 0.9948 |
| open | ema_5 | 0.9948 |
| sma_10 | ema_5 | 0.9948 |
| ema_5 | rolling_mean_10 | 0.9948 |
| sma_10 | open_lag_5 | 0.9948 |
| rolling_mean_10 | open_lag_5 | 0.9948 |
| rolling_max_5 | high_lag_2 | 0.9947 |
| rolling_max_5 | open_lag_3 | 0.9947 |
| sma_100 | sma_200 | 0.9947 |
| bollinger_lower | rolling_min_20 | 0.9947 |
| ema_5 | close_lag_3 | 0.9947 |
| sma_10 | rolling_min_10 | 0.9947 |
| rolling_mean_10 | rolling_min_10 | 0.9947 |
| bollinger_lower | static_support | 0.9947 |
| sma_10 | rolling_mean_5 | 0.9946 |
| sma_5 | sma_10 | 0.9946 |
| sma_5 | rolling_mean_10 | 0.9946 |
| rolling_mean_5 | rolling_mean_10 | 0.9946 |
| weighted_close | close_lag_1 | 0.9946 |
| typical_price | close_lag_1 | 0.9946 |
| close | close_lag_1 | 0.9945 |
| median_price | close_lag_1 | 0.9945 |
| close_lag_1 | close_lag_2 | 0.9945 |
| bollinger_upper | rolling_max_20 | 0.9945 |
| close_lag_2 | close_lag_3 | 0.9945 |
| ema_5 | high_lag_3 | 0.9945 |
| rolling_max_5 | low_lag_2 | 0.9945 |
| high | close_lag_1 | 0.9944 |
| nearest_demand_zone | fib_236 | 0.9944 |
| close_lag_2 | high_lag_1 | 0.9944 |
| close_lag_3 | high_lag_2 | 0.9944 |
| ema_10 | close_lag_3 | 0.9944 |
| sma_200 | ema_200 | 0.9943 |
| weighted_close | rolling_min_5 | 0.9943 |
| typical_price | rolling_min_5 | 0.9943 |
| low | close_lag_1 | 0.9943 |
| sma_5 | rolling_min_10 | 0.9943 |
| rolling_mean_5 | rolling_min_10 | 0.9943 |
| close_lag_2 | low_lag_1 | 0.9943 |
| median_price | rolling_min_5 | 0.9943 |
| close_lag_3 | low_lag_2 | 0.9943 |
| close | rolling_min_5 | 0.9943 |
| sma_10 | rolling_max_5 | 0.9943 |
| rolling_max_5 | rolling_mean_10 | 0.9943 |
| ema_20 | rolling_median_20 | 0.9943 |
| sma_10 | rolling_max_10 | 0.9942 |
| rolling_mean_10 | rolling_max_10 | 0.9942 |
| rolling_max_5 | rolling_median_10 | 0.9942 |
| ema_5 | low_lag_3 | 0.9942 |
| bollinger_upper | static_resistance | 0.9942 |
| ema_5 | open_lag_3 | 0.9942 |
| ema_10 | high_lag_3 | 0.9942 |
| weighted_close | high_lag_1 | 0.9942 |
| low | rolling_min_5 | 0.9942 |
| typical_price | high_lag_1 | 0.9942 |
| rolling_max_5 | open_lag_2 | 0.9941 |
| ema_10 | low_lag_3 | 0.9941 |
| high | rolling_min_5 | 0.9941 |
| close | high_lag_1 | 0.9941 |
| median_price | high_lag_1 | 0.9941 |
| close_lag_1 | high_lag_2 | 0.9941 |
| high | high_lag_1 | 0.9941 |
| weighted_close | open_lag_1 | 0.9941 |
| weighted_close | low_lag_1 | 0.9941 |
| open | close_lag_1 | 0.9941 |
| typical_price | open_lag_1 | 0.9941 |
| close_lag_2 | high_lag_3 | 0.9941 |
| typical_price | low_lag_1 | 0.9941 |
| high_lag_1 | high_lag_2 | 0.9941 |
| close_lag_2 | open_lag_1 | 0.9940 |
| close | open_lag_1 | 0.9940 |
| close | low_lag_1 | 0.9940 |
| high_lag_2 | high_lag_3 | 0.9940 |
| close_lag_3 | open_lag_2 | 0.9940 |
| close_lag_1 | open_lag_2 | 0.9940 |
| close_lag_1 | low_lag_2 | 0.9940 |
| median_price | open_lag_1 | 0.9940 |
| median_price | low_lag_1 | 0.9940 |
| close_lag_2 | open_lag_3 | 0.9940 |
| close_lag_2 | low_lag_3 | 0.9940 |
| ema_10 | rolling_min_5 | 0.9940 |
| open | rolling_min_5 | 0.9939 |
| high | low_lag_1 | 0.9939 |
| high | open_lag_1 | 0.9939 |
| high_lag_1 | low_lag_2 | 0.9939 |
| ema_10 | open_lag_3 | 0.9939 |
| open_lag_2 | high_lag_1 | 0.9939 |
| low | high_lag_1 | 0.9939 |
| high_lag_2 | low_lag_3 | 0.9939 |
| open_lag_3 | high_lag_2 | 0.9938 |
| high_lag_2 | low_lag_1 | 0.9938 |
| low | open_lag_1 | 0.9938 |
| high_lag_3 | low_lag_2 | 0.9938 |
| low | low_lag_1 | 0.9938 |
| open_lag_2 | low_lag_1 | 0.9938 |
| sma_10 | close_lag_3 | 0.9938 |
| rolling_mean_10 | close_lag_3 | 0.9938 |
| low_lag_1 | low_lag_2 | 0.9938 |
| open_lag_3 | low_lag_2 | 0.9938 |
| low_lag_2 | low_lag_3 | 0.9937 |
| sma_10 | rolling_median_5 | 0.9937 |
| rolling_median_5 | rolling_mean_10 | 0.9937 |
| ema_10 | ema_20 | 0.9937 |
| open | high_lag_1 | 0.9937 |
| sma_10 | high_lag_3 | 0.9936 |
| rolling_mean_10 | high_lag_3 | 0.9936 |
| open_lag_1 | high_lag_2 | 0.9936 |
| sma_5 | rolling_median_10 | 0.9936 |
| rolling_mean_5 | rolling_median_10 | 0.9936 |
| sma_10 | low_lag_3 | 0.9936 |
| rolling_mean_10 | low_lag_3 | 0.9936 |
| open_lag_2 | high_lag_3 | 0.9936 |
| rolling_median_10 | close_lag_3 | 0.9936 |
| open | open_lag_1 | 0.9936 |
| rolling_median_20 | close_lag_10 | 0.9935 |
| open_lag_1 | open_lag_2 | 0.9935 |
| open_lag_2 | open_lag_3 | 0.9935 |
| open | low_lag_1 | 0.9935 |
| dynamic_resistance | fib_1272 | 0.9935 |
| nearest_resistance | fib_1272 | 0.9935 |
| open_lag_1 | low_lag_2 | 0.9935 |
| rolling_median_10 | low_lag_3 | 0.9935 |
| open_lag_2 | low_lag_3 | 0.9935 |
| rolling_median_10 | high_lag_3 | 0.9934 |
| ema_10 | close_lag_2 | 0.9934 |
| ema_5 | rolling_median_10 | 0.9934 |
| sma_10 | open_lag_3 | 0.9933 |
| rolling_mean_10 | open_lag_3 | 0.9933 |
| rolling_median_20 | high_lag_10 | 0.9933 |
| higher_low | lower_low | 0.9933 |
| higher_high | lower_high | 0.9933 |
| nearest_supply_zone | fib_1272 | 0.9933 |
| ema_10 | high_lag_2 | 0.9933 |
| ema_10 | low_lag_2 | 0.9933 |
| fib_50 | fib_786 | 0.9933 |
| rolling_median_5 | rolling_min_10 | 0.9932 |
| rolling_median_20 | open_lag_10 | 0.9932 |
| typical_price | sma_5 | 0.9932 |
| typical_price | rolling_mean_5 | 0.9932 |
| weighted_close | sma_5 | 0.9932 |
| weighted_close | rolling_mean_5 | 0.9932 |
| median_price | sma_5 | 0.9932 |
| median_price | rolling_mean_5 | 0.9932 |
| rolling_median_20 | low_lag_10 | 0.9932 |
| close | sma_5 | 0.9931 |
| close | rolling_mean_5 | 0.9931 |
| rolling_median_10 | open_lag_3 | 0.9931 |
| high | sma_5 | 0.9931 |
| high | rolling_mean_5 | 0.9931 |
| low | sma_5 | 0.9930 |
| low | rolling_mean_5 | 0.9930 |
| rolling_max_5 | close_lag_1 | 0.9929 |
| ema_10 | open_lag_2 | 0.9929 |
| rolling_min_5 | close_lag_3 | 0.9929 |
| rolling_max_5 | high_lag_1 | 0.9928 |
| rolling_median_10 | rolling_min_10 | 0.9928 |
| rolling_min_5 | high_lag_3 | 0.9927 |
| ema_20 | rolling_mean_10 | 0.9927 |
| sma_10 | ema_20 | 0.9927 |
| rolling_median_5 | rolling_median_10 | 0.9927 |
| rolling_max_5 | low_lag_1 | 0.9926 |
| open | sma_5 | 0.9926 |
| open | rolling_mean_5 | 0.9926 |
| ema_10 | close_lag_5 | 0.9925 |
| rolling_min_5 | open_lag_3 | 0.9925 |
| rolling_min_5 | low_lag_3 | 0.9925 |
| rolling_max_5 | rolling_min_5 | 0.9925 |
| ema_10 | high_lag_5 | 0.9923 |
| ema_10 | low_lag_5 | 0.9922 |
| ema_10 | open_lag_5 | 0.9922 |
| rolling_max_5 | open_lag_1 | 0.9922 |
| rolling_min_10 | rolling_min_20 | 0.9921 |
| rolling_median_10 | rolling_max_10 | 0.9920 |
| rolling_min_10 | static_support | 0.9920 |
| typical_price | rolling_median_5 | 0.9919 |
| weighted_close | rolling_median_5 | 0.9919 |
| ema_10 | rolling_max_10 | 0.9919 |
| median_price | rolling_median_5 | 0.9919 |
| close | rolling_median_5 | 0.9918 |
| high | rolling_median_5 | 0.9918 |
| low | rolling_median_5 | 0.9917 |
| sma_100 | ema_100 | 0.9914 |
| open | rolling_median_5 | 0.9912 |
| sma_10 | close_lag_2 | 0.9911 |
| rolling_mean_10 | close_lag_2 | 0.9911 |
| sma_50 | ema_100 | 0.9911 |
| sma_10 | low_lag_2 | 0.9911 |
| rolling_mean_10 | low_lag_2 | 0.9911 |
| sma_10 | high_lag_2 | 0.9911 |
| rolling_mean_10 | high_lag_2 | 0.9911 |
| ema_20 | rolling_median_10 | 0.9910 |
| rolling_min_10 | low_lag_2 | 0.9910 |
| rolling_min_10 | close_lag_2 | 0.9910 |
| rolling_min_10 | high_lag_2 | 0.9910 |
| ema_10 | close_lag_1 | 0.9909 |
| sma_10 | rolling_min_5 | 0.9909 |
| rolling_min_5 | rolling_mean_10 | 0.9909 |
| ema_10 | low_lag_1 | 0.9909 |
| rolling_min_10 | open_lag_2 | 0.9908 |
| sma_50 | ema_50 | 0.9908 |
| ema_10 | high_lag_1 | 0.9907 |
| sma_10 | open_lag_2 | 0.9907 |
| rolling_mean_10 | open_lag_2 | 0.9907 |
| ema_20 | static_support | 0.9905 |
| rolling_min_10 | close_lag_3 | 0.9905 |
| ema_10 | open_lag_1 | 0.9904 |
| rolling_min_10 | low_lag_3 | 0.9904 |
| ema_20 | rolling_min_20 | 0.9904 |
| rolling_min_10 | high_lag_3 | 0.9904 |
| rolling_min_10 | open_lag_3 | 0.9902 |
| sma_20 | close_lag_10 | 0.9902 |
| bollinger_middle | close_lag_10 | 0.9902 |
| rolling_mean_20 | close_lag_10 | 0.9902 |
| sma_20 | high_lag_10 | 0.9902 |
| bollinger_middle | high_lag_10 | 0.9902 |
| rolling_mean_20 | high_lag_10 | 0.9902 |
| rolling_min_10 | low_lag_1 | 0.9901 |
| dynamic_support | fib_382 | 0.9901 |
| nearest_support | fib_382 | 0.9901 |
| rolling_min_10 | close_lag_1 | 0.9901 |
| sma_20 | low_lag_10 | 0.9900 |
| bollinger_middle | low_lag_10 | 0.9900 |
| rolling_mean_20 | low_lag_10 | 0.9900 |
| sma_20 | open_lag_10 | 0.9900 |
| bollinger_middle | open_lag_10 | 0.9900 |
| rolling_mean_20 | open_lag_10 | 0.9900 |
| fib_1272 | fib_1618 | 0.9900 |
| rolling_min_10 | high_lag_1 | 0.9899 |
| rolling_min_10 | open_lag_1 | 0.9898 |
| rolling_median_10 | low_lag_2 | 0.9897 |
| rolling_median_10 | close_lag_2 | 0.9897 |
| rolling_median_10 | high_lag_2 | 0.9896 |
| ema_50 | vwap | 0.9894 |
| rolling_max_5 | rolling_min_10 | 0.9894 |
| ema_10 | static_support | 0.9893 |
| nearest_demand_zone | fib_382 | 0.9892 |
| median_price | high_lag_2 | 0.9892 |
| typical_price | high_lag_2 | 0.9892 |
| typical_price | close_lag_2 | 0.9892 |
| typical_price | rolling_max_5 | 0.9892 |
| median_price | close_lag_2 | 0.9892 |
| rolling_median_10 | open_lag_2 | 0.9892 |
| weighted_close | close_lag_2 | 0.9892 |
| weighted_close | high_lag_2 | 0.9892 |
| weighted_close | rolling_max_5 | 0.9892 |
| median_price | rolling_max_5 | 0.9892 |
| high | rolling_max_5 | 0.9891 |
| low | high_lag_2 | 0.9891 |
| close | rolling_max_5 | 0.9891 |
| rolling_min_5 | rolling_median_10 | 0.9891 |
| high | close_lag_2 | 0.9891 |
| close | close_lag_2 | 0.9891 |
| high | high_lag_2 | 0.9891 |
| close | high_lag_2 | 0.9891 |
| low | close_lag_2 | 0.9890 |
| high_lag_3 | low_lag_1 | 0.9890 |
| close_lag_3 | high_lag_1 | 0.9890 |
| close_lag_1 | close_lag_3 | 0.9890 |
| high_lag_1 | high_lag_3 | 0.9890 |
| close_lag_1 | high_lag_3 | 0.9890 |
| close_lag_3 | low_lag_1 | 0.9890 |
| low | rolling_max_5 | 0.9890 |
| rolling_max_5 | close_lag_5 | 0.9890 |
| high_lag_5 | low_lag_3 | 0.9890 |
| close_lag_5 | high_lag_3 | 0.9889 |
| close_lag_3 | close_lag_5 | 0.9889 |
| high_lag_3 | high_lag_5 | 0.9889 |
| close_lag_3 | high_lag_5 | 0.9889 |
| close_lag_5 | low_lag_3 | 0.9889 |
| typical_price | open_lag_2 | 0.9889 |
| fib_236 | fib_618 | 0.9889 |
| median_price | open_lag_2 | 0.9889 |
| weighted_close | open_lag_2 | 0.9889 |
| ema_10 | rolling_min_20 | 0.9888 |
| close | open_lag_2 | 0.9888 |
| low | open_lag_2 | 0.9888 |
| high | open_lag_2 | 0.9887 |
| close_lag_1 | open_lag_3 | 0.9887 |
| open | high_lag_2 | 0.9887 |
| open_lag_3 | low_lag_1 | 0.9887 |
| open | close_lag_2 | 0.9887 |
| open_lag_3 | high_lag_1 | 0.9887 |
| rolling_max_10 | close_lag_5 | 0.9887 |
| open_lag_1 | high_lag_3 | 0.9887 |
| close_lag_3 | open_lag_1 | 0.9886 |
| typical_price | low_lag_2 | 0.9886 |
| close_lag_3 | open_lag_5 | 0.9886 |
| weighted_close | low_lag_2 | 0.9886 |
| rolling_max_10 | high_lag_5 | 0.9886 |
| median_price | low_lag_2 | 0.9886 |
| rolling_max_5 | high_lag_5 | 0.9886 |
| open_lag_5 | high_lag_3 | 0.9886 |
| open_lag_5 | low_lag_3 | 0.9886 |
| open_lag_3 | high_lag_5 | 0.9886 |
| rolling_max_5 | open_lag_5 | 0.9886 |
| close_lag_5 | open_lag_3 | 0.9885 |
| ema_20 | ema_50 | 0.9885 |
| open | rolling_max_5 | 0.9885 |
| close | low_lag_2 | 0.9885 |
| high | low_lag_2 | 0.9885 |
| close_lag_1 | low_lag_3 | 0.9885 |
| high_lag_1 | low_lag_3 | 0.9885 |
| low | low_lag_2 | 0.9884 |
| low_lag_1 | low_lag_3 | 0.9884 |
| close_lag_3 | low_lag_5 | 0.9884 |
| rolling_max_5 | low_lag_5 | 0.9884 |
| high_lag_3 | low_lag_5 | 0.9883 |
| open | open_lag_2 | 0.9883 |
| low_lag_3 | low_lag_5 | 0.9883 |
| open_lag_1 | open_lag_3 | 0.9883 |
| rolling_max_10 | low_lag_5 | 0.9883 |
| open_lag_3 | open_lag_5 | 0.9882 |
| rolling_max_10 | open_lag_5 | 0.9881 |
| open | low_lag_2 | 0.9881 |
| open_lag_1 | low_lag_3 | 0.9880 |
| open_lag_3 | low_lag_5 | 0.9879 |
| ema_20 | rolling_min_10 | 0.9877 |
| nearest_supply_zone | fib_618 | 0.9877 |
| sma_5 | close_lag_5 | 0.9876 |
| rolling_mean_5 | close_lag_5 | 0.9876 |
| dynamic_resistance | fib_618 | 0.9875 |
| nearest_resistance | fib_618 | 0.9875 |
| typical_price | rolling_min_10 | 0.9874 |
| median_price | rolling_min_10 | 0.9874 |
| weighted_close | rolling_min_10 | 0.9874 |
| sma_5 | high_lag_5 | 0.9873 |
| rolling_mean_5 | high_lag_5 | 0.9873 |
| low | rolling_min_10 | 0.9873 |
| sma_5 | open_lag_5 | 0.9873 |
| rolling_mean_5 | open_lag_5 | 0.9873 |
| close | rolling_min_10 | 0.9873 |
| high | rolling_min_10 | 0.9872 |
| sma_10 | low_lag_1 | 0.9872 |
| rolling_mean_10 | low_lag_1 | 0.9872 |
| sma_10 | close_lag_1 | 0.9871 |
| rolling_mean_10 | close_lag_1 | 0.9871 |
| sma_5 | low_lag_5 | 0.9871 |
| rolling_mean_5 | low_lag_5 | 0.9871 |
| sma_10 | high_lag_1 | 0.9871 |
| rolling_mean_10 | high_lag_1 | 0.9871 |
| sma_10 | static_support | 0.9870 |
| rolling_mean_10 | static_support | 0.9870 |
| ema_5 | close_lag_5 | 0.9870 |
| rolling_max_5 | rolling_max_10 | 0.9869 |
| open | rolling_min_10 | 0.9869 |
| fib_382 | fib_786 | 0.9868 |
| sma_10 | open_lag_1 | 0.9867 |
| rolling_mean_10 | open_lag_1 | 0.9867 |
| ema_5 | high_lag_5 | 0.9867 |
| rolling_median_5 | close_lag_5 | 0.9867 |
| typical_price | ema_10 | 0.9867 |
| ema_5 | open_lag_5 | 0.9867 |
| median_price | ema_10 | 0.9867 |
| rolling_min_10 | close_lag_5 | 0.9867 |
| weighted_close | ema_10 | 0.9867 |
| low | ema_10 | 0.9866 |
| sma_20 | rolling_mean_10 | 0.9866 |
| bollinger_middle | rolling_mean_10 | 0.9866 |
| sma_10 | sma_20 | 0.9866 |
| sma_10 | bollinger_middle | 0.9866 |
| sma_10 | rolling_mean_20 | 0.9866 |
| rolling_mean_10 | rolling_mean_20 | 0.9866 |
| sma_20 | ema_10 | 0.9866 |
| ema_10 | bollinger_middle | 0.9866 |
| ema_10 | rolling_mean_20 | 0.9866 |
| rolling_min_10 | high_lag_5 | 0.9866 |
| ema_5 | low_lag_5 | 0.9865 |
| close | ema_10 | 0.9865 |
| rolling_min_10 | low_lag_5 | 0.9865 |
| ema_20 | rolling_max_10 | 0.9865 |
| high | ema_10 | 0.9864 |
| rolling_median_5 | high_lag_5 | 0.9864 |
| rolling_min_10 | open_lag_5 | 0.9864 |
| rolling_median_5 | open_lag_5 | 0.9863 |
| sma_10 | rolling_min_20 | 0.9863 |
| rolling_mean_10 | rolling_min_20 | 0.9863 |
| rolling_median_5 | low_lag_5 | 0.9861 |
| open | ema_10 | 0.9861 |
| bollinger_lower | rolling_min_10 | 0.9860 |
| ema_20 | close_lag_5 | 0.9859 |
| ema_20 | low_lag_5 | 0.9858 |
| ema_20 | high_lag_5 | 0.9857 |
| ema_20 | open_lag_5 | 0.9855 |
| rolling_median_10 | static_support | 0.9853 |
| rolling_max_10 | rolling_median_20 | 0.9853 |
| sma_20 | fib_382 | 0.9853 |
| bollinger_middle | fib_382 | 0.9853 |
| rolling_mean_20 | fib_382 | 0.9853 |
| sma_20 | static_support | 0.9851 |
| bollinger_middle | static_support | 0.9851 |
| rolling_mean_20 | static_support | 0.9851 |
| rolling_median_10 | low_lag_1 | 0.9851 |
| rolling_median_10 | close_lag_1 | 0.9850 |
| sma_20 | static_resistance | 0.9850 |
| bollinger_middle | static_resistance | 0.9850 |
| rolling_mean_20 | static_resistance | 0.9850 |
| rolling_median_10 | high_lag_1 | 0.9849 |
| sma_20 | rolling_min_20 | 0.9849 |
| bollinger_middle | rolling_min_20 | 0.9849 |
| rolling_mean_20 | rolling_min_20 | 0.9849 |
| sma_20 | rolling_median_10 | 0.9849 |
| bollinger_middle | rolling_median_10 | 0.9849 |
| rolling_median_10 | rolling_mean_20 | 0.9849 |
| ema_5 | rolling_max_10 | 0.9848 |
| sma_20 | rolling_max_20 | 0.9848 |
| bollinger_middle | rolling_max_20 | 0.9848 |
| rolling_mean_20 | rolling_max_20 | 0.9848 |
| ema_50 | ema_200 | 0.9847 |
| sma_20 | fib_50 | 0.9846 |
| bollinger_middle | fib_50 | 0.9846 |
| rolling_mean_20 | fib_50 | 0.9846 |
| ema_50 | fib_236 | 0.9846 |
| rolling_median_10 | rolling_min_20 | 0.9846 |
| rolling_median_10 | open_lag_1 | 0.9846 |
| rolling_median_20 | fib_382 | 0.9845 |
| sma_20 | ema_50 | 0.9844 |
| ema_50 | bollinger_middle | 0.9844 |
| ema_50 | rolling_mean_20 | 0.9844 |
| sma_50 | vwap | 0.9842 |
| rolling_max_10 | rolling_mean_20 | 0.9842 |
| sma_20 | rolling_max_10 | 0.9842 |
| bollinger_middle | rolling_max_10 | 0.9842 |
| sma_5 | rolling_max_10 | 0.9841 |
| rolling_mean_5 | rolling_max_10 | 0.9841 |
| sma_10 | rolling_median_20 | 0.9840 |
| rolling_mean_10 | rolling_median_20 | 0.9840 |
| rolling_max_10 | close_lag_3 | 0.9839 |
| ema_20 | close_lag_10 | 0.9838 |
| rolling_max_10 | high_lag_3 | 0.9837 |
| ema_20 | high_lag_10 | 0.9837 |
| sma_200 | ema_100 | 0.9837 |
| weighted_close | close_lag_3 | 0.9837 |
| typical_price | close_lag_3 | 0.9837 |
| ema_20 | open_lag_10 | 0.9837 |
| rolling_max_10 | low_lag_3 | 0.9837 |
| ema_50 | rolling_min_20 | 0.9836 |
| close | close_lag_3 | 0.9836 |
| median_price | close_lag_3 | 0.9836 |
| high | close_lag_3 | 0.9835 |
| rolling_median_20 | fib_50 | 0.9835 |
| ema_20 | low_lag_10 | 0.9835 |
| close_lag_2 | close_lag_5 | 0.9835 |
| low | close_lag_3 | 0.9834 |
| close_lag_5 | high_lag_2 | 0.9834 |
| rolling_max_10 | open_lag_3 | 0.9833 |
| weighted_close | high_lag_3 | 0.9833 |
| typical_price | high_lag_3 | 0.9833 |
| close_lag_5 | low_lag_2 | 0.9833 |
| close | high_lag_3 | 0.9833 |
| median_price | high_lag_3 | 0.9832 |
| high | high_lag_3 | 0.9832 |
| bollinger_lower | rolling_median_10 | 0.9832 |
| sma_10 | bollinger_lower | 0.9831 |
| bollinger_lower | rolling_mean_10 | 0.9831 |
| close_lag_2 | high_lag_5 | 0.9831 |
| weighted_close | open_lag_3 | 0.9831 |
| typical_price | open_lag_3 | 0.9830 |
| low | high_lag_3 | 0.9830 |
| high_lag_2 | high_lag_5 | 0.9830 |
| close | open_lag_3 | 0.9830 |
| median_price | open_lag_3 | 0.9830 |
| weighted_close | low_lag_3 | 0.9829 |
| typical_price | low_lag_3 | 0.9829 |
| ema_10 | bollinger_lower | 0.9829 |
| high | open_lag_3 | 0.9829 |
| high_lag_5 | low_lag_2 | 0.9829 |
| sma_20 | fib_236 | 0.9829 |
| bollinger_middle | fib_236 | 0.9829 |
| rolling_mean_20 | fib_236 | 0.9829 |
| open | close_lag_3 | 0.9829 |
| close_lag_2 | open_lag_5 | 0.9829 |
| close | low_lag_3 | 0.9829 |
| rolling_median_5 | rolling_max_10 | 0.9829 |
| median_price | low_lag_3 | 0.9829 |
| low | open_lag_3 | 0.9828 |
| high | low_lag_3 | 0.9828 |
| open_lag_5 | high_lag_2 | 0.9828 |
| ema_50 | fib_382 | 0.9828 |
| close_lag_5 | open_lag_2 | 0.9827 |
| rolling_min_5 | close_lag_5 | 0.9827 |
| close_lag_2 | low_lag_5 | 0.9827 |
| low | low_lag_3 | 0.9827 |
| open_lag_5 | low_lag_2 | 0.9827 |
| ema_10 | rolling_median_20 | 0.9826 |
| high_lag_2 | low_lag_5 | 0.9826 |
| rolling_median_20 | fib_236 | 0.9826 |
| nearest_demand_zone | fib_50 | 0.9826 |
| dynamic_support | fib_50 | 0.9825 |
| nearest_support | fib_50 | 0.9825 |
| low_lag_2 | low_lag_5 | 0.9825 |
| rolling_min_5 | high_lag_5 | 0.9825 |
| open | high_lag_3 | 0.9824 |
| ema_5 | static_support | 0.9824 |
| rolling_min_5 | open_lag_5 | 0.9824 |
| rolling_min_5 | low_lag_5 | 0.9823 |
| ema_50 | static_support | 0.9823 |
| open_lag_2 | high_lag_5 | 0.9823 |
| ema_50 | rolling_median_20 | 0.9823 |
| open | open_lag_3 | 0.9822 |
| ema_5 | ema_20 | 0.9822 |
| open | low_lag_3 | 0.9821 |
| median_price | sma_10 | 0.9820 |
| median_price | rolling_mean_10 | 0.9820 |
| ema_20 | fib_382 | 0.9820 |
| typical_price | sma_10 | 0.9820 |
| typical_price | rolling_mean_10 | 0.9820 |
| ema_20 | bollinger_lower | 0.9820 |
| open_lag_2 | open_lag_5 | 0.9820 |
| weighted_close | sma_10 | 0.9820 |
| weighted_close | rolling_mean_10 | 0.9820 |
| low | sma_10 | 0.9820 |
| low | rolling_mean_10 | 0.9820 |
| open_lag_2 | low_lag_5 | 0.9820 |
| rolling_max_10 | rolling_min_10 | 0.9819 |
| rolling_median_10 | rolling_median_20 | 0.9819 |
| close | sma_10 | 0.9818 |
| close | rolling_mean_10 | 0.9818 |
| high | sma_10 | 0.9818 |
| high | rolling_mean_10 | 0.9818 |
| ema_5 | rolling_min_20 | 0.9818 |
| momentum | price_momentum | 0.9816 |
| rolling_min_5 | static_support | 0.9816 |
| sma_20 | fib_618 | 0.9815 |
| bollinger_middle | fib_618 | 0.9815 |
| rolling_mean_20 | fib_618 | 0.9815 |
| ema_50 | nearest_demand_zone | 0.9814 |
| open | sma_10 | 0.9814 |
| open | rolling_mean_10 | 0.9814 |
| rolling_min_5 | rolling_min_20 | 0.9813 |
| daily_return | pct_return | 0.9812 |
| ema_20 | fib_236 | 0.9811 |
| rolling_max_10 | close_lag_10 | 0.9811 |
| sma_5 | ema_20 | 0.9811 |
| ema_20 | rolling_mean_5 | 0.9811 |
| rolling_max_10 | high_lag_10 | 0.9809 |
| ema_20 | low_lag_3 | 0.9808 |
| sma_5 | static_support | 0.9808 |
| rolling_mean_5 | static_support | 0.9808 |
| sma_20 | low_lag_5 | 0.9808 |
| bollinger_middle | low_lag_5 | 0.9808 |
| rolling_mean_20 | low_lag_5 | 0.9808 |
| ema_20 | close_lag_3 | 0.9808 |
| rolling_max_10 | open_lag_10 | 0.9808 |
| daily_return | log_return | 0.9808 |
| sma_20 | close_lag_5 | 0.9808 |
| bollinger_middle | close_lag_5 | 0.9808 |
| rolling_mean_20 | close_lag_5 | 0.9808 |
| sma_20 | high_lag_5 | 0.9806 |
| bollinger_middle | high_lag_5 | 0.9806 |
| rolling_mean_20 | high_lag_5 | 0.9806 |
| ema_20 | high_lag_3 | 0.9806 |
| rolling_median_20 | static_support | 0.9804 |
| rolling_max_10 | low_lag_10 | 0.9803 |
| sma_20 | open_lag_5 | 0.9803 |
| bollinger_middle | open_lag_5 | 0.9803 |
| rolling_mean_20 | open_lag_5 | 0.9803 |
| ema_20 | open_lag_3 | 0.9803 |
| rolling_max_10 | close_lag_2 | 0.9802 |
| ema_20 | fib_50 | 0.9802 |
| sma_5 | rolling_min_20 | 0.9802 |
| rolling_mean_5 | rolling_min_20 | 0.9802 |
| ema_20 | rolling_median_5 | 0.9802 |
| rolling_max_10 | low_lag_2 | 0.9801 |
| rolling_max_10 | high_lag_2 | 0.9801 |
| rolling_median_20 | static_resistance | 0.9801 |
| rolling_median_20 | fib_618 | 0.9800 |
| rolling_median_20 | rolling_min_20 | 0.9800 |
| rolling_median_20 | rolling_max_20 | 0.9800 |
| rolling_median_5 | static_support | 0.9799 |
| median_price | rolling_median_10 | 0.9798 |
| typical_price | rolling_median_10 | 0.9798 |
| weighted_close | rolling_median_10 | 0.9798 |
| low | rolling_median_10 | 0.9798 |
| rolling_max_10 | open_lag_2 | 0.9797 |
| high | rolling_median_10 | 0.9796 |
| close | rolling_median_10 | 0.9796 |
| fib_786 | fib_1272 | 0.9794 |
| ema_50 | dynamic_support | 0.9794 |
| ema_50 | nearest_support | 0.9794 |
| ema_50 | bollinger_lower | 0.9794 |
| open | rolling_median_10 | 0.9793 |
| rolling_median_5 | rolling_min_20 | 0.9792 |
| nearest_supply_zone | fib_50 | 0.9792 |
| ema_20 | rolling_max_5 | 0.9790 |
| dynamic_resistance | fib_50 | 0.9790 |
| nearest_resistance | fib_50 | 0.9790 |
| rolling_median_20 | low_lag_5 | 0.9787 |
| ema_20 | static_resistance | 0.9787 |
| rolling_median_20 | close_lag_5 | 0.9786 |
| sma_20 | bollinger_upper | 0.9786 |
| bollinger_middle | bollinger_upper | 0.9786 |
| bollinger_upper | rolling_mean_20 | 0.9786 |
| sma_20 | rolling_min_10 | 0.9785 |
| bollinger_middle | rolling_min_10 | 0.9785 |
| rolling_min_10 | rolling_mean_20 | 0.9785 |
| ema_20 | rolling_max_20 | 0.9785 |
| close_lag_10 | fib_382 | 0.9785 |
| rolling_median_20 | high_lag_5 | 0.9785 |
| high_lag_10 | fib_382 | 0.9784 |
| open_lag_10 | fib_382 | 0.9784 |
| low_lag_10 | fib_382 | 0.9784 |
| rolling_median_20 | open_lag_5 | 0.9782 |
| close_lag_10 | fib_50 | 0.9782 |
| high_lag_10 | fib_50 | 0.9781 |
| ema_50 | fib_50 | 0.9781 |
| rolling_min_5 | rolling_max_10 | 0.9781 |
| low_lag_10 | fib_50 | 0.9780 |
| ema_20 | rolling_min_5 | 0.9780 |
| open_lag_10 | fib_50 | 0.9780 |
| low_lag_5 | static_support | 0.9778 |
| close_lag_5 | static_support | 0.9776 |
| high_lag_5 | static_support | 0.9776 |
| close_lag_3 | static_support | 0.9776 |
| low_lag_3 | static_support | 0.9776 |
| close_lag_5 | low_lag_1 | 0.9776 |
| close_lag_5 | high_lag_1 | 0.9775 |
| open_lag_5 | static_support | 0.9775 |
| high_lag_3 | static_support | 0.9774 |
| close_lag_1 | close_lag_5 | 0.9773 |
| open_lag_3 | static_support | 0.9773 |
| high_lag_5 | low_lag_1 | 0.9773 |
| open_lag_5 | low_lag_1 | 0.9773 |
| bollinger_lower | low_lag_5 | 0.9773 |
| high_lag_1 | high_lag_5 | 0.9773 |
| sma_10 | close_lag_10 | 0.9772 |
| rolling_mean_10 | close_lag_10 | 0.9772 |
| open_lag_5 | high_lag_1 | 0.9772 |
| bollinger_lower | close_lag_5 | 0.9771 |
| sma_10 | open_lag_10 | 0.9771 |
| rolling_mean_10 | open_lag_10 | 0.9771 |
| std_20 | variance_20 | 0.9771 |
| variance_20 | rolling_std_20 | 0.9771 |
| std_20 | rolling_var_20 | 0.9771 |
| rolling_std_20 | rolling_var_20 | 0.9771 |
| close_lag_1 | open_lag_5 | 0.9771 |
| sma_10 | high_lag_10 | 0.9771 |
| rolling_mean_10 | high_lag_10 | 0.9771 |
| low_lag_1 | low_lag_5 | 0.9771 |
| bollinger_lower | high_lag_5 | 0.9771 |
| close_lag_5 | open_lag_1 | 0.9771 |
| rolling_min_20 | low_lag_5 | 0.9771 |
| close_lag_1 | high_lag_5 | 0.9771 |
| high_lag_1 | low_lag_5 | 0.9770 |
| bollinger_upper | rolling_median_20 | 0.9770 |
| rolling_min_20 | close_lag_3 | 0.9770 |
| rolling_min_20 | low_lag_3 | 0.9770 |
| bollinger_lower | open_lag_5 | 0.9769 |
| close_lag_1 | low_lag_5 | 0.9769 |
| rolling_min_20 | close_lag_5 | 0.9769 |
| rolling_min_20 | high_lag_5 | 0.9768 |
| open_lag_1 | high_lag_5 | 0.9768 |
| open_lag_1 | open_lag_5 | 0.9768 |
| rolling_min_20 | high_lag_3 | 0.9768 |
| sma_10 | low_lag_10 | 0.9767 |
| rolling_mean_10 | low_lag_10 | 0.9767 |
| ema_20 | low_lag_2 | 0.9767 |
| rolling_min_20 | open_lag_3 | 0.9767 |
| rolling_min_20 | open_lag_5 | 0.9767 |
| low_lag_2 | static_support | 0.9766 |
| ema_20 | close_lag_2 | 0.9766 |
| open_lag_1 | low_lag_5 | 0.9766 |
| close_lag_2 | static_support | 0.9766 |
| high_lag_2 | static_support | 0.9765 |
| ema_20 | high_lag_2 | 0.9764 |
| open_lag_2 | static_support | 0.9764 |
| fib_236 | fib_786 | 0.9763 |
| ema_100 | nearest_demand_zone | 0.9763 |
| open_lag_10 | fib_236 | 0.9761 |
| ema_20 | open_lag_2 | 0.9761 |
| high_lag_10 | fib_236 | 0.9761 |
| low_lag_10 | fib_236 | 0.9761 |
| sma_20 | bollinger_lower | 0.9761 |
| bollinger_middle | bollinger_lower | 0.9761 |
| bollinger_lower | rolling_mean_20 | 0.9761 |
| close_lag_10 | fib_236 | 0.9760 |
| rolling_min_20 | low_lag_2 | 0.9759 |
| rolling_min_20 | close_lag_2 | 0.9759 |
| ema_20 | fib_618 | 0.9758 |
| rolling_min_20 | high_lag_2 | 0.9758 |
| close_lag_10 | fib_618 | 0.9758 |
| rolling_max_10 | low_lag_1 | 0.9757 |
| rolling_min_20 | open_lag_2 | 0.9757 |
| high_lag_10 | fib_618 | 0.9756 |
| rolling_max_10 | close_lag_1 | 0.9756 |
| rolling_max_10 | high_lag_1 | 0.9755 |
| low_lag_10 | fib_618 | 0.9755 |
| ema_5 | bollinger_lower | 0.9754 |
| open_lag_10 | fib_618 | 0.9754 |
| sma_100 | ema_50 | 0.9753 |
| rolling_median_10 | close_lag_10 | 0.9752 |
| rolling_max_10 | open_lag_1 | 0.9751 |
| rolling_median_10 | open_lag_10 | 0.9751 |
| rolling_median_10 | high_lag_10 | 0.9750 |
| ema_100 | fib_236 | 0.9750 |
| ema_10 | close_lag_10 | 0.9750 |
| ema_10 | open_lag_10 | 0.9749 |
| sma_5 | bollinger_lower | 0.9749 |
| bollinger_lower | rolling_mean_5 | 0.9749 |
| ema_10 | high_lag_10 | 0.9749 |
| rolling_median_10 | low_lag_10 | 0.9748 |
| rolling_max_5 | static_support | 0.9746 |
| static_resistance | fib_618 | 0.9745 |
| ema_10 | low_lag_10 | 0.9745 |
| rolling_max_20 | fib_618 | 0.9744 |
| bollinger_lower | rolling_median_5 | 0.9744 |
| bollinger_lower | low_lag_3 | 0.9742 |
| bollinger_lower | close_lag_3 | 0.9742 |
| low_lag_1 | static_support | 0.9741 |
| close_lag_1 | static_support | 0.9741 |
| bollinger_lower | rolling_median_20 | 0.9740 |
| bollinger_lower | high_lag_3 | 0.9740 |
| bollinger_upper | fib_618 | 0.9740 |
| high_lag_1 | static_support | 0.9739 |
| open_lag_1 | static_support | 0.9738 |
| bollinger_lower | open_lag_3 | 0.9737 |
| rolling_max_5 | rolling_min_20 | 0.9737 |
| nearest_demand_zone | fib_618 | 0.9736 |
| rolling_min_20 | low_lag_1 | 0.9735 |
| rolling_min_20 | close_lag_1 | 0.9734 |
| rolling_min_10 | rolling_median_20 | 0.9733 |
| rolling_min_20 | high_lag_1 | 0.9732 |
| ema_10 | ema_50 | 0.9732 |
| rolling_min_20 | open_lag_1 | 0.9732 |
| ema_20 | dynamic_support | 0.9730 |
| ema_20 | nearest_support | 0.9730 |
| rolling_max_20 | fib_786 | 0.9730 |
| static_resistance | fib_786 | 0.9730 |
| bollinger_lower | rolling_min_5 | 0.9730 |
| rolling_median_20 | dynamic_support | 0.9729 |
| rolling_median_20 | nearest_support | 0.9729 |
| rolling_median_20 | nearest_demand_zone | 0.9727 |
| sma_20 | fib_786 | 0.9726 |
| bollinger_middle | fib_786 | 0.9726 |
| rolling_mean_20 | fib_786 | 0.9726 |
| dynamic_support | fib_618 | 0.9726 |
| nearest_support | fib_618 | 0.9726 |
| bollinger_upper | fib_786 | 0.9726 |
| static_resistance | fib_50 | 0.9726 |
| ema_20 | nearest_demand_zone | 0.9726 |
| sma_20 | nearest_demand_zone | 0.9725 |
| bollinger_middle | nearest_demand_zone | 0.9725 |
| rolling_mean_20 | nearest_demand_zone | 0.9725 |
| ema_50 | rolling_min_10 | 0.9725 |
| sma_20 | dynamic_support | 0.9725 |
| bollinger_middle | dynamic_support | 0.9725 |
| rolling_mean_20 | dynamic_support | 0.9725 |
| sma_20 | nearest_support | 0.9725 |
| bollinger_middle | nearest_support | 0.9725 |
| rolling_mean_20 | nearest_support | 0.9725 |
| rolling_max_20 | fib_50 | 0.9724 |
| rolling_max_20 | close_lag_10 | 0.9720 |
| close_lag_10 | static_resistance | 0.9719 |
| ema_100 | fib_382 | 0.9719 |
| bollinger_upper | fib_50 | 0.9719 |
| close_lag_10 | low_lag_5 | 0.9718 |
| low | close_lag_5 | 0.9718 |
| low | open_lag_5 | 0.9717 |
| high_lag_10 | static_resistance | 0.9717 |
| rolling_max_20 | high_lag_10 | 0.9717 |
| median_price | close_lag_5 | 0.9717 |
| open_lag_10 | low_lag_5 | 0.9717 |
| sma_50 | sma_100 | 0.9716 |
| median_price | open_lag_5 | 0.9716 |
| rolling_max_10 | static_support | 0.9716 |
| typical_price | close_lag_5 | 0.9716 |
| rolling_max_20 | low_lag_10 | 0.9715 |
| high_lag_10 | low_lag_5 | 0.9715 |
| low | high_lag_5 | 0.9715 |
| low_lag_5 | low_lag_10 | 0.9715 |
| low_lag_10 | static_resistance | 0.9715 |
| low | low_lag_5 | 0.9715 |
| typical_price | open_lag_5 | 0.9715 |
| weighted_close | close_lag_5 | 0.9715 |
| open_lag_10 | static_resistance | 0.9714 |
| rolling_max_20 | open_lag_10 | 0.9714 |
| weighted_close | open_lag_5 | 0.9714 |
| median_price | high_lag_5 | 0.9714 |
| close_lag_10 | open_lag_5 | 0.9714 |
| ema_20 | low_lag_1 | 0.9714 |
| median_price | low_lag_5 | 0.9714 |
| close_lag_10 | high_lag_5 | 0.9714 |
| bollinger_upper | close_lag_10 | 0.9714 |
| high | close_lag_5 | 0.9713 |
| sma_10 | fib_382 | 0.9713 |
| rolling_mean_10 | fib_382 | 0.9713 |
| typical_price | high_lag_5 | 0.9713 |
| open_lag_5 | open_lag_10 | 0.9713 |
| typical_price | low_lag_5 | 0.9712 |
| open | close_lag_5 | 0.9712 |
| high | open_lag_5 | 0.9712 |
| open_lag_10 | high_lag_5 | 0.9712 |
| ema_20 | close_lag_1 | 0.9712 |
| open | open_lag_5 | 0.9712 |
| weighted_close | low_lag_5 | 0.9712 |
| weighted_close | high_lag_5 | 0.9712 |
| rolling_max_10 | fib_382 | 0.9712 |
| rolling_max_10 | fib_50 | 0.9712 |
| close_lag_5 | close_lag_10 | 0.9711 |
| close | close_lag_5 | 0.9711 |
| open_lag_5 | low_lag_10 | 0.9711 |
| open_lag_5 | high_lag_10 | 0.9711 |
| close | open_lag_5 | 0.9711 |
| ema_10 | fib_382 | 0.9711 |
| high_lag_5 | low_lag_10 | 0.9710 |
| ema_20 | high_lag_1 | 0.9710 |
| high_lag_5 | high_lag_10 | 0.9710 |
| close_lag_5 | open_lag_10 | 0.9710 |
| high | high_lag_5 | 0.9710 |
| high | low_lag_5 | 0.9710 |
| bollinger_upper | low_lag_10 | 0.9710 |
| open | high_lag_5 | 0.9710 |
| open | low_lag_5 | 0.9709 |
| bollinger_upper | high_lag_10 | 0.9709 |
| sma_20 | low_lag_3 | 0.9709 |
| bollinger_middle | low_lag_3 | 0.9709 |
| rolling_mean_20 | low_lag_3 | 0.9709 |
| close_lag_5 | low_lag_10 | 0.9709 |
| close | low_lag_5 | 0.9708 |
| close_lag_5 | high_lag_10 | 0.9708 |
| close | high_lag_5 | 0.9708 |
| bollinger_lower | low_lag_2 | 0.9708 |
| bollinger_upper | open_lag_10 | 0.9708 |
| ema_50 | rolling_mean_10 | 0.9708 |
| sma_10 | ema_50 | 0.9708 |
| bollinger_lower | close_lag_2 | 0.9707 |
| ema_20 | open_lag_1 | 0.9707 |
| bollinger_lower | rolling_max_5 | 0.9707 |
| sma_20 | close_lag_3 | 0.9706 |
| bollinger_middle | close_lag_3 | 0.9706 |
| rolling_mean_20 | close_lag_3 | 0.9706 |
| rolling_median_20 | fib_786 | 0.9706 |
| bollinger_lower | high_lag_2 | 0.9706 |
| sma_10 | fib_236 | 0.9705 |
| rolling_mean_10 | fib_236 | 0.9705 |
| high_lag_10 | static_support | 0.9705 |
| ema_50 | fib_618 | 0.9705 |
| median_price | rolling_max_10 | 0.9705 |
| typical_price | rolling_max_10 | 0.9705 |
| low | rolling_max_10 | 0.9704 |
| weighted_close | rolling_max_10 | 0.9704 |
| sma_20 | high_lag_3 | 0.9704 |
| bollinger_middle | high_lag_3 | 0.9704 |
| rolling_mean_20 | high_lag_3 | 0.9704 |
| median_price | static_support | 0.9704 |
| ema_5 | bollinger_middle | 0.9704 |
| ema_5 | rolling_mean_20 | 0.9704 |
| sma_20 | ema_5 | 0.9704 |
| ema_10 | fib_236 | 0.9704 |
| low | static_support | 0.9704 |
| typical_price | static_support | 0.9703 |
| rolling_max_10 | rolling_min_20 | 0.9703 |
| weighted_close | static_support | 0.9703 |
| bollinger_lower | open_lag_2 | 0.9703 |
| close | rolling_max_10 | 0.9703 |
| high | rolling_max_10 | 0.9702 |
| open_lag_10 | static_support | 0.9701 |
| rolling_min_20 | high_lag_10 | 0.9701 |
| close_lag_10 | static_support | 0.9701 |
| sma_20 | open_lag_3 | 0.9701 |
| bollinger_middle | open_lag_3 | 0.9701 |
| rolling_mean_20 | open_lag_3 | 0.9701 |
| close | static_support | 0.9701 |
| high | static_support | 0.9700 |
| low_lag_10 | static_support | 0.9700 |
| open | static_support | 0.9700 |
| rolling_min_20 | open_lag_10 | 0.9698 |
| rolling_min_20 | close_lag_10 | 0.9698 |
| median_price | rolling_min_20 | 0.9697 |
| typical_price | rolling_min_20 | 0.9697 |
| low | rolling_min_20 | 0.9697 |
| rolling_median_10 | fib_382 | 0.9697 |
| open | rolling_max_10 | 0.9697 |
| weighted_close | rolling_min_20 | 0.9697 |
| rolling_min_20 | low_lag_10 | 0.9697 |
| sma_10 | fib_50 | 0.9696 |
| rolling_mean_10 | fib_50 | 0.9696 |
| close | rolling_min_20 | 0.9695 |
| high | rolling_min_20 | 0.9694 |
| ema_10 | fib_50 | 0.9694 |
| open | rolling_min_20 | 0.9693 |
| ema_50 | rolling_median_10 | 0.9693 |
| rolling_median_10 | fib_236 | 0.9692 |
| static_support | fib_236 | 0.9690 |
| sma_5 | sma_20 | 0.9690 |
| sma_5 | bollinger_middle | 0.9690 |
| sma_20 | rolling_mean_5 | 0.9690 |
| bollinger_middle | rolling_mean_5 | 0.9690 |
| sma_5 | rolling_mean_20 | 0.9690 |
| rolling_mean_5 | rolling_mean_20 | 0.9690 |
| rolling_max_10 | fib_618 | 0.9690 |
| nearest_supply_zone | fib_382 | 0.9688 |
| dynamic_resistance | fib_382 | 0.9685 |
| nearest_resistance | fib_382 | 0.9685 |
| rolling_max_10 | fib_236 | 0.9684 |
| close_lag_10 | fib_786 | 0.9683 |
| static_resistance | fib_382 | 0.9683 |
| ema_100 | dynamic_support | 0.9683 |
| ema_100 | nearest_support | 0.9683 |
| sma_50 | nearest_demand_zone | 0.9681 |
| sma_20 | rolling_median_5 | 0.9681 |
| bollinger_middle | rolling_median_5 | 0.9681 |
| rolling_median_5 | rolling_mean_20 | 0.9681 |
| high_lag_10 | fib_786 | 0.9681 |
| rolling_max_20 | fib_382 | 0.9680 |
| rolling_median_10 | fib_50 | 0.9679 |
| low_lag_10 | fib_786 | 0.9679 |
| ema_20 | bollinger_upper | 0.9678 |
| sma_20 | rolling_max_5 | 0.9678 |
| bollinger_middle | rolling_max_5 | 0.9678 |
| rolling_max_5 | rolling_mean_20 | 0.9678 |
| rolling_min_20 | fib_236 | 0.9678 |
| open_lag_10 | fib_786 | 0.9677 |
| bollinger_upper | fib_382 | 0.9675 |
| sma_50 | fib_236 | 0.9675 |
| dynamic_resistance | fib_1618 | 0.9675 |
| nearest_resistance | fib_1618 | 0.9675 |
| static_support | fib_382 | 0.9673 |
| open_lag_10 | dynamic_support | 0.9673 |
| open_lag_10 | nearest_support | 0.9673 |
| high_lag_5 | fib_382 | 0.9673 |
| low_lag_10 | dynamic_support | 0.9672 |
| low_lag_10 | nearest_support | 0.9672 |
| high_lag_10 | dynamic_support | 0.9671 |
| high_lag_10 | nearest_support | 0.9671 |
| open_lag_10 | nearest_demand_zone | 0.9671 |
| nearest_supply_zone | fib_1618 | 0.9670 |
| close_lag_5 | fib_382 | 0.9670 |
| low_lag_10 | nearest_demand_zone | 0.9670 |
| high_lag_10 | nearest_demand_zone | 0.9670 |
| close_lag_10 | dynamic_support | 0.9669 |
| close_lag_10 | nearest_support | 0.9669 |
| low_lag_5 | fib_382 | 0.9669 |
| close_lag_10 | nearest_demand_zone | 0.9668 |
| ema_20 | ema_100 | 0.9668 |
| open_lag_5 | fib_382 | 0.9666 |
| rolling_max_10 | rolling_max_20 | 0.9666 |
| rolling_min_10 | high_lag_10 | 0.9665 |
| high_lag_5 | fib_236 | 0.9665 |
| ema_50 | close_lag_10 | 0.9665 |
| ema_50 | open_lag_10 | 0.9664 |
| ema_50 | low_lag_10 | 0.9664 |
| rolling_min_10 | close_lag_10 | 0.9664 |
| rolling_min_10 | open_lag_10 | 0.9664 |
| rolling_max_10 | static_resistance | 0.9663 |
| close_lag_5 | fib_236 | 0.9663 |
| rolling_median_20 | low_lag_3 | 0.9662 |
| sma_50 | dynamic_support | 0.9662 |
| sma_50 | nearest_support | 0.9662 |
| low_lag_5 | fib_236 | 0.9662 |
| ema_50 | high_lag_10 | 0.9661 |
| rolling_min_20 | fib_382 | 0.9661 |
| open_lag_5 | fib_236 | 0.9659 |
| rolling_median_20 | close_lag_3 | 0.9659 |
| sma_10 | fib_618 | 0.9658 |
| rolling_mean_10 | fib_618 | 0.9658 |
| rolling_min_10 | low_lag_10 | 0.9658 |
| bollinger_lower | low_lag_1 | 0.9658 |
| bollinger_lower | close_lag_1 | 0.9658 |
| high_lag_5 | fib_50 | 0.9656 |
| bollinger_lower | high_lag_1 | 0.9656 |
| rolling_median_20 | high_lag_3 | 0.9656 |
| std_10 | variance_10 | 0.9655 |
| variance_10 | rolling_std_10 | 0.9655 |
| std_10 | rolling_var_10 | 0.9655 |
| rolling_std_10 | rolling_var_10 | 0.9655 |
| ema_10 | fib_618 | 0.9655 |
| close_lag_5 | fib_50 | 0.9654 |
| rolling_median_20 | open_lag_3 | 0.9653 |
| bollinger_lower | open_lag_1 | 0.9653 |
| sma_20 | rolling_min_5 | 0.9653 |
| bollinger_middle | rolling_min_5 | 0.9653 |
| rolling_min_5 | rolling_mean_20 | 0.9653 |
| low_lag_5 | fib_50 | 0.9652 |
| ema_100 | fib_50 | 0.9652 |
| ema_20 | fib_786 | 0.9652 |
| bollinger_lower | rolling_max_10 | 0.9652 |
| ema_100 | rolling_min_20 | 0.9651 |
| static_support | dynamic_support | 0.9650 |
| static_support | nearest_support | 0.9650 |
| low | ema_20 | 0.9649 |
| open_lag_5 | fib_50 | 0.9649 |
| median_price | ema_20 | 0.9649 |
| typical_price | ema_20 | 0.9649 |
| weighted_close | ema_20 | 0.9648 |
| sma_100 | nearest_demand_zone | 0.9647 |
| ema_5 | rolling_median_20 | 0.9646 |
| close | ema_20 | 0.9646 |
| ema_10 | dynamic_support | 0.9646 |
| ema_10 | nearest_support | 0.9646 |
| sma_20 | low_lag_2 | 0.9645 |
| bollinger_middle | low_lag_2 | 0.9645 |
| rolling_mean_20 | low_lag_2 | 0.9645 |
| high | ema_20 | 0.9645 |
| sma_10 | dynamic_support | 0.9645 |
| rolling_mean_10 | dynamic_support | 0.9645 |
| sma_10 | nearest_support | 0.9645 |
| rolling_mean_10 | nearest_support | 0.9645 |
| static_support | nearest_demand_zone | 0.9645 |
| bollinger_lower | high_lag_10 | 0.9644 |
| swing_high | supply_zone | 0.9643 |
| bollinger_lower | open_lag_10 | 0.9642 |
| sma_20 | close_lag_2 | 0.9642 |
| bollinger_middle | close_lag_2 | 0.9642 |
| rolling_mean_20 | close_lag_2 | 0.9642 |
| open | ema_20 | 0.9642 |
| bollinger_lower | close_lag_10 | 0.9641 |
| sma_20 | high_lag_2 | 0.9640 |
| bollinger_middle | high_lag_2 | 0.9640 |
| rolling_mean_20 | high_lag_2 | 0.9640 |
| bollinger_lower | low_lag_10 | 0.9640 |
| sma_50 | ema_20 | 0.9639 |
| rolling_min_20 | nearest_demand_zone | 0.9638 |
| rolling_median_10 | fib_618 | 0.9638 |
| rolling_max_20 | nearest_supply_zone | 0.9638 |
| vwap | nearest_demand_zone | 0.9637 |
| rolling_min_20 | dynamic_support | 0.9637 |
| rolling_min_20 | nearest_support | 0.9637 |
| rolling_median_10 | dynamic_support | 0.9637 |
| rolling_median_10 | nearest_support | 0.9637 |
| sma_20 | open_lag_2 | 0.9637 |
| bollinger_middle | open_lag_2 | 0.9637 |
| rolling_mean_20 | open_lag_2 | 0.9637 |
| static_resistance | nearest_supply_zone | 0.9636 |
| rolling_max_20 | dynamic_resistance | 0.9636 |
| rolling_max_20 | nearest_resistance | 0.9636 |
| bollinger_upper | nearest_supply_zone | 0.9636 |
| static_resistance | dynamic_resistance | 0.9634 |
| static_resistance | nearest_resistance | 0.9634 |
| static_support | fib_50 | 0.9633 |
| bollinger_upper | dynamic_resistance | 0.9633 |
| bollinger_upper | nearest_resistance | 0.9633 |
| ema_10 | nearest_demand_zone | 0.9633 |
| sma_5 | rolling_median_20 | 0.9633 |
| rolling_mean_5 | rolling_median_20 | 0.9633 |
| sma_10 | nearest_demand_zone | 0.9632 |
| rolling_mean_10 | nearest_demand_zone | 0.9632 |
| fib_618 | fib_1272 | 0.9632 |
| sma_50 | fib_382 | 0.9631 |
| rolling_max_5 | rolling_median_20 | 0.9631 |
| ema_100 | static_support | 0.9630 |
| ema_10 | static_resistance | 0.9627 |
| ema_10 | rolling_max_20 | 0.9627 |
| vwap | fib_236 | 0.9625 |
| rolling_median_5 | rolling_median_20 | 0.9624 |
| bollinger_lower | fib_236 | 0.9623 |
| ema_50 | close_lag_5 | 0.9623 |
| vwap | dynamic_support | 0.9622 |
| vwap | nearest_support | 0.9622 |
| ema_50 | low_lag_5 | 0.9621 |
| rolling_median_10 | nearest_demand_zone | 0.9621 |
| sma_200 | ema_50 | 0.9621 |
| rolling_min_20 | fib_50 | 0.9621 |
| rolling_max_10 | fib_786 | 0.9620 |
| sma_20 | ema_100 | 0.9620 |
| ema_100 | bollinger_middle | 0.9620 |
| ema_100 | rolling_mean_20 | 0.9620 |
| bollinger_lower | dynamic_support | 0.9620 |
| bollinger_lower | nearest_support | 0.9620 |
| rolling_min_10 | fib_382 | 0.9619 |
| rolling_min_10 | fib_236 | 0.9618 |
| high_lag_5 | fib_618 | 0.9618 |
| ema_50 | high_lag_5 | 0.9617 |
| bollinger_lower | nearest_demand_zone | 0.9617 |
| ema_100 | bollinger_lower | 0.9616 |
| close_lag_5 | fib_618 | 0.9615 |
| ema_50 | open_lag_5 | 0.9615 |
| low_lag_5 | fib_618 | 0.9614 |
| sma_10 | rolling_max_20 | 0.9611 |
| rolling_mean_10 | rolling_max_20 | 0.9611 |
| open_lag_5 | fib_618 | 0.9611 |
| sma_10 | static_resistance | 0.9610 |
| rolling_mean_10 | static_resistance | 0.9610 |
| high_lag_5 | dynamic_support | 0.9608 |
| high_lag_5 | nearest_support | 0.9608 |
| close_lag_5 | dynamic_support | 0.9605 |
| close_lag_5 | nearest_support | 0.9605 |
| low_lag_5 | dynamic_support | 0.9604 |
| low_lag_5 | nearest_support | 0.9604 |
| open_lag_5 | dynamic_support | 0.9602 |
| open_lag_5 | nearest_support | 0.9602 |
| ema_5 | ema_50 | 0.9602 |
| static_resistance | fib_236 | 0.9601 |
| median_price | bollinger_lower | 0.9597 |
| typical_price | bollinger_lower | 0.9597 |
| rolling_max_20 | fib_236 | 0.9597 |
| low | bollinger_lower | 0.9597 |
| weighted_close | bollinger_lower | 0.9597 |
| rolling_max_10 | dynamic_support | 0.9596 |
| rolling_max_10 | nearest_support | 0.9596 |
| rolling_min_10 | fib_50 | 0.9596 |
| vwap | fib_382 | 0.9596 |
| close | bollinger_lower | 0.9595 |
| high | bollinger_lower | 0.9594 |
| sma_20 | sma_50 | 0.9594 |
| sma_50 | bollinger_middle | 0.9594 |
| sma_50 | rolling_mean_20 | 0.9594 |
| ema_100 | rolling_median_20 | 0.9594 |
| high_lag_5 | nearest_demand_zone | 0.9594 |
| open_lag_10 | low_lag_3 | 0.9593 |
| close_lag_5 | nearest_demand_zone | 0.9591 |
| open | bollinger_lower | 0.9591 |
| bollinger_upper | fib_236 | 0.9591 |
| close_lag_10 | low_lag_3 | 0.9589 |
| low_lag_5 | nearest_demand_zone | 0.9589 |
| high_lag_10 | low_lag_3 | 0.9588 |
| close_lag_3 | open_lag_10 | 0.9588 |
| open_lag_10 | high_lag_3 | 0.9588 |
| ema_50 | rolling_max_20 | 0.9588 |
| bollinger_upper | rolling_max_10 | 0.9588 |
| rolling_median_20 | low_lag_2 | 0.9587 |
| ema_50 | static_resistance | 0.9587 |
| sma_50 | rolling_median_20 | 0.9587 |
| open_lag_3 | open_lag_10 | 0.9586 |
| open_lag_5 | nearest_demand_zone | 0.9586 |
| low_lag_3 | low_lag_10 | 0.9585 |
| close_lag_3 | close_lag_10 | 0.9585 |
| close_lag_10 | high_lag_3 | 0.9585 |
| rolling_min_5 | rolling_median_20 | 0.9584 |
| ema_50 | rolling_max_10 | 0.9584 |
| close_lag_3 | high_lag_10 | 0.9584 |
| rolling_median_20 | close_lag_2 | 0.9584 |
| rolling_max_10 | nearest_demand_zone | 0.9584 |
| sma_5 | ema_50 | 0.9584 |
| ema_50 | rolling_mean_5 | 0.9584 |
| high_lag_3 | high_lag_10 | 0.9584 |
| sma_50 | rolling_min_20 | 0.9583 |
| close_lag_10 | open_lag_3 | 0.9583 |
| bollinger_lower | fib_382 | 0.9582 |
| open_lag_3 | high_lag_10 | 0.9582 |
| close_lag_3 | low_lag_10 | 0.9581 |
| high_lag_3 | low_lag_10 | 0.9581 |
| rolling_median_20 | high_lag_2 | 0.9581 |
| rolling_median_10 | rolling_max_20 | 0.9580 |
| rolling_median_10 | static_resistance | 0.9579 |
| open_lag_3 | low_lag_10 | 0.9579 |
| ema_50 | rolling_median_5 | 0.9578 |
| ema_50 | rolling_min_5 | 0.9578 |
| rolling_median_20 | open_lag_2 | 0.9577 |
| ema_5 | open_lag_10 | 0.9577 |
| ema_5 | high_lag_10 | 0.9576 |
| ema_5 | close_lag_10 | 0.9576 |
| sma_20 | low_lag_1 | 0.9574 |
| bollinger_middle | low_lag_1 | 0.9574 |
| rolling_mean_20 | low_lag_1 | 0.9574 |
| rolling_min_10 | dynamic_support | 0.9573 |
| rolling_min_10 | nearest_support | 0.9573 |
| close_lag_20 | static_resistance | 0.9573 |
| high_lag_20 | static_resistance | 0.9573 |
| rolling_max_5 | open_lag_10 | 0.9572 |
| open_lag_20 | static_resistance | 0.9570 |
| ema_5 | low_lag_10 | 0.9570 |
| sma_20 | close_lag_1 | 0.9570 |
| bollinger_middle | close_lag_1 | 0.9570 |
| rolling_mean_20 | close_lag_1 | 0.9570 |
| rolling_max_5 | close_lag_10 | 0.9569 |
| rolling_min_10 | nearest_demand_zone | 0.9569 |
| rolling_max_5 | high_lag_10 | 0.9569 |
| static_support | fib_618 | 0.9569 |
| sma_20 | high_lag_1 | 0.9568 |
| bollinger_middle | high_lag_1 | 0.9568 |
| rolling_mean_20 | high_lag_1 | 0.9568 |
| nearest_demand_zone | fib_786 | 0.9567 |
| ema_50 | low_lag_3 | 0.9567 |
| ema_50 | close_lag_3 | 0.9567 |
| rolling_max_20 | close_lag_20 | 0.9566 |
| rolling_max_20 | high_lag_20 | 0.9566 |
| sma_50 | fib_50 | 0.9565 |
| rolling_max_5 | low_lag_10 | 0.9565 |
| low_lag_20 | static_resistance | 0.9564 |
| sma_20 | open_lag_1 | 0.9564 |
| bollinger_middle | open_lag_1 | 0.9564 |
| rolling_mean_20 | open_lag_1 | 0.9564 |
| sma_10 | fib_786 | 0.9564 |
| rolling_mean_10 | fib_786 | 0.9564 |
| sma_50 | static_support | 0.9564 |
| rolling_max_20 | open_lag_20 | 0.9564 |
| sma_5 | open_lag_10 | 0.9561 |
| rolling_mean_5 | open_lag_10 | 0.9561 |
| ema_50 | high_lag_3 | 0.9560 |
| ema_10 | fib_786 | 0.9559 |
| high_lag_3 | fib_382 | 0.9559 |
| sma_5 | high_lag_10 | 0.9559 |
| rolling_mean_5 | high_lag_10 | 0.9559 |
| sma_5 | close_lag_10 | 0.9559 |
| rolling_mean_5 | close_lag_10 | 0.9559 |
| low_lag_3 | fib_382 | 0.9559 |
| ema_50 | open_lag_3 | 0.9558 |
| rolling_max_20 | low_lag_20 | 0.9557 |
| high_lag_3 | fib_236 | 0.9557 |
| close_lag_3 | fib_382 | 0.9556 |
| rolling_min_20 | fib_618 | 0.9556 |
| low_lag_3 | fib_236 | 0.9556 |
| sma_50 | ema_200 | 0.9555 |
| sma_5 | low_lag_10 | 0.9554 |
| rolling_mean_5 | low_lag_10 | 0.9554 |
| open_lag_3 | fib_382 | 0.9553 |
| close_lag_3 | fib_236 | 0.9553 |
| rolling_min_10 | fib_618 | 0.9552 |
| open_lag_3 | fib_236 | 0.9552 |
| rolling_median_5 | open_lag_10 | 0.9551 |
| bollinger_upper | close_lag_20 | 0.9550 |
| ema_5 | fib_382 | 0.9550 |
| sma_100 | fib_236 | 0.9550 |
| ema_100 | fib_618 | 0.9549 |
| rolling_median_5 | high_lag_10 | 0.9549 |
| rolling_median_5 | close_lag_10 | 0.9549 |
| vwap | fib_50 | 0.9548 |
| ema_5 | fib_236 | 0.9548 |
| bollinger_upper | open_lag_20 | 0.9548 |
| bollinger_upper | high_lag_20 | 0.9547 |
| sma_50 | bollinger_lower | 0.9546 |
| ema_20 | vwap | 0.9546 |
| ema_50 | fib_786 | 0.9544 |
| rolling_median_5 | low_lag_10 | 0.9544 |
| dynamic_support | fib_786 | 0.9544 |
| nearest_support | fib_786 | 0.9544 |
| rolling_max_20 | low_lag_5 | 0.9543 |
| rolling_max_20 | close_lag_5 | 0.9543 |
| bollinger_upper | low_lag_20 | 0.9543 |
| rolling_max_20 | high_lag_5 | 0.9542 |
| low_lag_5 | static_resistance | 0.9542 |
| rolling_median_10 | fib_786 | 0.9541 |
| high_lag_5 | static_resistance | 0.9541 |
| close_lag_5 | static_resistance | 0.9541 |
| high_lag_3 | fib_50 | 0.9539 |
| sma_20 | nearest_supply_zone | 0.9539 |
| bollinger_middle | nearest_supply_zone | 0.9539 |
| rolling_mean_20 | nearest_supply_zone | 0.9539 |
| low_lag_3 | fib_50 | 0.9539 |
| rolling_max_20 | open_lag_5 | 0.9538 |
| open_lag_5 | static_resistance | 0.9537 |
| rolling_max_5 | fib_382 | 0.9537 |
| sma_20 | dynamic_resistance | 0.9537 |
| bollinger_middle | dynamic_resistance | 0.9537 |
| rolling_mean_20 | dynamic_resistance | 0.9537 |
| sma_20 | nearest_resistance | 0.9537 |
| bollinger_middle | nearest_resistance | 0.9537 |
| rolling_mean_20 | nearest_resistance | 0.9537 |
| close_lag_3 | fib_50 | 0.9536 |
| sma_5 | fib_382 | 0.9536 |
| rolling_mean_5 | fib_382 | 0.9536 |
| nearest_supply_zone | fib_236 | 0.9536 |
| sma_5 | fib_236 | 0.9534 |
| rolling_mean_5 | fib_236 | 0.9534 |
| ema_50 | rolling_max_5 | 0.9534 |
| rolling_max_5 | fib_236 | 0.9534 |
| volume | volume_ratio | 0.9534 |
| open_lag_3 | fib_50 | 0.9532 |
| dynamic_resistance | fib_236 | 0.9531 |
| nearest_resistance | fib_236 | 0.9531 |
| ema_50 | close_lag_2 | 0.9531 |
| ema_50 | low_lag_2 | 0.9530 |
| rolling_median_5 | fib_382 | 0.9530 |
| rolling_median_5 | fib_236 | 0.9529 |
| ema_5 | fib_50 | 0.9529 |
| ema_50 | high_lag_2 | 0.9525 |
| high_lag_5 | fib_786 | 0.9524 |
| bollinger_lower | fib_50 | 0.9523 |
| ema_50 | open_lag_2 | 0.9522 |
| close_lag_5 | fib_786 | 0.9521 |
| close_lag_10 | nearest_supply_zone | 0.9520 |
| low_lag_5 | fib_786 | 0.9520 |
| static_support | static_resistance | 0.9520 |
| close_lag_10 | dynamic_resistance | 0.9519 |
| close_lag_10 | nearest_resistance | 0.9519 |
| open_lag_10 | low_lag_2 | 0.9517 |
| rolling_max_5 | fib_50 | 0.9517 |
| high_lag_10 | nearest_supply_zone | 0.9517 |
| rolling_min_20 | static_resistance | 0.9516 |
| open_lag_5 | fib_786 | 0.9516 |
| close_lag_10 | low_lag_2 | 0.9516 |
| sma_50 | low_lag_20 | 0.9515 |
| high_lag_10 | low_lag_2 | 0.9515 |
| close_lag_2 | open_lag_10 | 0.9515 |
| high_lag_10 | dynamic_resistance | 0.9515 |
| high_lag_10 | nearest_resistance | 0.9515 |
| open_lag_10 | high_lag_2 | 0.9514 |
| sma_5 | fib_50 | 0.9514 |
| rolling_mean_5 | fib_50 | 0.9514 |
| rolling_min_5 | open_lag_10 | 0.9514 |
| low_lag_10 | nearest_supply_zone | 0.9514 |
| sma_50 | open_lag_20 | 0.9513 |
| rolling_max_20 | static_support | 0.9513 |
| close_lag_2 | high_lag_10 | 0.9513 |
| close_lag_2 | close_lag_10 | 0.9513 |
| rolling_min_5 | high_lag_10 | 0.9513 |
| high_lag_2 | high_lag_10 | 0.9513 |
| sma_50 | close_lag_20 | 0.9513 |
| close_lag_10 | high_lag_2 | 0.9513 |
| rolling_min_5 | close_lag_10 | 0.9512 |
| sma_50 | high_lag_20 | 0.9512 |
| open_lag_10 | nearest_supply_zone | 0.9512 |
| low_lag_10 | dynamic_resistance | 0.9512 |
| low_lag_10 | nearest_resistance | 0.9512 |
| rolling_median_20 | nearest_supply_zone | 0.9511 |
| open_lag_2 | open_lag_10 | 0.9510 |
| high_lag_3 | dynamic_support | 0.9510 |
| high_lag_3 | nearest_support | 0.9510 |
| rolling_max_20 | rolling_min_20 | 0.9510 |
| low_lag_2 | low_lag_10 | 0.9510 |
| open_lag_10 | dynamic_resistance | 0.9510 |
| open_lag_10 | nearest_resistance | 0.9510 |
| rolling_median_20 | dynamic_resistance | 0.9509 |
| rolling_median_20 | nearest_resistance | 0.9509 |
| low_lag_3 | dynamic_support | 0.9509 |
| low_lag_3 | nearest_support | 0.9509 |
| close_lag_10 | open_lag_2 | 0.9509 |
| open_lag_2 | high_lag_10 | 0.9509 |
| rolling_median_5 | fib_50 | 0.9508 |
| close_lag_2 | low_lag_10 | 0.9507 |
| open_lag_3 | dynamic_support | 0.9507 |
| open_lag_3 | nearest_support | 0.9507 |
| sma_100 | fib_382 | 0.9507 |
| rolling_min_5 | low_lag_10 | 0.9507 |
| close_lag_3 | dynamic_support | 0.9507 |
| close_lag_3 | nearest_support | 0.9507 |
| high_lag_2 | low_lag_10 | 0.9506 |
| ema_50 | bollinger_upper | 0.9506 |
| rolling_median_20 | low_lag_1 | 0.9506 |
| sma_100 | dynamic_support | 0.9504 |
| sma_100 | nearest_support | 0.9504 |
| ema_5 | dynamic_support | 0.9503 |
| ema_5 | nearest_support | 0.9503 |
| open_lag_2 | low_lag_10 | 0.9503 |
| rolling_median_20 | close_lag_1 | 0.9501 |
| vwap | rolling_mean_20 | 0.9501 |
| sma_20 | vwap | 0.9501 |
| bollinger_middle | vwap | 0.9501 |
| sma_20 | high_lag_20 | 0.9500 |
| bollinger_middle | high_lag_20 | 0.9500 |
| rolling_mean_20 | high_lag_20 | 0.9500 |

### Low-Variance Features
death_cross, golden_cross, is_marubozu, is_price_outlier

### Duplicate Feature Groups
- is_price_outlier, is_marubozu
- price_diff, open_close_diff
- change_of_character, trend_reversal_signal