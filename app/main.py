import math
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.data_loader import fetch_ohlcv
from src.indicators import add_indicators
from src.patterns import run_all_pattern_detectors
from src.backtest import backtest_breakout_20d, backtest_rsi_reversal
from src.ai_explainer import get_gemini_explanation

app = FastAPI(title="ET Markets - Chart Pattern Intelligence")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


def _f(v):
    if v is None:
        return None
    try:
        f = float(v)
        return None if (math.isnan(f) or math.isinf(f)) else f
    except (TypeError, ValueError):
        return None

def _flist(series) -> list:
    return [_f(v) for v in series.tolist()]

def _clean_meta(meta: dict) -> dict:
    return {k: (_f(v) if isinstance(v, (float, int)) else v) for k, v in meta.items()}


class AnalysisRequest(BaseModel):
    symbol: str = "TCS.NS"
    period: str = "1y"
    interval: str = "1d"
    recent_bars: int = 20


def get_backtest_for_pattern(df: pd.DataFrame, pattern_name: str) -> dict:
    if pattern_name == "20D_BREAKOUT":
        return backtest_breakout_20d(df)
    if pattern_name == "RSI_REVERSAL":
        return backtest_rsi_reversal(df)
    return {"pattern": pattern_name, "note": "Backtest not implemented for this pattern."}


def scan_recent_signals(df: pd.DataFrame, bars: int = 20):
    found = []
    min_history = 70
    start_idx = max(min_history, len(df) - bars)
    for i in range(start_idx, len(df)):
        sub = df.iloc[:i + 1]
        for r in run_all_pattern_detectors(sub):
            if r.get("triggered"):
                found.append({
                    "date":    str(sub.index[-1].date()),
                    "pattern": r.get("pattern"),
                    "meta":    _clean_meta(r.get("meta", {})),
                })
    uniq = {}
    for x in found:
        uniq[(x["date"], x["pattern"])] = x
    out = list(uniq.values())
    out.sort(key=lambda x: x["date"], reverse=True)
    return out


@app.get("/")
async def root():
    return FileResponse("static/index.html")

@app.get("/api/health")
async def health():
    return {"status": "ok"}

@app.post("/api/analyze")
async def analyze(req: AnalysisRequest):
    try:
        raw = fetch_ohlcv(symbol=req.symbol, period=req.period, interval=req.interval)
        df = add_indicators(raw).copy()

        missing = [c for c in ["Open", "High", "Low", "Close", "Volume"] if c not in df.columns]
        if missing:
            raise HTTPException(status_code=400, detail=f"Missing columns: {missing}")

        chart_data = {
            "dates":  [str(d.date()) for d in df.index],
            "open":   _flist(df["Open"]),
            "high":   _flist(df["High"]),
            "low":    _flist(df["Low"]),
            "close":  _flist(df["Close"]),
            "volume": _flist(df["Volume"]),
            "ema20":  _flist(df["EMA20"]) if "EMA20" in df.columns else [],
            "sma50":  _flist(df["SMA50"]) if "SMA50" in df.columns else [],
        }

        pattern_results = run_all_pattern_detectors(df)
        enriched_signals = []

        any_triggered = False

        for p in pattern_results:
            bt = get_backtest_for_pattern(df, p["pattern"])

            if p.get("triggered"):
                any_triggered = True

                ai_text = get_gemini_explanation(req.symbol, p, bt)

                enriched_signals.append({
                    "pattern":     p["pattern"],
                    "signal_time": p.get("signal_time"),
                    "meta":        _clean_meta(p.get("meta", {})),
                    "backtest":    bt,
                    "ai_insight":  ai_text,
                })

        # ✅ ADD THIS BLOCK (VERY IMPORTANT)
        if not any_triggered:
            ai_text = get_gemini_explanation(
                req.symbol,
                {"pattern": "NO_SIGNAL", "meta": {}},
                {"note": "No active pattern"}
            )

            enriched_signals.append({
                "pattern": "MARKET_CONTEXT",
                "signal_time": str(df.index[-1].date()),
                "meta": {},
                "backtest": {},
                "ai_insight": ai_text,
            })

        recent_signals = scan_recent_signals(df, bars=req.recent_bars)

        last = df.iloc[-1]
        snapshot = {
            "close":  _f(last.get("Close")),
            "rsi14":  _f(last.get("RSI14")),
            "ema20":  _f(last.get("EMA20")),
            "sma50":  _f(last.get("SMA50")),
            "volume": _f(last.get("Volume")),
            "macd":   _f(last.get("MACD")),
            "atr14":  _f(last.get("ATR14")),
        }

        debug = {
            "rows":            len(df),
            "columns":         list(df.columns),
            "resolved_symbol": raw.attrs.get("resolved_symbol", req.symbol),
        }

        return {
            "symbol":         req.symbol,
            "chart_data":     chart_data,
            "latest_signals": enriched_signals,
            "recent_signals": recent_signals,
            "snapshot":       snapshot,
            "debug":          debug,
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))