import os
from dotenv import load_dotenv
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from src.data_loader import fetch_ohlcv
from src.indicators import add_indicators
from src.patterns import run_all_pattern_detectors
from src.backtest import backtest_breakout_20d, backtest_rsi_reversal
from src.ai_explainer import get_gemini_explanation

load_dotenv()

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="ET Markets - Chart Pattern Intelligence",
    layout="wide"
)

st.title("📈 ET Markets - Chart Pattern Intelligence (NSE)")
st.caption("Data → Pattern Signal → Historical Context → Plain-English AI Insight")

# -----------------------------
# Sidebar controls
# -----------------------------
with st.sidebar:
    st.header("Configuration")

    symbol = st.text_input(
    "NSE Symbol",
    value="TCS.NS",
    help="Examples: RELIANCE.NS, TCS.NS, INFY.NS, HDFCBANK.NS"
    )

    period = st.selectbox(
        "History Period",
        ["6mo", "1y", "2y", "5y"],
        index=1
    )

    interval = st.selectbox(
        "Interval",
        ["1d", "1wk"],
        index=0
    )

    recent_bars = st.slider(
        "Recent bars to scan",
        min_value=10,
        max_value=60,
        value=20,
        step=5,
        help="Scan for pattern triggers in recent candles, not just the latest candle."
    )

    st.markdown("---")
    st.subheader("Signal Sensitivity")
    breakout_vol_mult = st.slider(
        "Breakout volume multiplier (display hint only)",
        min_value=1.0,
        max_value=2.0,
        value=1.2,
        step=0.1,
        help="Current detector logic in src/patterns.py may still use fixed thresholds."
    )

    run_btn = st.button("Run Analysis", type="primary")

# -----------------------------
# Helpers
# -----------------------------
def build_price_chart(df: pd.DataFrame, symbol: str):
    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        name="OHLC"
    ))

    if "EMA20" in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df["EMA20"],
            mode="lines", name="EMA20"
        ))

    if "SMA50" in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df["SMA50"],
            mode="lines", name="SMA50"
        ))

    fig.update_layout(
        title=f"{symbol} Price Chart",
        height=650,
        xaxis_rangeslider_visible=False,
        legend=dict(orientation="h")
    )
    return fig


def get_backtest_for_pattern(df: pd.DataFrame, pattern_name: str) -> dict:
    if pattern_name == "20D_BREAKOUT":
        return backtest_breakout_20d(df)
    if pattern_name == "RSI_REVERSAL":
        return backtest_rsi_reversal(df)
    return {"pattern": pattern_name, "note": "Backtest not yet implemented for this pattern."}


def scan_recent_signals(df: pd.DataFrame, bars: int = 20):
    """
    Re-run pattern detectors over rolling endpoints for recent bars.
    Returns unique signals by (date, pattern).
    """
    found = []
    min_history = 70  # enough history for rolling indicators + pattern windows
    start_idx = max(min_history, len(df) - bars)

    for i in range(start_idx, len(df)):
        sub = df.iloc[: i + 1]
        results = run_all_pattern_detectors(sub)

        for r in results:
            if r.get("triggered"):
                found.append({
                    "date": str(sub.index[-1].date()),
                    "pattern": r.get("pattern"),
                    "meta": r.get("meta", {})
                })

    # de-duplicate by (date, pattern)
    uniq = {}
    for x in found:
        key = (x["date"], x["pattern"])
        uniq[key] = x

    out = list(uniq.values())
    out.sort(key=lambda x: x["date"], reverse=True)
    return out


def show_snapshot(df: pd.DataFrame):
    latest = df.iloc[-1]
    row = {
        "Close": float(latest["Close"]) if pd.notna(latest["Close"]) else None,
        "RSI14": float(latest["RSI14"]) if "RSI14" in df.columns and pd.notna(latest["RSI14"]) else None,
        "EMA20": float(latest["EMA20"]) if "EMA20" in df.columns and pd.notna(latest["EMA20"]) else None,
        "SMA50": float(latest["SMA50"]) if "SMA50" in df.columns and pd.notna(latest["SMA50"]) else None,
        "Volume": float(latest["Volume"]) if pd.notna(latest["Volume"]) else None,
    }
    st.dataframe(pd.DataFrame([row]), use_container_width=True)


# -----------------------------
# Main
# -----------------------------
if run_btn:
    try:
        # 1) Fetch & enrich
        raw = fetch_ohlcv(symbol=symbol, period=period, interval=interval)
        df = add_indicators(raw).copy()

        # Safety check for required columns
        required_cols = ["Open", "High", "Low", "Close", "Volume"]
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            st.error(f"Missing required columns: {missing}")
            st.stop()

        # 2) Chart
        st.plotly_chart(build_price_chart(df, symbol), use_container_width=True)

        # 3) Latest-bar pattern signals
        st.subheader("Detected Pattern Signals (Latest Bar)")
        pattern_results = run_all_pattern_detectors(df)
        latest_signals = [p for p in pattern_results if p.get("triggered")]

        if latest_signals:
            for p in latest_signals:
                st.success(f"✅ {p['pattern']} triggered on {p['signal_time']}")
                st.json(p.get("meta", {}))

                bt = get_backtest_for_pattern(df, p["pattern"])
                st.info(f"Backtest: {bt}")

                ai_text = get_gemini_explanation(symbol, p, bt)
                st.markdown(f"**AI Insight:** {ai_text}")
        else:
            st.warning("No major tracked pattern triggered on the latest bar.")

        # 4) Recent scan
        st.subheader(f"Recent Signals (Last {recent_bars} Bars)")
        recent = scan_recent_signals(df, bars=recent_bars)

        if recent:
            st.success(f"Found {len(recent)} signal(s) in last {recent_bars} bars.")
            st.dataframe(
                pd.DataFrame([{"date": r["date"], "pattern": r["pattern"]} for r in recent]),
                use_container_width=True
            )

            with st.expander("Show recent signal details"):
                for r in recent:
                    st.markdown(f"**{r['date']} — {r['pattern']}**")
                    st.json(r["meta"])
        else:
            st.info(
                f"No signals found in last {recent_bars} bars. "
                "Try period=2y/5y, interval=1d, or another NSE symbol."
            )

        # 5) Snapshot
        st.subheader("Quick Stats Snapshot")
        show_snapshot(df)

        # 6) Optional debug info
        with st.expander("Debug: Data Health"):
            st.write(f"Rows: {len(df)}")
            st.write(f"Columns: {list(df.columns)}")
            st.write("Tail:")
            st.dataframe(df.tail(5), use_container_width=True)

    except Exception as e:
        st.error(f"Error: {e}")