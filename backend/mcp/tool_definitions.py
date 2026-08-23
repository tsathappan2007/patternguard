import json
from typing import List, Dict, Any

MCP_TOOL_DEFINITIONS = [
    {
        "name": "navigate_to",
        "description": "Navigates the live browser to a specified URL.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "The destination URL to navigate to."}
            },
            "required": ["url"]
        }
    },
    {
        "name": "click_element",
        "description": "Clicks an interactive element (button, link, tab) on the current page to progress the funnel.",
        "parameters": {
            "type": "object",
            "properties": {
                "selector_or_text": {"type": "string", "description": "CSS selector or visible text of the element to click (e.g. 'button:has-text(\"Checkout\")' or 'a.cancel-link')."},
                "intent": {"type": "string", "description": "The strategic reason for clicking this element."}
            },
            "required": ["selector_or_text"]
        }
    },
    {
        "name": "interact_checkbox",
        "description": "Inspects and optionally unchecks or checks a checkbox to test default bias or add-on sneaking.",
        "parameters": {
            "type": "object",
            "properties": {
                "selector": {"type": "string", "description": "CSS selector of the checkbox input."},
                "action": {"type": "string", "enum": ["check", "uncheck", "inspect"], "description": "Action to perform on checkbox."}
            },
            "required": ["selector", "action"]
        }
    },
    {
        "name": "flag_dark_pattern",
        "description": "Prosecutes a deceptive dark pattern identified on the current page with statutory legal grounding.",
        "parameters": {
            "type": "object",
            "properties": {
                "pattern_name": {"type": "string", "description": "Name of the dark pattern (e.g. 'Sneak into Basket', 'Confirmshaming', 'Drip Pricing', 'Fake Countdown Timer', 'Roach Motel')."},
                "severity": {"type": "string", "enum": ["Critical", "High", "Medium", "Low"], "description": "Severity classification."},
                "dom_selector": {"type": "string", "description": "Exact CSS selector of the offending element."},
                "element_text": {"type": "string", "description": "The exact misleading text or copy."},
                "plain_explanation": {"type": "string", "description": "Clear plain English explanation of why this is deceptive."},
                "psychological_mechanism": {"type": "string", "description": "Underlying cognitive bias being exploited (e.g. Loss Aversion, Default Effect, Sunk Cost Fallacy)."},
                "score_impact": {"type": "number", "description": "Score penalty to add to Manipulation Index (10 to 30 points)."}
            },
            "required": ["pattern_name", "severity", "plain_explanation"]
        }
    },
    {
        "name": "finish_audit",
        "description": "Terminates the audit session once all steps in the funnel have been investigated.",
        "parameters": {
            "type": "object",
            "properties": {
                "executive_summary": {"type": "string", "description": "Final regulatory summary of findings."}
            },
            "required": ["executive_summary"]
        }
    }
]

