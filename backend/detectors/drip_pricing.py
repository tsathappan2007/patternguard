import re
from typing import List, Dict, Any
from .base import BaseDetector, DetectionResult

DRIP_FEE_KEYWORDS = [
    r"service fee", r"convenience fee", r"platform fee", r"processing fee",
    r"handling fee", r"resort fee", r"facility charge", r"admin fee",
    r"regulatory fee", r"security surcharge", r"booking fee"
]

class DripPricingDetector(BaseDetector):
    name: str = "Hidden Cost & Drip Pricing Detector"
    category: str = "Hidden Costs"

    def analyze_step(self, step_data: Dict[str, Any], flow_context: Dict[str, Any]) -> List[DetectionResult]:
        results = []
        step_number = step_data.get("step_number", 1)
        current_price = step_data.get("price_detected")
        current_currency = step_data.get("price_currency")
        current_context = step_data.get("page_context")
        all_steps = flow_context.get("steps", [])
        
        # Check fee line items on current page
        fee_elements = step_data.get("fee_line_items", []) if current_context in {"cart", "checkout"} else []
        for fee in fee_elements:
            fee_name = fee.get("name", "")
            fee_amount = fee.get("amount", 0.0)
            fee_symbol = fee.get("currency_symbol") or step_data.get("price_symbol") or "$"
            is_mandatory = fee.get("is_mandatory", True)
            
            for kw in DRIP_FEE_KEYWORDS:
                if re.search(kw, fee_name, re.IGNORECASE) and fee_amount > 0:
                    results.append(DetectionResult(
                        category="Hidden Costs",
                        pattern_name="Drip Pricing / Undisclosed Mandatory Surcharge",
                        severity="High",
                        score_impact=22.0,
                        plain_explanation=f"Revealed unadvertised mandatory fee '{fee_name}' ({fee_symbol}{fee_amount:.2f}) on Step {step_number}. This fee was absent from initial search/product pricing.",
                        dom_selector=fee.get("selector", ".drip-fee-row"),
                        dom_snippet=fee.get("html", f"<div class='fee-row'><span>{fee_name}</span><span>{fee_symbol}{fee_amount:.2f}</span></div>"),
                        element_text=f"{fee_name}: {fee_symbol}{fee_amount:.2f}",
                        bounding_box=fee.get("bounding_box"),
                        psychological_mechanism="Sunk Cost Fallacy & Escalation of Commitment: Consumers invest effort through steps and feel compelled to finish despite unexpected price inflation.",
                        regulatory_citation="FTC Rule on Unfair or Deceptive Fees (16 CFR Part 464); EU Unfair Commercial Practices Directive 2005/29/EC",
                        regulatory_statute="FTC 16 CFR § 464.3 & UK Digital Markets Act",
                        remedy_recommendation="Adopt All-In Pricing: Display the total mandatory price inclusive of all non-optional fees from the very first product display."
                    ))

        # Check total price drift across multi-step flow
        if step_number > 1 and all_steps:
            first_step = all_steps[0]
            first_step_price = first_step.get("price_detected")
            first_currency = first_step.get("price_currency")
            valid_contexts = (
                first_step.get("page_context") in {"product", "cart", "checkout"}
                and current_context in {"cart", "checkout"}
            )
            valid_price_roles = (
                first_step.get("price_role") in {"product", "total"}
                and step_data.get("price_role") == "total"
            )
            same_currency = bool(first_currency and current_currency and first_currency == current_currency)
            has_fee_evidence = any(float(fee.get("amount", 0) or 0) > 0 for fee in fee_elements)
            if (
                valid_contexts and valid_price_roles and same_currency and has_fee_evidence
                and first_step_price and current_price and current_price > first_step_price
            ):
                price_delta = current_price - first_step_price
                percent_increase = (price_delta / first_step_price) * 100
                currency_symbol = step_data.get("price_symbol") or first_step.get("price_symbol") or current_currency
                
                if percent_increase >= 12.0 and not step_data.get("user_added_items", False):
                    results.append(DetectionResult(
                        category="Hidden Costs",
                        pattern_name="Late-Stage Checkout Price Inflation",
                        severity="Critical",
                        score_impact=28.0,
                        plain_explanation=f"Total checkout price escalated by +{currency_symbol}{price_delta:.2f} (+{percent_increase:.1f}%) between Step 1 ({currency_symbol}{first_step_price:.2f}) and Step {step_number} ({currency_symbol}{current_price:.2f}) with mandatory fee evidence present.",
                        dom_selector=step_data.get("price_selector", ".checkout-final-total"),
                        dom_snippet=f"<div class='final-total'>Final Total: {currency_symbol}{current_price:.2f} (Initial was {currency_symbol}{first_step_price:.2f})</div>",
                        element_text=f"Total: {currency_symbol}{current_price:.2f}",
                        bounding_box=step_data.get("price_bounding_box"),
                        psychological_mechanism="Bait-and-Switch: Lures consumers with low headline price, then surreptitiously inflates final transaction cost.",
                        regulatory_citation="FTC Junk Fee Guidance; CFPB Circular 2022-06; California SB 478 (Honest Pricing Law)",
                        regulatory_statute="Cal. Civ. Code § 1770(a)(29)",
                        remedy_recommendation="State accurate total upfront. Itemize optional add-ons only with explicit opt-in checkboxes."
                    ))

        return results

