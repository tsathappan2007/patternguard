import os
import uuid
from .db import get_db_connection, init_db
from ..evidence.annotator import annotate_screenshot

def seed_database():
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if sites already exist
    cursor.execute("SELECT COUNT(*) as cnt FROM sites")
    if cursor.fetchone()["cnt"] > 0:
        conn.close()
        return

    print("Seeding initial dark pattern audit records...")

    sample_sites = [
        {
            "id": "site_trapfit",
            "name": "GymTrap Elite Club",
            "domain": "gymtrap.internal",
            "category": "SaaS & Subscription",
            "manipulation_index": 94.5,
            "grade": "F",
            "critical_count": 3,
            "high_count": 2,
            "medium_count": 1,
            "low_count": 0,
            "top_violation": "Offline Phone-Call Cancellation Wall",
            "primary_pattern": "Obstruction",
            "ftc_risk_level": "Critical Violation Liability"
        },
        {
            "id": "site_shopsneak",
            "name": "ShopSneak Retail Pro",
            "domain": "shopsneak.internal",
            "category": "E-Commerce / Consumer Goods",
            "manipulation_index": 88.0,
            "grade": "F",
            "critical_count": 2,
            "high_count": 3,
            "medium_count": 1,
            "low_count": 0,
            "top_violation": "Pre-checked Warranty + Drip Surcharge",
            "primary_pattern": "Sneaking",
            "ftc_risk_level": "Critical Violation Liability"
        },
        {
            "id": "site_aerofare",
            "name": "AeroFare Express Flights",
            "domain": "aerofare.internal",
            "category": "Travel & Hospitality",
            "manipulation_index": 76.2,
            "grade": "F",
            "critical_count": 2,
            "high_count": 2,
            "medium_count": 2,
            "low_count": 0,
            "top_violation": "Fabricated 15-Minute Flight Seat Panic",
            "primary_pattern": "Urgency",
            "ftc_risk_level": "Critical Violation Liability"
        },
        {
            "id": "site_streamcloud",
            "name": "StreamMax Premium",
            "domain": "streammax.internal",
            "category": "Digital Media & Streaming",
            "manipulation_index": 54.0,
            "grade": "D",
            "critical_count": 0,
            "high_count": 3,
            "medium_count": 1,
            "low_count": 1,
            "top_violation": "Confirmshaming Guilt-Trip Opt-out",
            "primary_pattern": "Confirmshaming",
            "ftc_risk_level": "High"
        },
        {
            "id": "site_honestgoods",
            "name": "Ethical Basics & Supply",
            "domain": "ethicalbasics.internal",
            "category": "Sustainable Commerce",
            "manipulation_index": 6.5,
            "grade": "A+",
            "critical_count": 0,
            "high_count": 0,
            "medium_count": 0,
            "low_count": 1,
            "top_violation": "None (All-in Transparent Pricing)",
            "primary_pattern": "Clean",
            "ftc_risk_level": "Compliant"
        }
    ]

    for s in sample_sites:
        cursor.execute("""
        INSERT INTO sites (
            id, domain, name, category, manipulation_index, grade, status,
            scans_count, critical_count, high_count, medium_count, low_count,
            top_violation, primary_pattern, ftc_risk_level
        ) VALUES (?, ?, ?, ?, ?, ?, 'audited', 1, ?, ?, ?, ?, ?, ?, ?)
        """, (
            s["id"], s["domain"], s["name"], s["category"], s["manipulation_index"],
            s["grade"], s["critical_count"], s["high_count"], s["medium_count"],
            s["low_count"], s["top_violation"], s["primary_pattern"], s["ftc_risk_level"]
        ))

        scan_id = f"scan_{s['id']}_001"
        flow_type = "cancellation_audit" if "trap" in s["id"] else "checkout_audit"
        cursor.execute("""
        INSERT INTO scans (
            id, site_id, target_url, flow_type, status, manipulation_index,
            grade, total_steps, findings_count, duration_ms
        ) VALUES (?, ?, ?, ?, 'completed', ?, ?, 3, ?, 2850)
        """, (
            scan_id, s["id"], f"http://127.0.0.1:8000/mock/{s['id'].replace('site_', '')}",
            flow_type, s["manipulation_index"], s["grade"],
            s["critical_count"] + s["high_count"] + s["medium_count"] + s["low_count"]
        ))

        # Add mock findings
        if s["id"] == "site_shopsneak":
            findings_data = [
                {
                    "id": "find_shopsneak_01",
                    "category": "Sneaking",
                    "pattern_name": "Pre-selected Add-on / Sneak into Basket",
                    "severity": "Critical",
                    "score_impact": 25.0,
                    "plain_explanation": "Found pre-selected '2-Year Full Accidental Damage Protection Plan' ($18.99) checked by default without affirmative consumer click.",
                    "dom_selector": "input[type='checkbox'][name='warranty'][checked]",
                    "dom_snippet": "<input type='checkbox' checked name='warranty'> +$18.99 (Pre-selected)",
                    "element_text": "Add 2-Year Full Accidental Damage Protection Plan +$18.99",
                    "bounding_box": {"x": 680, "y": 280, "width": 420, "height": 65},
                    "psychological_mechanism": "Default Effect / Inertia Bias: Consumers assume pre-checked options are mandatory or recommended standard configurations.",
                    "regulatory_citation": "FTC Act Section 5 Unfair/Deceptive Practices; EU DSA Article 25; California AB 390",
                    "regulatory_statute": "15 U.S.C. § 45 & EU Reg 2022/2065",
                    "remedy_recommendation": "Uncheck all optional items by default; require explicit affirmative action."
                },
                {
                    "id": "find_shopsneak_02",
                    "category": "Hidden Costs",
                    "pattern_name": "Late-Stage Checkout Drip Pricing",
                    "severity": "Critical",
                    "score_impact": 28.0,
                    "plain_explanation": "Total escalated from $89.00 initial product price to $120.34 at Step 2 due to unannounced 'Regulatory & Convenience Fee' ($7.50) and 'Mandatory Studio Handling' ($4.85).",
                    "dom_selector": ".checkout-final-total",
                    "dom_snippet": "<div class='fee-row'><span>Platform Regulatory & Convenience Fee</span><span>$7.50</span></div>",
                    "element_text": "Total Due Now: $120.34 (Initial: $89.00)",
                    "bounding_box": {"x": 380, "y": 320, "width": 520, "height": 80},
                    "psychological_mechanism": "Sunk Cost Fallacy: Exploits time already invested in checkout funnel to compel acceptance of inflated totals.",
                    "regulatory_citation": "FTC Rule on Unfair or Deceptive Fees (16 CFR Part 464); California SB 478",
                    "regulatory_statute": "FTC 16 CFR § 464.3 / Cal. Civ. Code § 1770(a)(29)",
                    "remedy_recommendation": "Present all-inclusive pricing upfront from the first product screen."
                },
                {
                    "id": "find_shopsneak_03",
                    "category": "Urgency",
                    "pattern_name": "Resetting Fake Countdown Clock",
                    "severity": "High",
                    "score_impact": 22.0,
                    "plain_explanation": "Timer displaying '04:59' resets back to 5 minutes on page reload, manufacturing artificial purchase panic with no real inventory expiration.",
                    "dom_selector": ".deal-countdown-timer",
                    "dom_snippet": "<div class='deal-countdown-timer'>⚠️ CART RESERVED FOR 04:59</div>",
                    "element_text": "⚠️ CART RESERVED FOR 04:59",
                    "bounding_box": {"x": 380, "y": 80, "width": 520, "height": 45},
                    "psychological_mechanism": "Urgency Heuristic / FOMO: Reduces time available for rational price comparison.",
                    "regulatory_citation": "FTC v. Urgency Marketing / ASA Rulings on Deceptive Timers",
                    "regulatory_statute": "16 CFR Part 464 & EU UCPD Annex I",
                    "remedy_recommendation": "Do not display countdown clocks unless tied to verified external contractual deadline."
                },
                {
                    "id": "find_shopsneak_04",
                    "category": "Visual Deception",
                    "pattern_name": "Camouflaged Low-Contrast Auto-Renewal Disclosure",
                    "severity": "High",
                    "score_impact": 18.0,
                    "plain_explanation": "Annual membership auto-renewal disclosure ($119/yr) rendered at 9px in #c4c4c4 on #f3f4f6 background (contrast ratio 1.74:1, failing WCAG 4.5:1 minimum).",
                    "dom_selector": ".hidden-disclosure p",
                    "dom_snippet": "<p style='color: #c4c4c4; font-size: 9px;'>By placing this order, you agree to recurring annual membership auto-renews...</p>",
                    "element_text": "By placing this order, you agree to recurring annual membership auto-renews at $119/year",
                    "bounding_box": {"x": 380, "y": 420, "width": 520, "height": 40},
                    "psychological_mechanism": "Visual Suppression: Conspires to hide legal liability terms in illegible microprint.",
                    "regulatory_citation": "FTC Clear and Conspicuous Disclosure Guidelines; WCAG 2.1 Level AA",
                    "regulatory_statute": "16 CFR § 425.4",
                    "remedy_recommendation": "Increase font size to minimum 13px with at least 4.5:1 contrast."
                }
            ]

            # Generate annotated screenshot
            annotated_url = annotate_screenshot(
                image_path="",
                findings=findings_data,
                output_filename="seed_shopsneak_evidence.png"
            )

            for f in findings_data:
                cursor.execute("""
                INSERT INTO findings (
                    id, scan_id, step_id, site_id, category, pattern_name,
                    severity, score_impact, dom_selector, dom_snippet, element_text,
                    screenshot_path, annotated_path, plain_explanation,
                    psychological_mechanism, regulatory_citation, regulatory_statute, remedy_recommendation
                ) VALUES (?, ?, 'step_01', ?, ?, ?, ?, ?, ?, ?, ?, '/static/evidence/seed_shopsneak_evidence.png', ?, ?, ?, ?, ?, ?)
                """, (
                    f["id"], scan_id, s["id"], f["category"], f["pattern_name"],
                    f["severity"], f["score_impact"], f["dom_selector"], f["dom_snippet"],
                    f["element_text"], annotated_url, f["plain_explanation"],
                    f["psychological_mechanism"], f["regulatory_citation"], f["regulatory_statute"], f["remedy_recommendation"]
                ))

        elif s["id"] == "site_trapfit":
            findings_data = [
                {
                    "id": "find_gymtrap_01",
                    "category": "Obstruction",
                    "pattern_name": "Offline Phone-Call Cancellation Wall",
                    "severity": "Critical",
                    "score_impact": 35.0,
                    "plain_explanation": "Enrolling is 1-click online, but cancellation is blocked online and mandates calling 1-800-555-0199 during limited weekday windows.",
                    "dom_selector": ".call-support-wall",
                    "dom_snippet": "<div class='call-support-wall'>To cancel, call 1-800-555-0199 Mon-Fri 9:00 AM - 4:30 PM EST</div>",
                    "element_text": "Phone Verification Required: 1-800-555-0199",
                    "bounding_box": {"x": 420, "y": 260, "width": 440, "height": 110},
                    "psychological_mechanism": "Sludge & Social Friction: Introduces human confrontation barrier to discourage cancellation.",
                    "regulatory_citation": "FTC Click-to-Cancel Final Rule (16 CFR § 425.6); California Auto-Renewal Law AB 390",
                    "regulatory_statute": "16 CFR § 425.6(c)",
                    "remedy_recommendation": "Provide immediate symmetrical 1-click online cancellation."
                },
                {
                    "id": "find_gymtrap_02",
                    "category": "Obstruction",
                    "pattern_name": "Roach Motel / 4-Step Cancellation Labyrinth",
                    "severity": "Critical",
                    "score_impact": 30.0,
                    "plain_explanation": "Cancellation forces the user through 4 consecutive hurdle screens (guilt-tripping, retention offers, mandatory surveys, phone wall) vs 1-click signup.",
                    "dom_selector": ".cancel-flow-step",
                    "dom_snippet": "<div class='step-indicator'>Cancellation Step 1 of 4</div>",
                    "element_text": "Cancellation Step 1 of 4: Are you sure you want to surrender your progress?",
                    "bounding_box": {"x": 420, "y": 140, "width": 440, "height": 90},
                    "psychological_mechanism": "Decision Fatigue & Depletion: Repeated retention screens wear down customer resolve.",
                    "regulatory_citation": "FTC Negative Option Rule / EU Digital Services Act Article 25",
                    "regulatory_statute": "DSA Art. 25(1)",
                    "remedy_recommendation": "Allow direct single-step cancellation without multi-page friction."
                },
                {
                    "id": "find_gymtrap_03",
                    "category": "Confirmshaming",
                    "pattern_name": "Manipulative Loss-Framed Opt-Out Copy",
                    "severity": "High",
                    "score_impact": 24.0,
                    "plain_explanation": "Forces user to click: 'No thanks, I don't care about my health and want to give up my discount' to proceed with cancellation.",
                    "dom_selector": ".decline-offer",
                    "dom_snippet": "<a class='decline-offer subtle-link'>No thanks, I don't care about my health and want to give up my discount</a>",
                    "element_text": "No thanks, I don't care about my health and want to give up my discount",
                    "bounding_box": {"x": 420, "y": 440, "width": 440, "height": 35},
                    "psychological_mechanism": "Emotional Coercion: Weaponizes identity-derogating language to elicit shame.",
                    "regulatory_citation": "FTC Dark Patterns Policy Statement; UK CMA Guidelines",
                    "regulatory_statute": "FTC Docket No. P214504",
                    "remedy_recommendation": "Use neutral choices like 'Cancel Subscription' and 'Keep Subscription'."
                }
            ]

            annotated_url = annotate_screenshot(
                image_path="",
                findings=findings_data,
                output_filename="seed_gymtrap_evidence.png"
            )

            for f in findings_data:
                cursor.execute("""
                INSERT INTO findings (
                    id, scan_id, step_id, site_id, category, pattern_name,
                    severity, score_impact, dom_selector, dom_snippet, element_text,
                    screenshot_path, annotated_path, plain_explanation,
                    psychological_mechanism, regulatory_citation, regulatory_statute, remedy_recommendation
                ) VALUES (?, ?, 'step_01', ?, ?, ?, ?, ?, ?, ?, ?, '/static/evidence/seed_gymtrap_evidence.png', ?, ?, ?, ?, ?, ?)
                """, (
                    f["id"], scan_id, s["id"], f["category"], f["pattern_name"],
                    f["severity"], f["score_impact"], f["dom_selector"], f["dom_snippet"],
                    f["element_text"], annotated_url, f["plain_explanation"],
                    f["psychological_mechanism"], f["regulatory_citation"], f["regulatory_statute"], f["remedy_recommendation"]
                ))

    conn.commit()
    conn.close()
    print("Database seeding completed successfully.")

if __name__ == "__main__":
    seed_database()
