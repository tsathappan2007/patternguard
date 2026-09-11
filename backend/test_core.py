import sqlite3

import pytest

from backend.agent.flow_crawler import AutonomousFlowCrawler
from backend.database import db
from backend.detectors.engine import DarkPatternEngine
from backend.detectors.drip_pricing import DripPricingDetector
from backend.scoring.calculator import calculate_manipulation_index
from backend.mock_sites import mock_templates


def test_crawler_schema_drives_detectors():
    step = {
        "step_number": 2,
        "page_text": "Only 2 left in stock. Deal expires in 04:59.",
        "interactive_elements": [{
            "tag": "input", "type": "checkbox", "checked": True,
            "name": "warranty", "label": "Add warranty $18.99",
            "text": "Add warranty $18.99", "bounding_box": {"x": 1, "y": 2, "width": 20, "height": 20}
        }],
        "buttons": [],
        "disclosure_elements": [],
        "fee_line_items": [{"name": "Mandatory platform fee", "amount": 7.50}],
        "banner_elements": [{"text": "Only 2 left in stock"}],
        "timer_detected": {"display_time": "04:59", "resets_on_reload": True},
        "price_detected": 120.0,
        "price_currency": "USD",
        "price_symbol": "$",
        "price_role": "total",
        "page_context": "checkout",
    }
    context = {"flow_type": "checkout", "steps": [{
        "price_detected": 89.0,
        "price_currency": "USD",
        "price_symbol": "$",
        "price_role": "product",
        "page_context": "product",
    }]}
    categories = {finding["category"] for finding in DarkPatternEngine().analyze_step(step, context)}
    assert {"Sneaking", "Hidden Costs", "Urgency"}.issubset(categories)


def test_price_parser_preserves_currency_and_indian_grouping():
    assert AutonomousFlowCrawler._parse_money("Deal price ₹67,500.00") == (67500.0, "INR", "₹")
    assert AutonomousFlowCrawler._parse_money("Total USD 149.99") == (149.99, "USD", "$")


def test_drip_pricing_ignores_unrelated_browse_page_prices():
    context = {"flow_type": "checkout", "steps": [{
        "price_detected": 675.0,
        "price_currency": "INR",
        "price_symbol": "₹",
        "price_role": "product",
        "page_context": "product",
    }]}
    amazon_homepage = {
        "step_number": 4,
        "price_detected": 899.0,
        "price_currency": "INR",
        "price_symbol": "₹",
        "price_role": "product",
        "page_context": "browse",
        "fee_line_items": [],
    }
    findings = DripPricingDetector().analyze_step(amazon_homepage, context)
    assert not any(f.pattern_name == "Late-Stage Checkout Price Inflation" for f in findings)


def test_price_inflation_requires_mandatory_fee_evidence():
    context = {"flow_type": "checkout", "steps": [{
        "price_detected": 675.0,
        "price_currency": "INR",
        "price_symbol": "₹",
        "price_role": "product",
        "page_context": "product",
    }]}
    checkout_without_fees = {
        "step_number": 2,
        "price_detected": 899.0,
        "price_currency": "INR",
        "price_symbol": "₹",
        "price_role": "total",
        "page_context": "checkout",
        "fee_line_items": [],
    }
    findings = DripPricingDetector().analyze_step(checkout_without_fees, context)
    assert not any(f.pattern_name == "Late-Stage Checkout Price Inflation" for f in findings)


def test_safe_checkout_actions_allow_cart_progression_only():
    candidates = [
        {"label": "Buy Now with 1-Click", "href": "/buy-now"},
        {"label": "Add to Cart", "href": ""},
        {"label": "Place your order", "href": "/checkout/submit"},
    ]
    action = AutonomousFlowCrawler._choose_safe_checkout_action(candidates, "product")
    assert action["label"] == "Add to Cart"
    assert action["action_type"] == "add_to_cart"

    assert AutonomousFlowCrawler._choose_safe_checkout_action(
        [{"label": "Authorize Payment", "href": ""}], "checkout"
    ) is None


def test_safe_checkout_actions_open_cart_and_stop_before_payment():
    open_cart = AutonomousFlowCrawler._choose_safe_checkout_action(
        [{"label": "Cart (1)", "href": "https://shop.example/gp/cart/view.html"}],
        "product",
        phase="after_add"
    )
    assert open_cart["action_type"] == "open_cart"

    begin_checkout = AutonomousFlowCrawler._choose_safe_checkout_action(
        [{"label": "Proceed to checkout", "href": "/checkout"}], "cart"
    )
    assert begin_checkout["action_type"] == "begin_checkout"
    assert AutonomousFlowCrawler._choose_safe_checkout_action(
        [{"label": "Place order and pay", "href": "/order"}], "cart"
    ) is None


def test_mock_pages_use_local_stylesheet():
    pages = [
        value for name, value in vars(mock_templates).items()
        if name.endswith("HTML_STEP1") or name.endswith("HTML_STEP2")
        or name.startswith("GYMTRAP_HTML_")
    ]
    assert len(pages) == 8
    assert all('/mock/styles.css' in page for page in pages)
    assert all('cdn.tailwindcss.com' not in page for page in pages)


def test_score_uses_impacts_deduplicates_and_applies_flow_multiplier():
    finding = {
        "category": "Sneaking", "pattern_name": "Preselected", "element_text": "Warranty",
        "step_number": 1, "severity": "High", "score_impact": 20
    }
    result = calculate_manipulation_index([finding, dict(finding)], {"asymmetry_ratio": 3})
    assert result["manipulation_index"] == 23.0
    assert result["total_findings"] == 1
    assert result["duplicates_removed"] == 1


def test_target_validation_blocks_ssrf_but_allows_built_in_mocks():
    validate = AutonomousFlowCrawler._validate_public_target
    assert validate("http://127.0.0.1:8000/mock/shopsneak").endswith("/mock/shopsneak")
    with pytest.raises(ValueError):
        validate("http://127.0.0.1:8000/admin")
    with pytest.raises(ValueError):
        validate("http://10.0.0.1/private")


def test_completed_scan_is_persisted(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "pattern-guard-test.db"))
    db.init_db()
    crawler = AutonomousFlowCrawler()
    result = {
        "site_id": "site_test", "scan_id": "scan_test", "domain": "example.com",
        "site_name": "Example", "flow_type": "general", "duration_ms": 10, "total_steps": 1,
        "score_summary": {
            "manipulation_index": 20.0, "grade": "B", "critical_count": 0,
            "high_count": 1, "medium_count": 0, "low_count": 0, "ftc_risk_level": "Low"
        },
        "steps": [{
            "step_number": 1, "title": "Example", "url": "https://example.com",
            "navigation_intent": "Complete", "raw_screenshot": None, "annotated_screenshot": None,
            "buttons": [], "checkboxes": [], "prices": [], "disclaimers": []
        }],
        "findings": [{
            "id": "finding_test", "step_number": 1, "category": "General",
            "pattern_name": "Test pattern", "severity": "High", "score_impact": 20,
            "plain_explanation": "Test evidence"
        }]
    }
    assert crawler._persist_scan(result, "https://example.com", "Test pattern") == "site_test"
    with sqlite3.connect(db.DB_PATH) as conn:
        assert conn.execute("SELECT COUNT(*) FROM scans").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM findings").fetchone()[0] == 1
