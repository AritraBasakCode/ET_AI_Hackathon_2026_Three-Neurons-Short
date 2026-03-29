<div align="center">

```
██████╗  █████╗ ████████╗████████╗███████╗██████╗ ███╗   ██╗██╗ ██████╗ 
██╔══██╗██╔══██╗╚══██╔══╝╚══██╔══╝██╔════╝██╔══██╗████╗  ██║██║██╔═══██╗
██████╔╝███████║   ██║      ██║   █████╗  ██████╔╝██╔██╗ ██║██║██║   ██║
██╔═══╝ ██╔══██║   ██║      ██║   ██╔══╝  ██╔══██╗██║╚██╗██║██║██║▄▄ ██║
██║     ██║  ██║   ██║      ██║   ███████╗██║  ██║██║ ╚████║██║╚██████╔╝
╚═╝     ╚═╝  ╚═╝   ╚═╝      ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝ ╚══▀▀═╝
```

# PatternIQ — NSE Chart Pattern Intelligence Platform

**Real-time technical pattern detection · Historical backtesting · Gemini AI plain-English insights**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111%2B-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)
[![NSE](https://img.shields.io/badge/Exchange-NSE%20India-orange?style=flat-square)](https://nseindia.com)
[![Gemini](https://img.shields.io/badge/AI-Gemini%202.0%20Flash-4285F4?style=flat-square&logo=google)](https://ai.google.dev)

</div>

---

## Table of Contents

- [Overview](#overview)
- [Platform Features](#platform-features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the App](#running-the-app)
- [Usage Guide](#usage-guide)
- [API Reference](#api-reference)
- [Pattern Detection Logic](#pattern-detection-logic)
- [Backtesting Methodology](#backtesting-methodology)
- [AI Insight Engine](#ai-insight-engine)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)
- [Disclaimer](#disclaimer)

---

## Overview

PatternIQ is a full-stack market intelligence platform built for Indian retail investors and traders. It combines **real-time NSE data**, **algorithmic chart pattern detection**, **historical backtesting**, and **Gemini AI-powered plain-English explanations** into a single Bloomberg-style terminal interface.

The platform was built for the **ET Markets AI Hackathon 2026** by Team Three Neurons Short, with the goal of making institutional-grade technical analysis accessible and understandable to every retail participant in India's equity markets.

> **Data → Pattern Signal → Historical Context → AI Plain-English Insight**

---

## Platform Features

### 📊 Live Chart Engine
- Interactive candlestick chart powered by **TradingView Lightweight Charts v4**
- Synchronized volume histogram with green/red color coding
- EMA20 and SMA50 overlays rendered in real-time
- Period-over-period return display

### 🔍 Pattern Detection Engine
Three algorithmic detectors run on every analysis:

| Pattern | Logic | Trigger Condition |
|---|---|---|
| **20D Breakout** | Price breaks above 20-day rolling high | Close > prev 20D high AND Volume > 1.2× 20D avg volume |
| **RSI Reversal** | Bullish RSI crossover from oversold | RSI crosses above 30 from below AND Close > EMA20 |
| **S/R Touch** | Price touches inferred support or resistance | Close within 1% of rolling local extrema mean |

### 📈 Historical Backtesting
Each triggered pattern is backtested automatically against the full historical dataset:
- Forward-looking success rate over configurable hold periods
- Win/loss count and percentage
- Parameter-aware results (hold days, target %)

### 🤖 Gemini AI Insight Engine
When a pattern triggers, the Gemini 2.0 Flash model generates structured analysis with five components:
- **Summary** — one-sentence headline
- **What Happened** — technical description of the signal
- **Why It Matters** — market significance and context
- **Risk Caution** — key downside considerations
- **Backtest Context** — how to interpret the historical success rate

### 📉 Market Snapshot Panel
Live indicators rendered in the sidebar:
- Close price, RSI(14), EMA20, SMA50, Volume, MACD, ATR(14)
- Visual gauge bars for RSI and MACD momentum
- Color-coded bull/bear classification

### 🕐 Scan History Log
Rolling window scan across the last N bars (configurable 10–60) finds every historical pattern occurrence — not just the latest candle.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Browser Client                      │
│  index.html + style.css + app.js                        │
│  Lightweight Charts  ←→  Fetch API  ←→  DOM Renderer    │
└─────────────────┬───────────────────────────────────────┘
                  │  HTTP POST /api/analyze
                  ▼
┌─────────────────────────────────────────────────────────┐
│                  FastAPI Server (main.py)               │
│                                                         │
│  POST /api/analyze ──► fetch_ohlcv()                    │
│                    ──► add_indicators()                 │
│                    ──► run_all_pattern_detectors()      │
│                    ──► backtest_*()                     │
│                    ──► get_gemini_explanation()         │
│                    ──► NaN sanitization                 │
│                    ──► JSON response                    │
│                                                         │
│  GET  /           ──► static/index.html                 │
│  GET  /api/health ──► {"status": "ok"}                  │
└──────────┬──────────────────────────┬───────────────────┘
           │                          │
           ▼                          ▼
  ┌─────────────────┐      ┌──────────────────────┐
  │   Yahoo Finance │      │   Google Gemini API  │
  │   (yfinance)    │      │   gemini-2.0-flash   │
  │   NSE/BSE OHLCV │      │   Structured JSON AI │
  └─────────────────┘      └──────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.10+, FastAPI, Uvicorn |
| **Data** | yfinance (Yahoo Finance), pandas, numpy |
| **AI** | Google Gemini 2.0 Flash via `google-generativeai` |
| **Frontend** | Vanilla HTML5 / CSS3 / JavaScript (ES2022) |
| **Charts** | TradingView Lightweight Charts v4 (CDN) |
| **Fonts** | Syne (display) + JetBrains Mono (data) via Google Fonts |
| **Deployment** | Uvicorn ASGI, static file serving via FastAPI |

---

## Prerequisites

Before you begin, ensure you have:

- **Python 3.10 or higher** installed ([download](https://python.org/downloads))
- **pip** (comes with Python)
- **Git** ([download](https://git-scm.com))
- A **Google Gemini API key** — free tier available at [ai.google.dev](https://ai.google.dev)
- Internet access (for Yahoo Finance data + Gemini API calls)

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
```

### 2. Navigate to the App Directory

```bash
cd app
```

> ⚠️ **Critical:** All commands from this point must be run from inside the `app/` directory. The server uses relative paths for static files and module imports.

### 3. Create a Virtual Environment (Recommended)

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (Command Prompt):**
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

> This installs: `fastapi`, `uvicorn`, `yfinance`, `pandas`, `numpy`, `google-generativeai`, `python-dotenv`, `curl_cffi`

---

## Configuration

### 5. Set Up Your API Key

Copy the example environment file:

```bash
# macOS / Linux
cp .env.example .env

# Windows
copy .env.example .env
```

Open `.env` in any text editor and add your Gemini API key:

```env
GEMINI_API_KEY=your_actual_api_key_here
```

#### Getting a Gemini API Key (Free)
1. Visit [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Sign in with a Google account
3. Click **Create API Key**
4. Copy the key into your `.env` file

> **Note:** The platform works without a Gemini API key — pattern detection, charts, and backtesting all function normally. Only the AI Insight panel will show a "key not configured" message.

---

## Running the App

### 6. Start the Server

```bash
uvicorn main:app --reload --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 7. Open in Browser

Navigate to:
```
http://localhost:8000
```

### Stopping the Server

```
Ctrl + C
```

---

### Production Mode (No Auto-Reload)

For a stable demo or deployment:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
```

---

## Usage Guide

### Running Your First Analysis

1. **Enter an NSE symbol** in the top-left input field
   - Format: `SYMBOL.NS` for NSE (e.g. `RELIANCE.NS`, `INFY.NS`, `HDFCBANK.NS`)
   - The `.NS` suffix is auto-added if omitted

2. **Select a history period**: `6M`, `1Y`, `2Y`, or `5Y`
   - Longer periods give the backtester more signal samples
   - `2Y` or `5Y` recommended for meaningful backtest statistics

3. **Choose interval**: `D` (Daily) or `W` (Weekly)

4. **Set scan depth**: How many recent bars to scan for historical signals (10–60)

5. **Click `SCAN PATTERNS`** or press `Enter`

### Reading the Results

#### Chart Panel
- **Green candles** = close > open (bullish)
- **Red candles** = close < open (bearish)
- **Cyan line** = EMA20 (short-term trend)
- **Amber dashed line** = SMA50 (medium-term trend)
- **⚡ badge** in chart header = pattern triggered on latest bar

#### Live Signal Detection (left panel)
- Shows patterns that fired on the **most recent bar**
- Each card includes: pattern name, trigger time, raw indicator values, backtest stats, and AI insight
- If no pattern fires, shows a contextual market state summary with RSI/MACD/trend pills

#### Historical Signal Log (right panel)
- Every pattern occurrence found in the last N bars
- Useful for seeing pattern frequency and recency

#### Sidebar Stats
- **CLOSE** — latest close price (amber = above SMA50, red = below)
- **RSI 14** — green < 30 (oversold), amber > 70 (overbought)
- **MACD** — green = positive momentum, red = negative
- **Gauge bars** — visual RSI and MACD momentum indicators

### Supported Symbols

Any NSE-listed equity. Examples:

| Sector | Symbols |
|---|---|
| IT | `TCS.NS`, `INFY.NS`, `WIPRO.NS`, `HCLTECH.NS` |
| Banking | `HDFCBANK.NS`, `ICICIBANK.NS`, `SBIN.NS`, `KOTAKBANK.NS` |
| Energy | `RELIANCE.NS`, `ONGC.NS`, `POWERGRID.NS` |
| FMCG | `HINDUNILVR.NS`, `ITC.NS`, `NESTLEIND.NS` |
| Auto | `TATAMOTORS.NS`, `MARUTI.NS`, `M&M.NS` |
| Pharma | `SUNPHARMA.NS`, `DRREDDY.NS`, `CIPLA.NS` |

---

## API Reference

The FastAPI backend exposes three endpoints. Interactive docs available at `http://localhost:8000/docs`.

### `GET /`
Serves the frontend application (`static/index.html`).

---

### `POST /api/analyze`

Runs full analysis pipeline for a given symbol.

**Request Body:**
```json
{
  "symbol": "TCS.NS",
  "period": "1y",
  "interval": "1d",
  "recent_bars": 20
}
```

| Field | Type | Options | Default |
|---|---|---|---|
| `symbol` | string | Any NSE/BSE ticker | `TCS.NS` |
| `period` | string | `6mo`, `1y`, `2y`, `5y` | `1y` |
| `interval` | string | `1d`, `1wk` | `1d` |
| `recent_bars` | integer | `10` – `60` | `20` |

**Response:**
```json
{
  "symbol": "TCS.NS",
  "chart_data": {
    "dates": ["2024-04-01", "..."],
    "open": [3800.0, "..."],
    "high": [3850.0, "..."],
    "low":  [3780.0, "..."],
    "close": [3820.0, "..."],
    "volume": [1200000, "..."],
    "ema20": [3810.0, "..."],
    "sma50": [3750.0, "..."]
  },
  "latest_signals": [
    {
      "pattern": "20D_BREAKOUT",
      "signal_time": "2025-03-28",
      "meta": {
        "close": 3820.0,
        "prev_20d_high": 3800.0,
        "volume": 1500000,
        "vol20": 1100000
      },
      "backtest": {
        "pattern": "20D_BREAKOUT",
        "total_signals": 12,
        "wins": 8,
        "success_rate_pct": 66.67,
        "params": { "hold_days": 10, "target_pct": 0.03 }
      },
      "ai_insight": {
        "summary": "TCS breaks 20-day high with strong volume confirmation.",
        "what_happened": "...",
        "why_it_matters": "...",
        "risk_caution": "...",
        "backtest_context": "..."
      }
    }
  ],
  "recent_signals": [
    { "date": "2025-03-15", "pattern": "RSI_REVERSAL", "meta": {} }
  ],
  "snapshot": {
    "close": 3820.0,
    "rsi14": 58.4,
    "ema20": 3810.0,
    "sma50": 3750.0,
    "volume": 1500000,
    "macd": 24.3,
    "atr14": 62.1
  },
  "debug": {
    "rows": 248,
    "columns": ["Open", "High", "Low", "Close", "..."],
    "resolved_symbol": "TCS.NS"
  }
}
```

---

### `GET /api/health`

Health check endpoint.

**Response:**
```json
{ "status": "ok" }
```

---

## Pattern Detection Logic

### 20D Breakout

```
Signal: Close[t] > max(High[t-20 : t-1])
        AND Volume[t] > 1.2 × mean(Volume[t-20 : t-1])
```

Identifies momentum breakouts where price clears a 20-day resistance level with above-average volume. The volume filter reduces false breakouts during low-liquidity periods.

### RSI Reversal

```
Signal: RSI14[t-1] < 30
        AND RSI14[t] >= 30
        AND Close[t] > EMA20[t]
```

Detects oversold bounces — specifically the candle where RSI crosses back above the 30 threshold, combined with price trading above its 20-day exponential average to confirm short-term bullish momentum.

### Support / Resistance Touch

```
Resistance = mean(Close at local maxima, last 5 peaks)
Support    = mean(Close at local minima, last 5 troughs)

Signal: |Close[t] - Resistance| / Resistance < 0.01
        OR
        |Close[t] - Support| / Support < 0.01
```

Uses a local extrema algorithm (window order = 4) over a 120-bar lookback to infer dynamic support and resistance zones. Triggers when price comes within 1% of either level.

---

## Backtesting Methodology

Backtests are **in-sample** and purely historical — they measure how often the same signal, in the past, led to a +3% gain (breakout) or +2.5% gain (RSI reversal) within 10 trading days.

```
For each historical signal at bar i:
  entry = Close[i]
  future_max = max(Close[i+1 : i+10])
  success = (future_max / entry - 1) >= target_pct
```

| Pattern | Target Return | Hold Period |
|---|---|---|
| 20D Breakout | +3.0% | 10 days |
| RSI Reversal | +2.5% | 10 days |

> ⚠️ **Important:** These are backward-looking statistics on the same dataset used for detection. They should not be treated as forward return estimates. Past performance does not guarantee future results.

---

## AI Insight Engine

When a pattern triggers, PatternIQ calls **Gemini 2.0 Flash** with a structured prompt requesting a JSON response in the following schema:

```json
{
  "summary":          "One-sentence headline (max 15 words)",
  "what_happened":    "2-3 sentences on what the pattern detected",
  "why_it_matters":   "2-3 sentences on market significance",
  "risk_caution":     "1-2 sentences on key risks",
  "backtest_context": "1-2 sentences interpreting the success rate"
}
```

The response is parsed and each field is rendered as a labeled section in the UI. If Gemini returns malformed JSON, the raw text is displayed as a fallback. If no API key is configured, a clear message is shown without breaking the rest of the analysis.

---

## Project Structure

```
app/
├── main.py                  # FastAPI app, all routes, NaN sanitization
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variable template
├── .env                     # Your actual keys (do NOT commit this)
│
├── src/
│   ├── __init__.py          # Makes src a Python package (must exist)
│   ├── data_loader.py       # yfinance OHLCV fetcher with fallback logic
│   ├── indicators.py        # EMA, SMA, RSI, MACD, ATR computation
│   ├── patterns.py          # 3 pattern detectors + local extrema util
│   ├── backtest.py          # Historical success rate calculator
│   └── ai_explainer.py      # Gemini API call with structured JSON prompt
│
└── static/
    ├── index.html           # Single-page frontend shell
    ├── style.css            # Bloomberg × Cyberpunk terminal theme
    └── app.js               # Chart logic, API calls, DOM rendering
```

---

## Troubleshooting

### `ModuleNotFoundError: No module named 'main'`
You are running uvicorn from the wrong directory. Make sure you `cd app` first.

### `No data found for symbol: XYZ.NS`
- Check the ticker spelling — use the NSE symbol exactly (e.g. `M&M.NS` not `MM.NS`)
- Yahoo Finance may rate-limit rapid successive requests — wait 30 seconds and retry
- Run `pip install -U yfinance curl_cffi` to ensure the latest version

### `ValueError: Out of range float values are not JSON compliant`
This means NaN values reached the response serializer. Pull the latest `main.py` which includes the `_f()` sanitizer.

### `404 Not Found` on `/api/analyze`
- Confirm you are inside the `app/` directory when starting uvicorn
- Verify `src/__init__.py` exists (even as an empty file)
- Check `http://localhost:8000/api/health` — if that also 404s, the imports are failing silently on startup

### `Yahoo API requires curl_cffi session`
Install the required dependency: `pip install curl_cffi`

### AI insight shows "key not configured"
Add `GEMINI_API_KEY=your_key` to your `.env` file and restart the server.

### Charts appear blank after analysis
Hard-refresh the browser: `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac) to clear the JS cache.

---

## Disclaimer

> PatternIQ is built for **educational and research purposes only**. Nothing on this platform constitutes financial advice, investment advice, or a recommendation to buy or sell any security. Technical patterns and backtested success rates are historical observations and do not predict future price movements. Always conduct your own research and consult a SEBI-registered financial advisor before making investment decisions. The developers accept no liability for any trading losses incurred.

---

<div align="center">

Built with ⚡ for the **ET Markets AI Hackathon 2026**

**Team Three Neurons Short**

</div>
