import os
import time
import json
import uuid
import re
from typing import List, Dict, Any, Optional, Callable
import requests
from .tool_definitions import MCP_TOOL_DEFINITIONS

class AutonomousMCPAgent:
    """
    Autonomous Model Context Protocol (MCP) Agent Controller.
    Supports Groq (`gsk_...`), xAI Grok (`xai-...`), and OpenAI (`sk-...`).
    """
    def __init__(self, api_key: str):
        self.api_key = api_key.strip()
        if self.api_key.startswith("gsk_"):
            self.endpoint = "https://api.groq.com/openai/v1/chat/completions"
            self.model = "llama-3.3-70b-versatile"
            self.provider_label = "Groq Llama 3.3"
        elif self.api_key.startswith("xai-"):
            self.endpoint = "https://api.x.ai/v1/chat/completions"
            self.model = "grok-beta"
            self.provider_label = "xAI Grok"
        else:
            self.endpoint = "https://api.openai.com/v1/chat/completions"
            self.model = "gpt-4o-mini"
            self.provider_label = "OpenAI GPT"

    def plan_and_execute_step(
        self,
        page,
        step_idx: int,
        flow_type: str,
        current_dom: Dict[str, Any],
        emit: Callable[[str, Dict[str, Any]], None]
    ) -> Dict[str, Any]:
        """
        Gives the LLM full MCP tool control over the live Playwright page.
        """
        emit("log", {"message": f"[AI Engine] Analyzing live DOM state via {self.provider_label}..."})

        # Format interactive elements for LLM context
        interactive_summary = {
            "url": current_dom.get("url"),
            "title": current_dom.get("title"),
            "step_number": step_idx,
            "flow_goal": f"Investigate deceptive patterns in {flow_type} funnel.",
            "buttons": [
                b.get("text") for b in current_dom.get("buttons", [])[:8] if b.get("text")
            ],
            "checkboxes": [
                {"label": cb.get("label"), "checked": cb.get("checked")} 
                for cb in current_dom.get("checkboxes", [])[:5]
            ],
            "prices": current_dom.get("prices", [])[:5],
            "text_snippet": current_dom.get("page_text", "")[:300]
        }

        system_prompt = (
            "You are Pattern Guard AI, a consumer protection forensic auditor. "
            "Analyze the website DOM state for manipulative UX (dark patterns, sneaked add-ons, drip fees, confirmshaming, roach motel). "
            "Respond in JSON format with two keys:\n"
            "1. 'thought': your brief reasoning.\n"
            "2. 'violations': list of objects with keys: 'pattern_name', 'severity' (Critical, High, Medium), 'explanation', 'psychological_mechanism'.\n"
            "3. 'click_target': text of next button to click (optional)."
        )

        user_prompt = f"Live Website State:\n{json.dumps(interactive_summary)}"

        findings = []
        should_finish = False

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.1
            }

            resp = requests.post(self.endpoint, headers=headers, json=payload, timeout=8)
            if resp.status_code == 200:
                data = resp.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                # Extract JSON using regex
                json_match = re.search(r"(\{.*\})", content, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group(1))
                else:
                    parsed = json.loads(content)

                thought = parsed.get("thought")
                if thought:
                    emit("log", {"message": f"[AI Reasoning]: {thought}"})

                # Process violations detected by AI
                violations = parsed.get("violations", [])
                for v in violations:
                    finding = {
                        "id": f"find_{uuid.uuid4().hex[:8]}",
                        "category": "Psychological Coercion",
                        "pattern_name": f"{self.provider_label}: {v.get('pattern_name', 'Deceptive Pattern')}",
                        "severity": v.get("severity", "High"),
                        "score_impact": 22.0 if v.get("severity") == "Critical" else 15.0,
                        "plain_explanation": v.get("explanation", "AI flagged deceptive psychological framing."),
                        "dom_selector": ".deceptive-ui",
                        "dom_snippet": "<span>Deceptive Framing</span>",
                        "element_text": v.get("pattern_name", ""),
                        "bounding_box": None,
                        "psychological_mechanism": v.get("psychological_mechanism", "Cognitive Bias Exploitation"),
                        "regulatory_citation": "FTC Act § 5 / EU DSA Art. 25",
                        "regulatory_statute": "15 U.S.C. § 45",
                        "remedy_recommendation": "Use neutral, transparent choice architecture."
                    }
                    findings.append(finding)
                    emit("log", {"message": f"[AI Violation Flagged]: {finding['pattern_name']}"})

                # Click target if suggested by AI
                click_target = parsed.get("click_target")
                if click_target and page:
                    try:
                        locator = page.locator(f"button:has-text('{click_target}'), a:has-text('{click_target}')").first
                        if locator.is_visible(timeout=1000):
                            emit("log", {"message": f"[AI Action]: Clicking '{click_target}'..."})
                            locator.click(timeout=2000)
                            time.sleep(1.0)
                    except Exception:
                        pass

            else:
                emit("log", {"message": f"[AI Notice]: Provider returned status {resp.status_code}. Using deterministic rules."})
        except Exception as ex:
            emit("log", {"message": f"[AI Notice]: {ex}. Using deterministic rules."})

        return {
            "findings": findings,
            "should_finish": should_finish
        }
