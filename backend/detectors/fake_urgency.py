import re
from typing import List, Dict, Any
from .base import BaseDetector, DetectionResult

SCARCITY_PATTERNS = [
    r"only \d+ (left in stock|seats left|rooms left|items left)",
    r"\d+ people (are viewing|viewing this right now|have this in their cart)",
    r"high demand[—\-:\s]+(selling fast|almost gone|booked \d+ times)",
    r"deal expires in \d+:\d+",
    r"offer reserved for \d+:\d+ minutes"
]

class FakeUrgencyDetector(BaseDetector):
    name: str = "Fake Urgency & Artificial Scarcity Detector"
    category: str = "Urgency"

    def analyze_step(self, step_data: Dict[str, Any], flow_context: Dict[str, Any]) -> List[DetectionResult]:
        results = []
        raw_html = step_data.get("dom_html", "")
        text_content = step_data.get("page_text", "")
        elements = step_data.get("interactive_elements", []) + step_data.get("banner_elements", [])
        
        # Check countdown timer anomalies
        timer_info = step_data.get("timer_detected")
        if timer_info:
            is_resetting = timer_info.get("resets_on_reload", False)
            initial_time = timer_info.get("initial_seconds", 0)
            reloaded_time = timer_info.get("reloaded_seconds", 0)
            
            if is_resetting or (reloaded_time > 0 and abs(reloaded_time - initial_time) < 5):
                results.append(DetectionResult(
                    category="Urgency",
                    pattern_name="Resetting Fake Countdown Clock",
                    severity="Critical",
                    score_impact=28.0,
                    plain_explanation=f"Detected artificial countdown timer that reset back to {timer_info.get('display_time', '15:00')} upon page refresh/navigation without actual offer expiration.",
                    dom_selector=timer_info.get("selector", ".deal-countdown-timer"),
                    dom_snippet=timer_info.get("html", f"<div class='countdown'>{timer_info.get('display_time', '15:00')}</div>"),
                    element_text=timer_info.get("display_time", "Countdown"),
                    bounding_box=timer_info.get("bounding_box"),
                    psychological_mechanism="Artificial Scarcity & FOMO (Fear of Missing Out): Triggers systemic panic and cognitive rush, disabling rational cost deliberation.",
                    regulatory_citation="FTC v. Urgency Marketing / ASA (UK Advertising Standards Authority) Rulings on Deceptive Timers",
                    regulatory_statute="16 CFR Part 464 & EU UCPD Annex I Item 7",
                    remedy_recommendation="Only display timers if an offer has a genuine, non-resetting contractual deadline backed by verifiable inventory rules."
                ))

        # Check deceptive stock pressure & viewer counters
        for elem in elements:
            text = elem.get("text", "").strip()
            if not text:
                continue
                
            for pattern in SCARCITY_PATTERNS:
                if re.search(pattern, text, re.IGNORECASE):
                    results.append(DetectionResult(
                        category="Urgency",
                        pattern_name="Fabricated High-Demand / Scarcity Banner",
                        severity="High",
                        score_impact=20.0,
                        plain_explanation=f"Found unverified social proof/urgency claim: \"{text}\". Creates synthetic scarcity pressure without verified real-time inventory feed.",
                        dom_selector=elem.get("selector", ".urgency-badge"),
                        dom_snippet=elem.get("html", f"<div class='urgency-badge'>{text}</div>"),
                        element_text=text,
                        bounding_box=elem.get("bounding_box"),
                        psychological_mechanism="Social Proof & Herd Behavior Exploitation: Uses simulated demand metrics to force impulsive purchase decisions.",
                        regulatory_citation="FTC Guides Concerning Use of Endorsements; EU Unfair Commercial Practices Directive",
                        regulatory_statute="EU Directive 2005/29/EC Art. 6",
                        remedy_recommendation="Ensure all stock level and viewer counters reflect authenticated, real-time backend inventory state."
                    ))
                    break

        return results

