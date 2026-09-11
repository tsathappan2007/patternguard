import uuid
from typing import List, Dict, Any, Optional
from .base import DetectionResult
from .sneak_into_basket import SneakIntoBasketDetector
from .drip_pricing import DripPricingDetector
from .confirmshaming import ConfirmshamingDetector
from .fake_urgency import FakeUrgencyDetector
from .roach_motel import RoachMotelDetector
from .contrast_visual import VisualContrastDetector
from .disguised_ads import DisguisedAdsDetector
from .ai_analyzer import CoercivePatternAIAnalyzer

class DarkPatternEngine:
    def __init__(self):
        self.detectors = [
            SneakIntoBasketDetector(),
            DripPricingDetector(),
            ConfirmshamingDetector(),
            FakeUrgencyDetector(),
            RoachMotelDetector(),
            VisualContrastDetector(),
            DisguisedAdsDetector()
        ]
        self.ai_analyzer = CoercivePatternAIAnalyzer()

    def analyze_step(
        self,
        step_data: Dict[str, Any],
        flow_context: Dict[str, Any],
        api_key: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        findings = []
        
        # Run rule detectors
        for detector in self.detectors:
            try:
                results = detector.analyze_step(step_data, flow_context)
                for res in results:
                    findings.append({
                        "id": f"find_{uuid.uuid4().hex[:10]}",
                        "category": res.category,
                        "pattern_name": res.pattern_name,
                        "severity": res.severity,
                        "score_impact": res.score_impact,
                        "plain_explanation": res.plain_explanation,
                        "dom_selector": res.dom_selector,
                        "dom_snippet": res.dom_snippet,
                        "element_text": res.element_text,
                        "bounding_box": res.bounding_box,
                        "psychological_mechanism": res.psychological_mechanism,
                        "regulatory_citation": res.regulatory_citation,
                        "regulatory_statute": res.regulatory_statute,
                        "remedy_recommendation": res.remedy_recommendation
                    })
            except Exception as e:
                print(f"[Detector Error] {detector.name}: {e}")

        # Run copy analysis
        text_corpus = [
            elem.get("text", "") for elem in step_data.get("interactive_elements", [])
        ] + [
            elem.get("text", "") for elem in step_data.get("buttons", [])
        ] + [step_data.get("page_text", "")]
        
        # Semantic provider inference is performed once by the crawler. This layer
        # remains deterministic so a configured key cannot cause duplicate calls.
        ai_findings = self.ai_analyzer.analyze_text_corpus(text_corpus, allow_external=False)
        for af in ai_findings:
            pattern_lower = af.get("pattern", "").lower()
            if "confirmshaming" in pattern_lower and any(f["category"] == "Confirmshaming" for f in findings):
                continue
            if "scarcity" in pattern_lower and any(f["category"] == "Urgency" for f in findings):
                continue
            findings.append({
                "id": f"find_{uuid.uuid4().hex[:10]}",
                "category": "Psychological Coercion",
                "pattern_name": af.get("pattern", "Deceptive Framing"),
                "severity": af.get("severity", "Medium"),
                "score_impact": af.get("score_impact", 15.0),
                "plain_explanation": af.get("explanation", "Psychological nudge detected"),
                "dom_selector": ".coercive-copy",
                "dom_snippet": f"<span>{af.get('text', '')}</span>",
                "element_text": af.get("text", ""),
                "bounding_box": None,
                "psychological_mechanism": af.get("psychological_mechanism", "Cognitive Bias Exploitation"),
                "regulatory_citation": "FTC Unfair Commercial Practices / EU Digital Services Act Art. 25",
                "regulatory_statute": "FTC 15 U.S.C. § 45",
                "remedy_recommendation": "Use neutral, non-coercive factual language."
            })

        return findings

