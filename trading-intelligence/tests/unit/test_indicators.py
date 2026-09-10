"""Tests for technical indicators."""

import numpy as np
import pandas as pd
import pytest

from indicators.technical import (
    rsi,
    ema,
    macd,
    atr,
    bollinger_bands,
    vwap,
    volatility,
    calculate_all,
)


@pytest.fixture
def sample_ohlcv() -> pd.DataFrame:
    """Generate sample OHLCV data for testing."""
    np.random.seed(42)
    n = 250
    close = pd.Series(np.random.randn(n).cumsum() + 100, name="close")
    high = close + np.random.uniform(0.5, 2.0, n)
    low = close - np.random.uniform(0.5, 2.0, n)
    open_ = close.shift(1).fillna(close.iloc[0])
    volume = pd.Series(np.random.randint(1000, 50000, n), name="volume")
    return pd.DataFrame({
        "open": open_,
        "high": high,
        "low": low,
        "close": close,
        "volume": volume,
    })


def test_rsi_range(sample_ohlcv: pd.DataFrame) -> None:
    """RSI should be between 0 and 100."""
    rsi_values = rsi(sample_ohlcv["close"])
    valid = rsi_values.dropna()
    assert (valid >= 0).all() and (valid <= 100).all()


def test_ema_length(sample_ohlcv: pd.DataFrame) -> None:
    """EMA should have same length as input."""
    ema20 = ema(sample_ohlcv["close"], 20)
    assert len(ema20) == len(sample_ohlcv)


def test_macd_components(sample_ohlcv: pd.DataFrame) -> None:
    """MACD should return 3 components."""
    macd_line, signal_line, hist = macd(sample_ohlcv["close"])
    assert len(macd_line) == len(sample_ohlcv)
    assert len(signal_line) == len(sample_ohlcv)
    assert len(hist) == len(sample_ohlcv)


def test_atr_positive(sample_ohlcv: pd.DataFrame) -> None:
    """ATR should be non-negative."""
    atr_val = atr(sample_ohlcv["high"], sample_ohlcv["low"], sample_ohlcv["close"])
    valid = atr_val.dropna()
    assert (valid >= 0).all()


def test_bollinger_bands_order(sample_ohlcv: pd.DataFrame) -> None:
    """Upper band should be >= middle band >= lower band."""
    upper, middle, lower = bollinger_bands(sample_ohlcv["close"])
    valid_idx = upper.dropna().index
    assert (upper[valid_idx] >= middle[valid_idx]).all()
    assert (middle[valid_idx] >= lower[valid_idx]).all()


def test_vwap_positive(sample_ohlcv: pd.DataFrame) -> None:
    """VWAP should be positive for positive prices."""
    vwap_val = vwap(
        sample_ohlcv["high"],
        sample_ohlcv["low"],
        sample_ohlcv["close"],
        sample_ohlcv["volume"],
    )
    assert (vwap_val.dropna() > 0).all()


def test_calculate_all_returns_dict(sample_ohlcv: pd.DataFrame) -> None:
    """calculate_all should return a dict with expected keys."""
    result = calculate_all(sample_ohlcv)
    assert isinstance(result, dict)
    assert "rsi_14" in result
    assert "ema_20" in result
    assert "ema_50" in result
    assert "ema_200" in result


def test_calculate_all_empty_df() -> None:
    """calculate_all should return empty dict for insufficient data."""
    df = pd.DataFrame({
        "open": [1, 2, 3],
        "high": [2, 3, 4],
        "low": [0, 1, 2],
        "close": [1, 2, 3],
        "volume": [100, 200, 300],
    })
    result = calculate_all(df)
    assert result == {}


def test_volatility_non_negative(sample_ohlcv: pd.DataFrame) -> None:
    """Volatility should be non-negative."""
    vol = volatility(sample_ohlcv["close"])
    valid = vol.dropna()
    assert (valid >= 0).all()
