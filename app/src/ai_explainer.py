import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file in app directory
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)


def get_gemini_explanation(symbol: str, pattern_result: dict, backtest_result: dict) -> dict:
    """
    Returns a structured dict with keys:
      summary, what_happened, why_it_matters, risk_caution, backtest_context
    Falls back to a plain string under key 'raw' if parsing fails.
    """
    
    # Get API key fresh each call to ensure it's loaded
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        # Debug: show what we tried to load
        env_file = Path(__file__).parent.parent / ".env"
        return {
            "error": f"Gemini API key not configured. Looked in: {env_file}. Add GEMINI_API_KEY in .env to enable AI explanations."
        }

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")

        prompt = f"""
You are a concise financial analyst for Indian retail investors.
Given the pattern signal and backtest data below, respond ONLY with a valid JSON object — no markdown, no explanation outside the JSON.

Return exactly this shape:
{{
  "summary": "One sentence headline (max 15 words)",
  "what_happened": "2-3 sentences describing what the pattern detected",
  "why_it_matters": "2-3 sentences on the market significance",
  "risk_caution": "1-2 sentences on key risks",
  "backtest_context": "1-2 sentences interpreting the historical success rate"
}}

Stock: {symbol}
Pattern: {json.dumps(pattern_result, indent=2)}
Backtest: {json.dumps(backtest_result, indent=2)}
"""

        resp = model.generate_content(prompt)
        text = getattr(resp, "text", "") or ""
        text = text.strip()
        # Strip markdown fences if present
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        text = text.strip()
        parsed = json.loads(text)
        return parsed

    except json.JSONDecodeError:
        # Return raw text in a structured wrapper
        raw = getattr(resp, "text", "AI explanation unavailable.") if 'resp' in dir() else "AI explanation unavailable."
        return {"summary": "AI insight available", "raw": raw.strip()}
    except Exception as e:
        return {"error": f"AI explanation error: {str(e)}"}