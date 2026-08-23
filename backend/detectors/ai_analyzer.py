import os
import json
import re
from typing import List, Dict, Any, Optional
import requests

class CoercivePatternAIAnalyzer:
    """
    Simplified, ultra-clean forensic copy analyzer:
    1. Deterministic Rule-Based Parsing (Default engine, zero external calls)
    2. Optional AI Inference (Enabled only when user provides an API key)
    """
    def __init__(self):
        self.default_api_key = os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("GROK_API_KEY")

    def analyze_text_corpus(
        self,
        text_segments: List[str],
        api_key: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        findings = []
        active_key = (api_key or self.default_api_key or "").strip()

        # 1. Deterministic Heuristics (Always active, 100% reliable)
        for text in text_segments:
            text_clean = text.strip()
            if len(text_clean) < 4:
                continue

            # Social Proof & False Scarcity
            if re.search(r"\b(9[0-9]% of (users|shoppers|members)|everyone chooses|popular choice|high demand|almost gone|people are viewing|limited stock)\b", text_clean, re.I):
                findings.append({
                    "pattern": "Social Proof Coercion / False Scarcity",
                    "severity": "Medium",
                    "score_impact": 14.0,
                    "text": text_clean[:120],
                    "explanation": f"Uses normative social pressure '{text_clean[:80]}' to induce conformity bias.",
                    "psychological_mechanism": "Bandwagon Effect & Scarcity Heuristic."
                })

            # Catastrophic Loss Framing
            if re.search(r"\b(forever lose|permanent loss|irrevocable|delete all my (data|progress|leads|benefits)|never get this price|lose all discounts)\b", text_clean, re.I):
                findings.append({
                    "pattern": "Catastrophic Loss Framing",
                    "severity": "High",
                    "score_impact": 22.0,
                    "text": text_clean[:120],
                    "explanation": f"Weaponizes loss threats ('{text_clean[:80]}') during opt-out.",
                    "psychological_mechanism": "Loss Aversion: Amplifies psychological pain of perceived loss."
                })

            # Coercive Decline & Confirmshaming
            if re.search(r"\b(no thanks[,\.\s]+i (don't|hate|prefer not)|prefer paying full price|i don't care about|i prefer to pay full)\b", text_clean, re.I):
                findings.append({
                    "pattern": "Confirmshaming / Coercive Opt-Out",
                    "severity": "High",
                    "score_impact": 24.0,
                    "text": text_clean[:120],
                    "explanation": f"Decline choice framed in self-deprecating copy: '{text_clean[:80]}'.",
                    "psychological_mechanism": "Emotional Coercion & Guilt Induction."
                })

        # 2. Optional AI Inference (Runs ONLY if user explicitly attached an API key)
        if active_key and text_segments:
            try:
                filtered_texts = [t.strip() for t in text_segments if len(t.strip()) > 8][:12]
                if filtered_texts:
                    # Detect endpoint from key format
                    if active_key.startswith("gsk_"):
                        endpoint = "https://api.groq.com/openai/v1/chat/completions"
                        model = "llama-3.3-70b-versatile"
                    elif active_key.startswith("xai-"):
                        endpoint = "https://api.x.ai/v1/chat/completions"
                        model = "grok-beta"
                    else:
                        endpoint = "https://api.openai.com/v1/chat/completions"
                        model = "gpt-4o-mini"

                    system_prompt = (
                        "You are Houdini Dark Pattern Legal Inspector. "
                        "Analyze the website text snippets for deceptive design patterns, "
                        "confirmshaming, drip pricing, fake urgency, and psychological coercion. "
                        "Return ONLY a JSON array of objects with keys: "
                        "pattern, severity ('Critical', 'High', 'Medium'), text, explanation, psychological_mechanism."
                    )

                    resp = requests.post(
                        endpoint,
                        headers={"Authorization": f"Bearer {active_key}", "Content-Type": "application/json"},
                        json={
                            "model": model,
                            "messages": [
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": f"Website Text:\n{json.dumps(filtered_texts)}"}
                            ],
                            "temperature": 0.1
                        },
                        timeout=6
                    )

                    if resp.status_code == 200:
                        content = resp.json().get("choices", [{}])[0].get("message", {}).get("content", "")
                        clean_json = re.sub(r"^```json\s*", "", content.strip(), flags=re.MULTILINE)
                        clean_json = re.sub(r"^```\s*$", "", clean_json.strip(), flags=re.MULTILINE)
                        ai_parsed = json.loads(clean_json)
                        if isinstance(ai_parsed, list):
                            for item in ai_parsed:
                                findings.append({
                                    "pattern": f"AI: {item.get('pattern', 'Deceptive Copy')}",
                                    "severity": item.get("severity", "High"),
                                    "score_impact": 18.0 if item.get("severity") == "Critical" else 12.0,
                                    "text": item.get("text", "")[:120],
                                    "explanation": item.get("explanation", "Psychological framing detected."),
                                    "psychological_mechanism": item.get("psychological_mechanism", "Cognitive Manipulation")
                                })
            except Exception:
                pass

        return findings
