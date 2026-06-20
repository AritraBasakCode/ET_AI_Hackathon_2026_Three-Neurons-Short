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
    # Try multiple variations for NSE/BSE stocks
    # Yahoo Finance primarily uses .NS for NSE
    candidates = [
        f"{base}.NS",      # NSE (primary)
        f"{base}.BO",      # BSE
        base,               # Plain symbol
    ]
    # Remove duplicates while preserving order
    seen = set()
    return [x for x in candidates if not (x in seen or seen.add(x))]


def _clean_df(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]

    keep = [c for c in ["Open", "High", "Low", "Close", "Adj Close", "Volume"] if c in df.columns]
    if not keep:
        return pd.DataFrame()

    out = df[keep].copy()

    for col in ["Open", "High", "Low", "Close", "Volume"]:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col].squeeze(), errors="coerce")

    req = [c for c in ["Open", "High", "Low", "Close", "Volume"] if c in out.columns]
    out = out.dropna(subset=req)
    if out.empty:
        return pd.DataFrame()

    out.index = pd.to_datetime(out.index).tz_localize(None)
    return out


def _history_with_ticker(symbol: str, period: str, interval: str) -> pd.DataFrame:
    t = yf.Ticker(symbol)
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
    candidates = _candidate_symbols(symbol)
    last_error = None

    for sym in candidates:
        for attempt in range(5):  # Increased from 3 to 5 attempts
            try:
                print(f"Attempt {attempt + 1}/5: Fetching {sym}...")
                df = _history_with_ticker(sym, period, interval)
                if not df.empty:
                    print(f"✓ Success with {sym}")
                    df.attrs["resolved_symbol"] = sym
                    return df

                df = _history_with_download(sym, period, interval)
                if not df.empty:
                    print(f"✓ Success with {sym}")
                    df.attrs["resolved_symbol"] = sym
                    return df

            except Exception as e:
                last_error = e
                print(f"✗ Failed: {sym} - {str(e)}")

            # Increase delay between attempts: 1s, 2s, 3s, 4s, 5s
            delay = 1.5 * (attempt + 1)
            time.sleep(delay)

    msg = f"No data found for symbol: {symbol}. Tried: {', '.join(candidates)}"
    if last_error:
        msg += f" | last error: {last_error}"
    raise ValueError(msg)