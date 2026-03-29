import pandas as pd
import numpy as np


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    for col in ["Open", "High", "Low", "Close", "Volume"]:
        out[col] = pd.to_numeric(out[col].squeeze(), errors="coerce")

    out["SMA20"] = out["Close"].rolling(20).mean()
    out["SMA50"] = out["Close"].rolling(50).mean()
    out["EMA20"] = out["Close"].ewm(span=20, adjust=False).mean()

    delta = out["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    gain_rolling = gain.rolling(14).mean()
    loss_rolling = loss.rolling(14).mean()
    rs = gain_rolling / loss_rolling.replace(0, np.nan)
    out["RSI14"] = 100 - (100 / (1 + rs))

    ema12 = out["Close"].ewm(span=12, adjust=False).mean()
    ema26 = out["Close"].ewm(span=26, adjust=False).mean()
    out["MACD"] = ema12 - ema26
    out["MACD_SIGNAL"] = out["MACD"].ewm(span=9, adjust=False).mean()
    out["MACD_HIST"] = out["MACD"] - out["MACD_SIGNAL"]

    high_low = out["High"] - out["Low"]
    high_close = (out["High"] - out["Close"].shift()).abs()
    low_close = (out["Low"] - out["Close"].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    out["ATR14"] = tr.rolling(14).mean()

    out["VOL20"] = out["Volume"].rolling(20).mean()
    return out