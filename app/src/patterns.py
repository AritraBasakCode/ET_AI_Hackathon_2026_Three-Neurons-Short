import pandas as pd
import numpy as np


def _local_extrema(series: pd.Series, order: int = 5):
    arr = series.values
    maxima, minima = [], []
    for i in range(order, len(arr) - order):
        window = arr[i - order:i + order + 1]
        if arr[i] == np.max(window):
            maxima.append(i)
        if arr[i] == np.min(window):
            minima.append(i)
    return maxima, minima


def detect_breakout_20d(df: pd.DataFrame) -> dict:
    d = df.copy()
    d["PREV_20D_HIGH"] = d["High"].rolling(20).max().shift(1)
    d["VOL20"] = d["Volume"].rolling(20).mean()

    if len(d) < 30:
        return {"triggered": False, "pattern": "20D_BREAKOUT"}

    last = d.iloc[-1]
    triggered = bool(
        pd.notna(last["PREV_20D_HIGH"])
        and last["Close"] > last["PREV_20D_HIGH"]
        and last["Volume"] > 1.2 * last["VOL20"]
    )

    return {
        "triggered": triggered,
        "pattern": "20D_BREAKOUT",
        "signal_time": str(d.index[-1].date()),
        "meta": {
            "close": float(last["Close"]),
            "prev_20d_high": float(last["PREV_20D_HIGH"]) if pd.notna(last["PREV_20D_HIGH"]) else None,
            "volume": float(last["Volume"]),
            "vol20": float(last["VOL20"]) if pd.notna(last["VOL20"]) else None,
        }
    }


def detect_reversal_rsi(df: pd.DataFrame) -> dict:
    if len(df) < 25:
        return {"triggered": False, "pattern": "RSI_REVERSAL"}

    d = df.copy()
    prev = d.iloc[-2]
    last = d.iloc[-1]

    triggered = bool(
        pd.notna(prev["RSI14"])
        and pd.notna(last["RSI14"])
        and prev["RSI14"] < 30
        and last["RSI14"] >= 30
        and last["Close"] > last["EMA20"]
    )

    return {
        "triggered": triggered,
        "pattern": "RSI_REVERSAL",
        "signal_time": str(d.index[-1].date()),
        "meta": {
            "rsi_prev": float(prev["RSI14"]) if pd.notna(prev["RSI14"]) else None,
            "rsi_last": float(last["RSI14"]) if pd.notna(last["RSI14"]) else None,
            "close": float(last["Close"]),
            "ema20": float(last["EMA20"]) if pd.notna(last["EMA20"]) else None,
        }
    }


def detect_support_resistance_touch(df: pd.DataFrame, lookback: int = 120) -> dict:
    if len(df) < lookback + 20:
        return {"triggered": False, "pattern": "SUPPORT_RESISTANCE_TOUCH"}

    d = df.tail(lookback).copy()
    max_idx, min_idx = _local_extrema(d["Close"], order=4)

    if len(max_idx) < 2 or len(min_idx) < 2:
        return {"triggered": False, "pattern": "SUPPORT_RESISTANCE_TOUCH"}

    resistance = float(d["Close"].iloc[max_idx].tail(5).mean())
    support = float(d["Close"].iloc[min_idx].tail(5).mean())
    last_close = float(d["Close"].iloc[-1])

    near_res = abs(last_close - resistance) / resistance < 0.01
    near_sup = abs(last_close - support) / support < 0.01

    triggered = near_res or near_sup
    zone = "RESISTANCE" if near_res else ("SUPPORT" if near_sup else "NONE")

    return {
        "triggered": triggered,
        "pattern": "SUPPORT_RESISTANCE_TOUCH",
        "signal_time": str(d.index[-1].date()),
        "meta": {
            "close": last_close,
            "support": support,
            "resistance": resistance,
            "zone": zone
        }
    }


def run_all_pattern_detectors(df: pd.DataFrame):
    results = []
    results.append(detect_breakout_20d(df))
    results.append(detect_reversal_rsi(df))
    results.append(detect_support_resistance_touch(df))
    return results