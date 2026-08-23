import re
import math
from typing import List, Dict, Any
from .base import BaseDetector, DetectionResult

def parse_color_to_rgb(color_str: str):
    if not color_str:
        return (0, 0, 0)
    color_str = color_str.strip().lower()
    
    # Handle hex #ffffff or #fff
    if color_str.startswith("#"):
        hex_val = color_str.lstrip("#")
        if len(hex_val) == 3:
            hex_val = "".join([c*2 for c in hex_val])
        if len(hex_val) == 6:
            try:
                return (int(hex_val[0:2], 16), int(hex_val[2:4], 16), int(hex_val[4:6], 16))
            except ValueError:
                pass
                
    # Handle rgb(...) or rgba(...)
    rgb_match = re.match(r"rgba?\((\d+),\s*(\d+),\s*(\d+)", color_str)
    if rgb_match:
        return (int(rgb_match.group(1)), int(rgb_match.group(2)), int(rgb_match.group(3)))
        
    return (100, 100, 100)

def calculate_luminance(r, g, b):
    a = [c / 255.0 for c in (r, g, b)]
    a = [((c / 12.92) if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4) for c in a]
    return 0.2126 * a[0] + 0.7152 * a[1] + 0.0722 * a[2]

def calculate_contrast_ratio(rgb1, rgb2):
    lum1 = calculate_luminance(*rgb1)
    lum2 = calculate_luminance(*rgb2)
    brightest = max(lum1, lum2)
    darkest = min(lum1, lum2)
    return (brightest + 0.05) / (darkest + 0.05)

CRITICAL_DISCLOSURE_KEYWORDS = [
    r"cancel anytime", r"recurring charge", r"auto-renews?", r"billed annually",
    r"terms and conditions", r"privacy policy", r"non-refundable", r"trial ends in",
    r"subscription begins", r"waive right", r"opt out", r"manage membership"
]

class VisualContrastDetector(BaseDetector):
    name: str = "Visual Deception & Low-Contrast Disclosure Detector"
    category: str = "Visual Deception"

    def analyze_step(self, step_data: Dict[str, Any], flow_context: Dict[str, Any]) -> List[DetectionResult]:
        results = []
        elements = step_data.get("interactive_elements", []) + step_data.get("disclosure_elements", [])
        
        for elem in elements:
            text = elem.get("text", "").strip()
            if not text:
                continue
                
            color_str = elem.get("color", "")
            bg_str = elem.get("background_color", "rgb(255, 255, 255)")
            font_size_px = elem.get("font_size_px", 14.0)
            
            # Check if this text contains important billing/cancellation disclaimers
            is_critical = any(re.search(kw, text, re.IGNORECASE) for kw in CRITICAL_DISCLOSURE_KEYWORDS)
            
            rgb_fg = parse_color_to_rgb(color_str)
            rgb_bg = parse_color_to_rgb(bg_str)
            contrast_ratio = calculate_contrast_ratio(rgb_fg, rgb_bg)
            
            # WCAG AA requires 4.5:1 for regular text, 3.0:1 for large text. Dark patterns often drop to < 2.0:1 or < 11px
            if is_critical:
                if contrast_ratio < 2.5:
                    results.append(DetectionResult(
                        category="Visual Deception",
                        pattern_name="Camouflaged Low-Contrast Disclosure",
                        severity="Critical" if contrast_ratio < 1.8 else "High",
                        score_impact=26.0 if contrast_ratio < 1.8 else 18.0,
                        plain_explanation=f"Critical disclosure \"{text[:70]}...\" rendered with illegible contrast ratio of {contrast_ratio:.2f}:1 (WCAG minimum is 4.5:1). Color: {color_str} on {bg_str}.",
                        dom_selector=elem.get("selector", ".hidden-disclosure"),
                        dom_snippet=elem.get("html", f"<p style='color:{color_str};'>{text}</p>"),
                        element_text=text,
                        bounding_box=elem.get("bounding_box"),
                        psychological_mechanism="Visual Suppression: Camouflages legally required terms against background to prevent conscious evaluation.",
                        regulatory_citation="FTC Clear and Conspicuous Disclosure Standards; WCAG 2.1 Level AA; EU Unfair Commercial Practices Directive",
                        regulatory_statute="16 CFR § 425.4 (Conspicuousness Mandate)",
                        remedy_recommendation="Ensure all fee and renewal disclosures maintain at least 4.5:1 contrast against their background."
                    ))
                elif font_size_px < 10.5:
                    results.append(DetectionResult(
                        category="Visual Deception",
                        pattern_name="Microscopic Fine Print / Illegible Terms",
                        severity="High",
                        score_impact=18.0,
                        plain_explanation=f"Important contract clause \"{text[:70]}...\" rendered at {font_size_px:.1f}px (well below readable 12px standard).",
                        dom_selector=elem.get("selector", ".micro-font-terms"),
                        dom_snippet=elem.get("html", f"<span style='font-size:{font_size_px}px;'>{text}</span>"),
                        element_text=text,
                        bounding_box=elem.get("bounding_box"),
                        psychological_mechanism="Visual Attrition: Forces users to strain or skip legalese by setting micro typography.",
                        regulatory_citation="FTC Enforcement on Fine Print Deceptions; Restatement of Consumer Contracts § 3",
                        regulatory_statute="FTC Act Section 5(a)",
                        remedy_recommendation="Increase font size of all terms and cancellation instructions to at least 13px."
                    ))

        return results

