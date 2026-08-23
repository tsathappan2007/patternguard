import os
import sys
import time
import uuid
import json
import asyncio
import re
from typing import List, Dict, Any, Optional, Callable
from playwright.sync_api import sync_playwright
import requests

try:
    from backend.database.db import get_db_connection
    from backend.detectors.engine import DarkPatternEngine
    from backend.evidence.annotator import annotate_screenshot, EVIDENCE_DIR
    from backend.scoring.calculator import calculate_manipulation_index
    from backend.mcp.ai_client import call_ai_inference
except ImportError:
    from database.db import get_db_connection
    from detectors.engine import DarkPatternEngine
    from evidence.annotator import annotate_screenshot, EVIDENCE_DIR
    from scoring.calculator import calculate_manipulation_index
    from mcp.ai_client import call_ai_inference

STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
SCREENSHOTS_DIR = os.path.join(STATIC_DIR, "screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
os.makedirs(EVIDENCE_DIR, exist_ok=True)

class AutonomousFlowCrawler:
    def __init__(self):
        self.engine = DarkPatternEngine()

    async def run_scan(
        self,
        target_url: str,
        site_name: Optional[str] = None,
        flow_type: str = "checkout",
        max_steps: int = 4,
        ai_api_key: Optional[str] = None,
        event_callback: Optional[Callable[[Dict[str, Any]], Any]] = None
    ) -> Dict[str, Any]:
        loop = asyncio.get_running_loop()
        
        def sync_emit(event_type: str, scan_id: str, data: Dict[str, Any]):
            if event_callback:
                payload = {"event": event_type, "scan_id": scan_id, "timestamp": time.time(), **data}
                if asyncio.iscoroutinefunction(event_callback):
                    asyncio.run_coroutine_threadsafe(event_callback(payload), loop)
                else:
                    loop.call_soon_threadsafe(event_callback, payload)

        return await asyncio.to_thread(
            self._execute_scan_sync,
            target_url=target_url,
            site_name=site_name,
            flow_type=flow_type,
            max_steps=max_steps,
            ai_api_key=ai_api_key,
            sync_emit=sync_emit
        )

    def _execute_scan_sync(
        self,
        target_url: str,
        site_name: Optional[str] = None,
        flow_type: str = "checkout",
        max_steps: int = 4,
        ai_api_key: Optional[str] = None,
        sync_emit: Optional[Callable[[str, str, Dict[str, Any]], None]] = None
    ) -> Dict[str, Any]:
        scan_id = f"scan_{uuid.uuid4().hex[:10]}"
        site_id = f"site_{uuid.uuid4().hex[:8]}"

        def emit(event_type: str, data: Dict[str, Any]):
            if sync_emit:
                sync_emit(event_type, scan_id, data)

        if not target_url.startswith("http://") and not target_url.startswith("https://"):
            target_url = "https://" + target_url

        import urllib.parse
        parsed = urllib.parse.urlparse(target_url)
        domain = parsed.netloc or parsed.path.split("/")[0]
        if not site_name:
            site_name = domain.replace("www.", "").capitalize()

        emit("log", {"message": f"Initializing Autonomous Audit Harness for: {domain}"})
        has_ai = bool(ai_api_key and ai_api_key.strip())
        if has_ai:
            emit("log", {"message": "AI Inference Layer: Enabled (Active model resolution engaged)"})
        else:
            emit("log", {"message": "Deterministic Heuristic Engine: Active"})

        # Check Bright Data Scraping Routing
        try:
            from ..scraper.brightdata import BrightDataManager
        except ImportError:
            from scraper.brightdata import BrightDataManager

        brightdata = BrightDataManager()
        use_bd, bd_reason = brightdata.should_use_brightdata(target_url)
        emit("log", {"message": f"[Network Shield]: {bd_reason}"})

        start_time = time.time()
        navigation_nodes = []
        all_findings = []
        flow_context = {"step_history": [], "flow_type": flow_type}

        with sync_playwright() as p:
            browser = None
            if use_bd:
                wss_url = brightdata.get_wss_url()
                if wss_url:
                    emit("log", {"message": "[Bright Data Scraping Browser]: Connecting over CDP (Auto-CAPTCHA & Proxy Active)..."})
                    try:
                        browser = p.chromium.connect_over_cdp(wss_url)
                    except Exception as bd_err:
                        emit("log", {"message": f"[Bright Data Notice]: {str(bd_err)[:80]}. Falling back to local Chromium."})
                        browser = None

            if browser is None:
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        "--no-sandbox",
                        "--disable-setuid-sandbox",
                        "--disable-dev-shm-usage",
                        "--disable-http2",
                        "--disable-blink-features=AutomationControlled",
                        "--ignore-certificate-errors"
                    ]
                )

            context = browser.new_context(
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                locale="en-US",
                extra_http_headers={
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
                }
            )
            page = context.new_page()

            current_url = target_url

            for step_idx in range(1, max_steps + 1):
                emit("log", {"message": f"Step {step_idx}: Navigating to {current_url}..."})
                step_title = f"Step {step_idx}"

                try:
                    page.goto(current_url, wait_until="commit", timeout=8000)
                    time.sleep(1.2)
                    step_title = page.title() or f"Step {step_idx}"
                    emit("log", {"message": f"Step {step_idx} Node Activated: '{step_title}'"})
                except Exception:
                    time.sleep(1.0)
                    step_title = page.title() or f"Step {step_idx}"
                    emit("log", {"message": f"Step {step_idx} Node Ready: '{step_title}'"})

                # Dismiss cookie banners quickly
                try:
                    page.evaluate("""
                        () => {
                            const btns = Array.from(document.querySelectorAll('button, a'));
                            const cookieBtn = btns.find(b => /accept all|accept cookies|agree|i agree/i.test(b.innerText));
                            if (cookieBtn) cookieBtn.click();
                        }
                    """)
                except Exception:
                    pass

                # Capture raw screenshot
                raw_filename = f"raw_{scan_id}_step{step_idx}.png"
                raw_filepath = os.path.join(SCREENSHOTS_DIR, raw_filename)
                raw_rel_url = f"/static/screenshots/{raw_filename}"
                page.screenshot(path=raw_filepath, full_page=False)

                # High-speed single JS evaluation for comprehensive DOM features (<10ms)
                step_data = self._fast_extract_dom(page, step_idx, raw_rel_url)
                flow_context["step_history"].append(step_data)

                emit("step_started", {
                    "step_number": step_idx,
                    "title": step_title,
                    "url": page.url,
                    "screenshot_url": raw_rel_url,
                    "buttons_count": len(step_data.get("buttons", [])),
                    "checkboxes_count": len(step_data.get("checkboxes", [])),
                    "prices": step_data.get("prices", [])
                })

                emit("log", {"message": f"Step {step_idx}: Inspecting DOM choice architecture..."})

                # Run rule detection engine on this step
                step_findings = self.engine.analyze_step(
                    step_data=step_data,
                    flow_context=flow_context,
                    api_key=ai_api_key
                )

                # If AI API key is connected, invoke AI inference
                if has_ai:
                    summary = {
                        "title": step_data.get("title"),
                        "buttons": [b.get("text") for b in step_data.get("buttons", [])[:6]],
                        "checkboxes": [cb.get("label") for cb in step_data.get("checkboxes", []) if cb.get("checked")],
                        "prices": step_data.get("prices", [])[:4],
                        "text": step_data.get("page_text", "")[:350]
                    }
                    def emit_log(msg: str):
                        emit("log", {"message": msg})
                    ai_findings = call_ai_inference(ai_api_key, summary, emit_log=emit_log)
                    for af in ai_findings:
                        af["id"] = f"find_{uuid.uuid4().hex[:8]}"
                        step_findings.append(af)

                for sf in step_findings:
                    sf["step_number"] = step_idx
                    sf["screenshot_path"] = raw_rel_url
                    all_findings.append(sf)
                    emit("finding_detected", sf)

                # Generate annotated visual evidence if findings exist
                annotated_rel_url = None
                if step_findings:
                    annotated_filename = f"annotated_{scan_id}_step{step_idx}.png"
                    annotated_rel_url = f"/static/evidence/{annotated_filename}"

                    try:
                        annotate_screenshot(
                            image_path=raw_filepath,
                            findings=step_findings,
                            output_filename=annotated_filename
                        )
                    except Exception as ann_err:
                        pass
                    
                    for sf in step_findings:
                        sf["annotated_path"] = annotated_rel_url

                # Determine next transition URL and reason
                next_url = None
                nav_action_reason = "Final Step in Funnel Reached"
                if step_idx < max_steps:
                    next_url, nav_action_reason = self._find_next_url_with_intent(page, flow_type)

                # Build rich navigation node structure
                node_structure = {
                    "step_number": step_idx,
                    "url": page.url,
                    "title": step_title,
                    "raw_screenshot": raw_rel_url,
                    "annotated_screenshot": annotated_rel_url or raw_rel_url,
                    "findings_count": len(step_findings),
                    "findings": step_findings,
                    "buttons": step_data.get("buttons", []),
                    "checkboxes": step_data.get("checkboxes", []),
                    "prices": step_data.get("prices", []),
                    "disclaimers": step_data.get("disclaimers", []),
                    "next_navigation_target": next_url,
                    "navigation_intent": nav_action_reason
                }
                navigation_nodes.append(node_structure)

                emit("step_completed", {
                    "step_number": step_idx,
                    "annotated_screenshot": annotated_rel_url or raw_rel_url,
                    "findings_count": len(step_findings),
                    "node_data": node_structure
                })

                if next_url and next_url != current_url and next_url != page.url:
                    current_url = next_url
                else:
                    break

            browser.close()

        duration_ms = int((time.time() - start_time) * 1000)
        score_summary = calculate_manipulation_index(all_findings)
        primary_pattern = all_findings[0]["pattern_name"] if all_findings else "Clean Flow"

        emit("log", {
            "message": f"Audit complete in {duration_ms}ms! Navigation Nodes: {len(navigation_nodes)} · Score: {score_summary['manipulation_index']}/100 [GRADE {score_summary['grade']}]"
        })

        final_result = {
            "site_id": site_id,
            "scan_id": scan_id,
            "domain": domain,
            "site_name": site_name,
            "flow_type": flow_type,
            "duration_ms": duration_ms,
            "total_steps": len(navigation_nodes),
            "score_summary": score_summary,
            "findings": all_findings,
            "steps": navigation_nodes,
            "navigation_nodes": navigation_nodes
        }

        emit("scan_completed", final_result)
        return final_result

    def _fast_extract_dom(self, page, step_idx: int, screenshot_path: str) -> Dict[str, Any]:
        """Extracts deep DOM structure, checkboxes, buttons, disclaimers, and price elements."""
        try:
            dom_data = page.evaluate("""
                () => {
                    const checkboxes = Array.from(document.querySelectorAll('input[type="checkbox"]')).map(cb => {
                        const rect = cb.getBoundingClientRect();
                        const label = cb.closest('label')?.innerText || document.querySelector(`label[for="${cb.id}"]`)?.innerText || cb.parentElement?.innerText || '';
                        return {
                            name: cb.name || cb.id || '',
                            id: cb.id || '',
                            checked: cb.checked,
                            label: label.trim().slice(0, 120),
                            bounding_box: rect.width > 0 ? [rect.x, rect.y, rect.width, rect.height] : null
                        };
                    });

                    const buttons = Array.from(document.querySelectorAll('button, input[type="submit"], [role="button"], a[href], a')).slice(0, 20).map(b => {
                        const rect = b.getBoundingClientRect();
                        return {
                            text: (b.innerText || b.value || b.getAttribute('aria-label') || '').trim().slice(0, 80),
                            classes: b.className || '',
                            tag: b.tagName.toLowerCase(),
                            href: b.href || '',
                            bounding_box: rect.width > 0 ? [rect.x, rect.y, rect.width, rect.height] : null
                        };
                    }).filter(b => b.text.length > 0);

                    const disclaimers = Array.from(document.querySelectorAll('small, p.disclaimer, span.terms, div.fine-print, [class*="fineprint"], [class*="subtext"], [class*="renewal"], [class*="terms"]')).slice(0, 8).map(d => {
                        return {
                            text: (d.innerText || '').trim().slice(0, 140),
                            tag: d.tagName.toLowerCase(),
                            fontSize: window.getComputedStyle(d).fontSize || '11px',
                            color: window.getComputedStyle(d).color || '#888'
                        };
                    }).filter(d => d.text.length > 8);

                    const pageText = document.body ? document.body.innerText.slice(0, 4000) : '';
                    
                    return {
                        checkboxes,
                        buttons,
                        disclaimers,
                        pageText
                    };
                }
            """)
        except Exception:
            dom_data = {"checkboxes": [], "buttons": [], "disclaimers": [], "pageText": ""}

        page_text = dom_data.get("pageText", "")
        price_matches = re.findall(r"\$\s?([0-9]+\.[0-9]{2})|([0-9]+\.[0-9]{2})\s?USD|₹\s?([0-9]+(?:\.[0-9]{2})?)", page_text)
        prices = []
        for m in price_matches[:8]:
            val = next((item for item in m if item), None)
            if val:
                try:
                    prices.append(float(val.replace(",", "")))
                except Exception:
                    pass

        return {
            "step": step_idx,
            "url": page.url,
            "title": page.title() or "",
            "page_text": page_text,
            "checkboxes": dom_data.get("checkboxes", []),
            "buttons": dom_data.get("buttons", []),
            "disclaimers": dom_data.get("disclaimers", []),
            "prices": prices,
            "screenshot_path": screenshot_path
        }

    def _find_next_url_with_intent(self, page, flow_type: str) -> (Optional[str], str):
        """Finds next step URL and returns the strategic navigation intent."""
        try:
            next_href = page.evaluate("""
                () => {
                    const links = Array.from(document.querySelectorAll('a[href]'));
                    
                    // 1. Cancellation funnel matches
                    const cancelRegex = /continue to cancel|proceed to cancel|cancel subscription|confirm cancellation|still want to cancel|keep membership|cancel/i;
                    const cancelBtn = links.find(l => cancelRegex.test(l.innerText || l.href));
                    if (cancelBtn && cancelBtn.href && cancelBtn.href !== window.location.href) {
                        return cancelBtn.href;
                    }

                    // 2. Progression matches (checkout, trial, start, continue, dashboard, order)
                    const priorityRegex = /proceed|checkout|buy now|start|free trial|get access|continue|view cart|order now|dashboard|sign up|join|plan/i;
                    const nextBtn = links.find(l => priorityRegex.test(l.innerText || l.getAttribute('aria-label') || l.href));
                    if (nextBtn && nextBtn.href && nextBtn.href !== window.location.href) {
                        return nextBtn.href;
                    }

                    // 3. Fallback: first internal valid link
                    const anyLink = links.find(l => l.href && !l.href.includes('#') && l.href !== window.location.href);
                    if (anyLink && anyLink.href) return anyLink.href;

                    return null;
                }
            """)
            if next_href:
                intent = "Traversing Cancellation Obstacle Maze" if "cancel" in (flow_type + next_href).lower() else "Progressing Funnel Walkthrough"
                return next_href, intent
        except Exception:
            pass
        return None, "Completed Funnel Walkthrough"
