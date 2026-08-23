import re
from typing import List, Dict, Any
from .base import BaseDetector, DetectionResult

SNEAK_KEYWORDS = [
    r"warranty", r"insurance", r"protection plan", r"express shipping",
    r"auto-renew", r"recurring", r"subscription", r"membership",
    r"carbon offset", r"priority handling", r"tip", r"donation",
    r"newsletter", r"marketing partner", r"sms alert", r"vip pass"
]

class SneakIntoBasketDetector(BaseDetector):
    name: str = "Sneak into Basket & Pre-selected Opt-in Detector"
    category: str = "Sneaking"

    def analyze_step(self, step_data: Dict[str, Any], flow_context: Dict[str, Any]) -> List[DetectionResult]:
        results = []
        dom_elements = step_data.get("interactive_elements", [])
        
        for elem in dom_elements:
            tag = elem.get("tag", "").lower()
            elem_type = elem.get("type", "").lower()
            is_checked = elem.get("checked", False)
            text = (elem.get("text", "") + " " + elem.get("label", "") + " " + elem.get("name", "")).strip()
            
            # Check pre-checked checkboxes or radio buttons with commercial/opt-in terms
            if tag == "input" and elem_type in ["checkbox", "radio"] and is_checked:
                matched_keywords = [kw for kw in SNEAK_KEYWORDS if re.search(kw, text, re.IGNORECASE)]
                
                # Check if it is marked as optional or adds a monetary value
                has_price = bool(re.search(r"(\$|€|£|\bUSD\b|\bEUR\b|\/mo|\/yr|\/month)\s*\d+(\.\d{2})?", text, re.IGNORECASE))
                
                if matched_keywords or has_price:
                    matched_term = matched_keywords[0] if matched_keywords else "unsolicited add-on"
                    severity = "Critical" if has_price else "High"
                    score_impact = 25.0 if has_price else 18.0
                    
                    results.append(DetectionResult(
                        category="Sneaking",
                        pattern_name="Pre-selected Add-on / Sneak into Basket",
                        severity=severity,
                        score_impact=score_impact,
                        plain_explanation=f"Found pre-selected '{matched_term}' opt-in ({text[:60]}...). Consumers are enrolled or charged by default without explicit affirmative consent.",
                        dom_selector=elem.get("selector", f"input[type={elem_type}][checked]"),
                        dom_snippet=elem.get("html", f"<input type='{elem_type}' checked /> {text}"),
                        element_text=text,
                        bounding_box=elem.get("bounding_box"),
                        psychological_mechanism="Default Effect / Inertia Exploitation: Capitalizes on user cognitive bias toward keeping pre-selected defaults.",
                        regulatory_citation="FTC Act Section 5 Unfair/Deceptive Practices; EU DSA Article 25; California AB 390 (Negative Option Billing)",
                        regulatory_statute="FTC 15 U.S.C. § 45 & EU Reg 2022/2065",
                        remedy_recommendation="Uncheck all optional items by default and require clear, unambiguous affirmative opt-in with explicit cost disclosure."
                    ))

            # Detect stealth auto-added cart items with default toggles
            if elem.get("is_auto_added", False):
                results.append(DetectionResult(
                    category="Sneaking",
                    pattern_name="Automated Basket Injection",
                    severity="Critical",
                    score_impact=30.0,
                    plain_explanation=f"Item '{elem.get('item_name', 'Protection Plan')}' was automatically injected into the cart without consumer action.",
                    dom_selector=elem.get("selector", ".cart-injected-item"),
                    dom_snippet=elem.get("html", "<div class='cart-item auto-added'>Protection Plan</div>"),
                    element_text=elem.get("item_name", "Auto Added Item"),
                    bounding_box=elem.get("bounding_box"),
                    psychological_mechanism="Hidden Cost Smuggling: Forces users to actively discover and manually delete unwanted additions.",
                    regulatory_citation="FTC Enforcement Policy on Negative Option Marketing (16 CFR § 425); EU Consumer Rights Directive Art. 22",
                    regulatory_statute="FTC Enforcement 86 FR 60822",
                    remedy_recommendation="Remove automatic basket additions immediately. Present add-ons as explicit separate purchase options."
                ))

        return results

