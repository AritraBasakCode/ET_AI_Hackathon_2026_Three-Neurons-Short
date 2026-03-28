# ET Markets - Chart Pattern Intelligence (MVP)

A Streamlit-based technical intelligence layer for NSE stocks:
- Detects breakout/reversal/support-resistance style pattern events
- Visualizes price + indicators in Plotly candlestick charts
- Runs basic per-pattern historical success stats
- Uses Gemini API for plain-English investor-friendly explanations

## Tech Stack
- AI: Gemini API
- Data: yfinance
- Backend: Python
- UI: Streamlit
- Charts: Plotly

## Setup

1. Clone and enter project:
   ```bash
   git clone <your_repo_url>
   cd et_markets_chart_intel
   ```

2. Install deps:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure env:
   ```bash
   cp .env.example .env
   # add GEMINI_API_KEY in .env
   ```

4. Run:
   ```bash
   streamlit run app.py
   ```

## Notes
- Use NSE symbols like `RELIANCE.NS`, `TCS.NS`, etc.
- Backtests here are simplified and educational, not production-grade strategy research.
- This is not investment advice.

## Next Improvements (Recommended)
- Add full NSE universe scanner + alert ranking
- Add more robust pattern library:
  - Ascending triangle, double top/bottom, MACD divergences
- Multi-timeframe confirmation logic
- Better walk-forward backtesting and transaction cost modeling
- Portfolio-level signal dashboard + watchlists
- ET Markets data connector (if direct feed/API is available)