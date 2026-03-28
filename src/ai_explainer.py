import os
import json
import google.generativeai as genai

def get_gemini_explanation(symbol: str, pattern_result: dict, backtest_result: dict) -> str:
    """
    Generate plain-English explanation using Gemini.
    Falls back safely if API key missing/error.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "Gemini API key not configured. Add GEMINI_API_KEY in .env to enable AI explanations."

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")

        prompt = f"""
You are a financial market assistant for Indian retail investors.
Explain this technical signal in plain English and include:
1) what happened,
2) why it may matter,
3) risk caution,
4) how historical success rates should be interpreted.

Stock: {symbol}
Pattern signal JSON: {json.dumps(pattern_result, indent=2)}
Backtest JSON: {json.dumps(backtest_result, indent=2)}

Keep it concise (max 160 words), non-hyped, and educational.
"""

        resp = model.generate_content(prompt)
        text = getattr(resp, "text", None)
        if text:
            return text.strip()
        return "AI explanation unavailable at the moment."

    except Exception as e:
        return f"AI explanation error: {str(e)}"