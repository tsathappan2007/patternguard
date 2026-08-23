import re
from typing import List, Dict, Any
from .base import BaseDetector, DetectionResult

class DisguisedAdsDetector(BaseDetector):
    name: str = "Disguised CTA & Asymmetric Button Weight Detector"
    category: str = "Deceptive Architecture"

    def analyze_step(self, step_data: Dict[str, Any], flow_context: Dict[str, Any]) -> List[DetectionResult]:
        results = []
        buttons = step_data.get("buttons", [])
        
        # Check asymmetric CTA pairs (e.g. giant vibrant "Upgrade Now" vs invisible "Keep Basic")
        if len(buttons) >= 2:
            primary_btn = None
            secondary_btn = None
            
            for b in buttons:
                text = b.get("text", "").lower()
                is_accept = any(kw in text for kw in ["upgrade", "add to order", "keep my discount", "continue with premium", "accept all"])
                is_decline = any(kw in text for kw in ["no thanks", "skip", "continue without", "decline", "cancel", "manage cookies"])
                
                if is_accept and not primary_btn:
                    primary_btn = b
                if is_decline and not secondary_btn:
                    secondary_btn = b
                    
            if primary_btn and secondary_btn:
                p_area = (primary_btn.get("bounding_box", {}).get("width", 100) * 
                          primary_btn.get("bounding_box", {}).get("height", 40))
                s_area = (secondary_btn.get("bounding_box", {}).get("width", 50) * 
                          secondary_btn.get("bounding_box", {}).get("height", 20))
                
                p_color = primary_btn.get("background_color", "")
                s_color = secondary_btn.get("background_color", "")
                
                # If primary is 4x larger or secondary is an unstyled faint link
                if (p_area > s_area * 3.5) or ("transparent" in s_color and "rgb(255" not in p_color):
                    results.append(DetectionResult(
                        category="Deceptive Architecture",
                        pattern_name="Asymmetric Choice Architecture / Visual Interference",
                        severity="High",
                        score_impact=20.0,
                        plain_explanation=f"Aggressive visual weight disparity between primary opt-in ('{primary_btn.get('text', '')}') and hidden decline action ('{secondary_btn.get('text', '')}'). Primary CTA is heavily accentuated while decline path is disguised as plain text.",
                        dom_selector=primary_btn.get("selector", "button.primary-upsell"),
                        dom_snippet=f"<div>{primary_btn.get('html', '<button>Accept</button>')} / {secondary_btn.get('html', '<a>Skip</a>')}</div>",
                        element_text=f"{primary_btn.get('text', '')} vs {secondary_btn.get('text', '')}",
                        bounding_box=primary_btn.get("bounding_box"),
                        psychological_mechanism="Visual Salience Hijacking: Channels user gaze and default motor reflex toward the monetized choice.",
                        regulatory_citation="EU Digital Services Act Article 25; FTC Deceptive Design Patterns Staff Report",
                        regulatory_statute="DSA Regulation (EU) 2022/2065 Art. 25",
                        remedy_recommendation="Give both accept and decline actions equal visual weight, contrast, and prominence."
                    ))

        return results

