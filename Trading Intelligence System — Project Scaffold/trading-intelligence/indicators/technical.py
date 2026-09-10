"""Technical indicators — all calculations done in Python, not by LLM."""

from __future__ import annotations

import numpy as np
import pandas as pd


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """Calculate Relative Strength Index (RSI).

    Args:
        series: Price series (typically close prices).
        period: Lookback period (default 14).

    Returns:
        RSI values (0-100).
    """
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = (-delta).where(delta < 0, 0.0)

    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def ema(series: pd.Series, period: int) -> pd.Series:
    """Calculate Exponential Moving Average (EMA).

    Args:
        series: Price series.
        period: EMA period.

    Returns:
        EMA values.
    """
    return series.ewm(span=period, adjust=False).mean()


def macd(
    series: pd.Series,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Calculate MACD (Moving Average Convergence Divergence).

    Args:
        series: Price series.
        fast: Fast EMA period (default 12).
        slow: Slow EMA period (default 26).
        signal: Signal line EMA period (default 9).

    Returns:
        Tuple of (MACD line, signal line, histogram).
    """
    ema_fast = ema(series, fast)
    ema_slow = ema(series, slow)
    macd_line = ema_fast - ema_slow
    signal_line = ema(macd_line, signal)
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def atr(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    period: int = 14,
) -> pd.Series:
    """Calculate Average True Range (ATR).

    Args:
        high: High prices.
        low: Low prices.
        close: Close prices.
        period: Lookback period (default 14).

    Returns:
        ATR values.
    """
    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.rolling(window=period, min_periods=period).mean()


def bollinger_bands(
    series: pd.Series,
    period: int = 20,
    num_std: float = 2.0,
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Calculate Bollinger Bands.

    Args:
        series: Price series.
        period: Moving average period (default 20).
        num_std: Number of standard deviations (default 2).

    Returns:
        Tuple of (upper band, middle band, lower band).
    """
    middle = series.rolling(window=period).mean()
    std = series.rolling(window=period).std()
    upper = middle + num_std * std
    lower = middle - num_std * std
    return upper, middle, lower


def vwap(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    volume: pd.Series,
) -> pd.Series:
    """Calculate Volume Weighted Average Price (VWAP).

    Args:
        high: High prices.
        low: Low prices.
        close: Close prices.
        volume: Volume series.

    Returns:
        VWAP values (cumulative).
    """
    typical_price = (high + low + close) / 3
    return (typical_price * volume).cumsum() / volume.cumsum()


def volatility(series: pd.Series, period: int = 20) -> pd.Series:
    """Calculate rolling volatility (annualized standard deviation of returns).

    Args:
        series: Price series.
        period: Lookback period (default 20).

    Returns:
        Annualized volatility values.
    """
    returns = series.pct_change()
    return returns.rolling(window=period).std() * np.sqrt(252)


def support_resistance(
    high: pd.Series,
    low: pd.Series,
    window: int = 20,
) -> tuple[float | None, float | None]:
    """Calculate simple support and resistance levels.

    Args:
        high: High prices.
        low: Low prices.
        window: Lookback window (default 20).

    Returns:
        Tuple of (resistance, support) — most recent levels.
    """
    if len(high) < window or len(low) < window:
        return None, None

    resistance = float(high.tail(window).max())
    support = float(low.tail(window).min())
    return support, resistance


def calculate_all(
    df: pd.DataFrame,
    timeframe: str = "1h",
) -> dict[str, float | None]:
    """Calculate all technical indicators for a DataFrame.

    Expects columns: open, high, low, close, volume.

    Args:
        df: OHLCV DataFrame.
        timeframe: Timeframe string for logging.

    Returns:
        Dict with all indicator values (latest).
    """
    if len(df) < 200:
        return {}

    close = df["close"]
    high = df["high"]
    low = df["low"]
    volume = df["volume"]

    rsi_val = rsi(close)
    macd_line, signal_line, hist = macd(close)
    ema20 = ema(close, 20)
    ema50 = ema(close, 50)
    ema200 = ema(close, 200)
    atr_val = atr(high, low, close)
    bb_upper, bb_middle, bb_lower = bollinger_bands(close)
    vwap_val = vwap(high, low, close, volume)
    vol = volatility(close)
    sup, res = support_resistance(high, low)

    return {
        "rsi_14": float(rsi_val.iloc[-1]) if not rsi_val.iloc[-1] != rsi_val.iloc[-1] else None,
        "macd": float(macd_line.iloc[-1]) if macd_line.iloc[-1] == macd_line.iloc[-1] else None,
        "macd_signal": float(signal_line.iloc[-1]) if signal_line.iloc[-1] == signal_line.iloc[-1] else None,
        "macd_hist": float(hist.iloc[-1]) if hist.iloc[-1] == hist.iloc[-1] else None,
        "ema_20": float(ema20.iloc[-1]) if ema20.iloc[-1] == ema20.iloc[-1] else None,
        "ema_50": float(ema50.iloc[-1]) if ema50.iloc[-1] == ema50.iloc[-1] else None,
        "ema_200": float(ema200.iloc[-1]) if ema200.iloc[-1] == ema200.iloc[-1] else None,
        "atr_14": float(atr_val.iloc[-1]) if atr_val.iloc[-1] == atr_val.iloc[-1] else None,
        "bollinger_upper": float(bb_upper.iloc[-1]) if bb_upper.iloc[-1] == bb_upper.iloc[-1] else None,
        "bollinger_middle": float(bb_middle.iloc[-1]) if bb_middle.iloc[-1] == bb_middle.iloc[-1] else None,
        "bollinger_lower": float(bb_lower.iloc[-1]) if bb_lower.iloc[-1] == bb_lower.iloc[-1] else None,
        "vwap": float(vwap_val.iloc[-1]) if vwap_val.iloc[-1] == vwap_val.iloc[-1] else None,
        "volume": float(volume.iloc[-1]) if volume.iloc[-1] == volume.iloc[-1] else None,
        "volatility": float(vol.iloc[-1]) if vol.iloc[-1] == vol.iloc[-1] else None,
        "support": sup,
        "resistance": res,
    }
