import re
from typing import List, Dict, Any
from .base import BaseDetector, DetectionResult

CONFIRMSHAMING_PATTERNS = [
    (r"no thanks[,\.\s]+i (don't|hate|prefer not|don't want to) (save|saving|money|discounts?|protect)", "Financial guilt-trip"),
    (r"i prefer (to )?pay(ing)? full price", "Cost-shaming"),
    (r"no[,\.\s]+i (don't care about|hate|don't want) (security|privacy|safety|protecting)", "Security disregard guilt"),
    (r"i don't want (to save|free|discounts?|deals?|growth|success|more clients)", "Deprecating decline choice"),
    (r"no[,\.\s]+i('d| would) rather (waste money|struggle|stay average|fail)", "Negative self-attribution"),
    (r"no thanks[,\.\s]+i('m fine|already have) (losing money|paying more)", "Financial self-harm copy"),
    (r"cancel and lose all my (data|work|leads|benefits|progress) forever", "Catastrophic loss framing"),
    (r"yes[,\.\s]+i want to give up my (discount|benefits|status|rewards)", "Loss-framing confirmation button")
]

class ConfirmshamingDetector(BaseDetector):
    name: str = "Confirmshaming & Manipulative Opt-out Detector"
    category: str = "Confirmshaming"

    def analyze_step(self, step_data: Dict[str, Any], flow_context: Dict[str, Any]) -> List[DetectionResult]:
        results = []
        interactive_elements = step_data.get("interactive_elements", [])
        
        for elem in interactive_elements:
            text = elem.get("text", "").strip().lower()
            if not text or len(text) < 4:
                continue
                
            for pattern, reason in CONFIRMSHAMING_PATTERNS:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    results.append(DetectionResult(
                        category="Confirmshaming",
                        pattern_name="Manipulative Decline Copy / Confirmshaming",
                        severity="High",
                        score_impact=24.0,
                        plain_explanation=f"Detected confirmshaming text on decline element: \"{elem.get('text', '')}\". Forces consumer to affirm a derogatory statement to decline an offer.",
                        dom_selector=elem.get("selector", "button.decline-offer"),
                        dom_snippet=elem.get("html", f"<button class='subtle-link'>{elem.get('text', '')}</button>"),
                        element_text=elem.get("text", ""),
                        bounding_box=elem.get("bounding_box"),
                        psychological_mechanism="Emotional Manipulation & Guilt Induction: Evokes cognitive dissonance and regret by forcing users into self-deprecating affirmations.",
                        regulatory_citation="FTC Policy Statement on Dark Patterns; EU Digital Services Act Article 25; UK CMA Dark Patterns Guidance",
                        regulatory_statute="FTC Matter No. P214504 / DSA Art. 25(1)",
                        remedy_recommendation="Use neutral, objective language for all choices (e.g. 'No, thanks' or 'Skip offer' rather than guilt-inducing statements)."
                    ))
                    break

        return results

