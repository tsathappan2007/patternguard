import os
import json
import re
from typing import Dict, Any, List, Optional, Callable
import requests
import urllib.parse
import ipaddress
import socket

# Cache fetched model per API key to avoid repeat lookups
_CACHED_MODELS: Dict[str, str] = {}

def get_best_available_model(endpoint_base: str, api_key: str, provider_name: str) -> str:
    """Queries the provider's /models endpoint to dynamically get active model IDs."""
    cache_key = f"{provider_name}_{endpoint_base}_{api_key[:10]}"
    if cache_key in _CACHED_MODELS:
        return _CACHED_MODELS[cache_key]

    try:
        models_url = endpoint_base.replace("/chat/completions", "/models")
        headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        resp = requests.get(models_url, headers=headers, timeout=3.5)
        if resp.status_code == 200:
            data = resp.json().get("data", [])
            model_ids = [m.get("id") for m in data if m.get("id")]
            
            # Prioritize best suited models
            preferred = [
                "llama-3.3-70b-versatile",
                "llama-3.1-8b-instant",
                "llama-3.1-70b-versatile",
                "llama3-70b-8192",
                "qwen-2.5-32b",
                "deepseek-r1-distill-llama-70b",
                "gpt-4o-mini",
                "gpt-4o",
                "grok-2",
                "grok-2-latest"
            ]
            for pref in preferred:
                if pref in model_ids:
                    _CACHED_MODELS[cache_key] = pref
                    return pref
            
            # If preferred not found, find any chat/llama/gpt model
            chat_models = [m for m in model_ids if any(k in m.lower() for k in ["llama", "gpt", "grok", "qwen", "mistral", "chat"])]
            if chat_models:
                _CACHED_MODELS[cache_key] = chat_models[0]
                return chat_models[0]
            
            if model_ids:
                _CACHED_MODELS[cache_key] = model_ids[0]
                return model_ids[0]
    except Exception:
        pass

    # Fallback defaults
    if provider_name == "Groq":
        return "llama-3.1-8b-instant"
    elif provider_name == "xAI Grok":
        return "grok-2"
    else:
        return "gpt-4o-mini"

def _validate_custom_endpoint(endpoint: str) -> str:
    parsed = urllib.parse.urlparse(endpoint)
    host = (parsed.hostname or "").lower()
    is_local = host in {"localhost", "127.0.0.1", "::1"}
    if parsed.scheme not in ({"http", "https"} if is_local else {"https"}):
        raise ValueError("Custom AI endpoint must use HTTPS, except for localhost development")
    if not host or parsed.username or parsed.password:
        raise ValueError("Invalid custom AI endpoint")
    if not is_local:
        try:
            addresses = {item[4][0] for item in socket.getaddrinfo(host, parsed.port or 443, type=socket.SOCK_STREAM)}
        except socket.gaierror as error:
            raise ValueError("Custom AI endpoint hostname could not be resolved") from error
        if any(not ipaddress.ip_address(address).is_global for address in addresses):
            raise ValueError("Custom AI endpoint may not target a private or reserved network")
    return endpoint.rstrip("/")


def call_ai_inference(
    api_key: str,
    prompt_data: Dict[str, Any],
    emit_log: Optional[Callable[[str], None]] = None,
    endpoint_override: Optional[str] = None,
    model_override: Optional[str] = None
) -> List[Dict[str, Any]]:
    key = (api_key or "").strip()
    if not key and not endpoint_override:
        return []

    # Detect provider, or use an explicitly configured OpenAI-compatible endpoint.
    if endpoint_override:
        base = _validate_custom_endpoint(endpoint_override)
        endpoint = base if base.endswith("/chat/completions") else f"{base}/chat/completions"
        provider_name = "Custom OpenAI-Compatible"
    elif key.startswith("gsk_") or "groq" in key.lower():
        endpoint = "https://api.groq.com/openai/v1/chat/completions"
        provider_name = "Groq"
    elif key.startswith("xai-"):
        endpoint = "https://api.x.ai/v1/chat/completions"
        provider_name = "xAI Grok"
    elif key.startswith("sk-or-"):
        endpoint = "https://openrouter.ai/api/v1/chat/completions"
        provider_name = "OpenRouter"
    else:
        endpoint = "https://api.openai.com/v1/chat/completions"
        provider_name = "OpenAI"

    # Dynamically find the active model for this user's key
    active_model = model_override or get_best_available_model(endpoint, key, provider_name)

    if emit_log:
        emit_log(f"[AI Layer] Connected to {provider_name} ({active_model})...")

    system_prompt = (
        "You are Pattern Guard's AI Dark Pattern Legal Auditor. "
        "Analyze the website step data for deceptive UX patterns: sneaked add-ons, drip pricing, confirmshaming, fake countdown clocks, roach motel cancellation. "
        "Respond with a JSON object containing a 'findings' list where each finding has: "
        "'pattern' (string), 'severity' ('Critical'|'High'|'Medium'), 'explanation' (string), 'mechanism' (string)."
    )

    user_prompt = f"Website Step Data:\n{json.dumps(prompt_data)}"

    try:
        headers = {"Content-Type": "application/json"}
        if key:
            headers["Authorization"] = f"Bearer {key}"
        payload = {
            "model": active_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.1,
            "max_tokens": 400
        }

        resp = requests.post(endpoint, headers=headers, json=payload, timeout=7)
        
        if resp.status_code == 200:
            raw_text = resp.json().get("choices", [{}])[0].get("message", {}).get("content", "")
            json_match = re.search(r"(\{.*\})", raw_text, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group(1))
                results = []
                for item in parsed.get("findings", []):
                    finding = {
                        "category": "Psychological Coercion",
                        "pattern_name": f"{provider_name}: {item.get('pattern', 'Deceptive Pattern')}",
                        "severity": item.get("severity", "High"),
                        "score_impact": 20.0 if item.get("severity") == "Critical" else 15.0,
                        "plain_explanation": item.get("explanation", "AI identified deceptive psychological framing."),
                        "dom_selector": ".deceptive-ui",
                        "dom_snippet": "<span>Deceptive Framing</span>",
                        "element_text": item.get("pattern", ""),
                        "bounding_box": None,
                        "psychological_mechanism": item.get("mechanism", "Cognitive Bias Exploitation"),
                        "regulatory_citation": "FTC Act § 5 / EU DSA Art. 25",
                        "regulatory_statute": "15 U.S.C. § 45",
                        "remedy_recommendation": "Use transparent, non-coercive choice architecture."
                    }
                    results.append(finding)
                    if emit_log:
                        emit_log(f"[AI Flagged]: {finding['pattern_name']}")
                return results
        else:
            err_msg = resp.json().get("error", {}).get("message", f"HTTP {resp.status_code}") if resp.headers.get("content-type", "").startswith("application/json") else f"HTTP {resp.status_code}"
            if emit_log:
                emit_log(f"[AI Notice]: {provider_name} ({err_msg}). Falling back to deterministic rules.")
    except Exception as e:
        if emit_log:
            emit_log(f"[AI Notice]: {str(e)[:60]}. Using deterministic rules.")

    return []
