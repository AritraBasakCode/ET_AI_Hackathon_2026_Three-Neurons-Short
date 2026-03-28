import time
import yfinance as yf
import pandas as pd


def _normalize_symbol(symbol: str) -> str:
    s = (symbol or "").strip().upper()
    if not s:
        return s
    if "." not in s:
        return f"{s}.NS"
    return s


def _candidate_symbols(symbol: str):
    s = _normalize_symbol(symbol)
    base = s.split(".")[0]
    return [f"{base}.NS", f"{base}.BO", base]


def _clean_df(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    # Flatten columns if needed
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]

    # Keep expected OHLCV
    keep = [c for c in ["Open", "High", "Low", "Close", "Adj Close", "Volume"] if c in df.columns]
    if not keep:
        return pd.DataFrame()

    out = df[keep].copy()

    # Force numeric 1D
    for col in ["Open", "High", "Low", "Close", "Volume"]:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col].squeeze(), errors="coerce")

    req = [c for c in ["Open", "High", "Low", "Close", "Volume"] if c in out.columns]
    out = out.dropna(subset=req)
    if out.empty:
        return pd.DataFrame()

    # Remove timezone from index if present
    out.index = pd.to_datetime(out.index).tz_localize(None)
    return out


def _history_with_ticker(symbol: str, period: str, interval: str) -> pd.DataFrame:
    t = yf.Ticker(symbol)
    # auto_adjust=False to keep raw OHLC consistent with your indicators
    df = t.history(period=period, interval=interval, auto_adjust=False, actions=False)
    return _clean_df(df)


def _history_with_download(symbol: str, period: str, interval: str) -> pd.DataFrame:
    df = yf.download(
        tickers=symbol,
        period=period,
        interval=interval,
        auto_adjust=False,
        progress=False,
        group_by="column",
        threads=False
    )
    return _clean_df(df)


def fetch_ohlcv(symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    """
    Robust fetch strategy:
    1) Ticker().history() with retries
    2) yf.download() fallback
    3) NSE -> BSE -> bare symbol fallback
    """
    candidates = _candidate_symbols(symbol)
    last_error = None

    for sym in candidates:
        for attempt in range(3):
            try:
                # Primary
                df = _history_with_ticker(sym, period, interval)
                if not df.empty:
                    df.attrs["resolved_symbol"] = sym
                    return df

                # Fallback method
                df = _history_with_download(sym, period, interval)
                if not df.empty:
                    df.attrs["resolved_symbol"] = sym
                    return df

            except Exception as e:
                last_error = e

            time.sleep(0.8 * (attempt + 1))

    msg = f"No data found for symbol: {symbol}. Tried: {', '.join(candidates)}"
    if last_error:
        msg += f" | last error: {last_error}"
    raise ValueError(msg)