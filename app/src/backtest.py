import pandas as pd


def backtest_breakout_20d(df: pd.DataFrame, hold_days: int = 10, target_pct: float = 0.03):
    d = df.copy()
    d["PREV_20D_HIGH"] = d["High"].rolling(20).max().shift(1)
    d["VOL20"] = d["Volume"].rolling(20).mean()

    signals = []
    for i in range(21, len(d) - hold_days):
        row = d.iloc[i]
        cond = (
            row["Close"] > row["PREV_20D_HIGH"]
            and row["Volume"] > 1.2 * row["VOL20"]
        )
        if cond:
            entry = row["Close"]
            future_window = d.iloc[i + 1:i + 1 + hold_days]
            future_max = future_window["Close"].max()
            success = (future_max / entry - 1) >= target_pct
            signals.append({
                "date": str(d.index[i].date()),
                "entry": float(entry),
                "future_max": float(future_max),
                "success": bool(success)
            })

    total = len(signals)
    wins = sum(s["success"] for s in signals)
    success_rate = (wins / total * 100) if total > 0 else None

    return {
        "pattern": "20D_BREAKOUT",
        "total_signals": total,
        "wins": wins,
        "success_rate_pct": round(success_rate, 2) if success_rate is not None else None,
        "params": {"hold_days": hold_days, "target_pct": target_pct}
    }


def backtest_rsi_reversal(df: pd.DataFrame, hold_days: int = 10, target_pct: float = 0.025):
    d = df.copy()
    signals = []
    for i in range(25, len(d) - hold_days):
        prev = d.iloc[i - 1]
        row = d.iloc[i]
        cond = (
            prev["RSI14"] < 30
            and row["RSI14"] >= 30
            and row["Close"] > row["EMA20"]
        )
        if cond:
            entry = row["Close"]
            future_max = d.iloc[i + 1:i + 1 + hold_days]["Close"].max()
            success = (future_max / entry - 1) >= target_pct
            signals.append({"date": str(d.index[i].date()), "success": bool(success)})

    total = len(signals)
    wins = sum(s["success"] for s in signals)
    success_rate = (wins / total * 100) if total > 0 else None

    return {
        "pattern": "RSI_REVERSAL",
        "total_signals": total,
        "wins": wins,
        "success_rate_pct": round(success_rate, 2) if success_rate is not None else None,
        "params": {"hold_days": hold_days, "target_pct": target_pct}
    }