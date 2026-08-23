from typing import List, Dict, Any
from .base import BaseDetector, DetectionResult

class RoachMotelDetector(BaseDetector):
    name: str = "Roach Motel & Asymmetric Cancellation Friction Detector"
    category: str = "Obstruction"

    def analyze_step(self, step_data: Dict[str, Any], flow_context: Dict[str, Any]) -> List[DetectionResult]:
        results = []
        flow_type = flow_context.get("flow_type", "")
        steps = flow_context.get("steps", [])
        cancel_step_count = len(steps)
        signup_step_count = flow_context.get("signup_step_count", 1)
        
        # Detect Phone-Call or Support-Ticket Only barriers
        barrier_detected = step_data.get("cancellation_barrier")
        if barrier_detected:
            results.append(DetectionResult(
                category="Obstruction",
                pattern_name="Offline/Support-Wall Cancellation Barrier",
                severity="Critical",
                score_impact=35.0,
                plain_explanation="Subscription can be created online in 1 click, but cancellation forces user to call a toll-free number or email human support during limited business hours.",
                dom_selector=barrier_detected.get("selector", ".call-support-wall"),
                dom_snippet=barrier_detected.get("html", "<p>To cancel, please call 1-800-555-0199 Mon-Fri 9am-5pm EST</p>"),
                element_text="Call to Cancel Mandate",
                bounding_box=barrier_detected.get("bounding_box"),
                psychological_mechanism="Friction-Induced Retention / Sludge: Imposes high cognitive and social anxiety barriers to dissuade users from revoking consent.",
                regulatory_citation="FTC Click-to-Cancel Final Rule (16 CFR Part 425.6); California Auto-Renewal Law AB 390 / SB 313",
                regulatory_statute="FTC 16 CFR § 425.6(c) (Click-to-Cancel Mandate)",
                remedy_recommendation="Provide a simple, immediate online cancellation mechanism that is at least as easy to use as the enrollment process."
            ))

        # Check multi-page labyrinth cancellation flows
        if flow_type == "cancellation" and cancel_step_count >= 3:
            results.append(DetectionResult(
                category="Obstruction",
                pattern_name="Roach Motel / Multi-Step Cancellation Labyrinth",
                severity="Critical" if cancel_step_count >= 4 else "High",
                score_impact=30.0 if cancel_step_count >= 4 else 20.0,
                plain_explanation=f"Cancellation requires {cancel_step_count} consecutive friction screens (offers, exit surveys, guilt prompts) vs 1-step signup ({signup_step_count} step). Asymmetry ratio: {cancel_step_count}:{signup_step_count}.",
                dom_selector=step_data.get("selector", ".cancel-flow-step"),
                dom_snippet=f"<div class='step-indicator'>Step {cancel_step_count} of Cancel Flow</div>",
                element_text=f"Cancellation Step {cancel_step_count}",
                bounding_box=step_data.get("bounding_box"),
                psychological_mechanism="Decision Fatigue & Sunk Cost Depletion: Wears down consumer resolve with successive retention roadblocks.",
                regulatory_citation="FTC Enforcement Policy on Negative Option Subscriptions; EU Digital Services Act Article 25",
                regulatory_statute="FTC Docket No. R011002 & DSA Art. 25(1)",
                remedy_recommendation="Implement symmetrical 1-click direct cancellation with no retention surveys before final confirmation."
            ))

        return results

