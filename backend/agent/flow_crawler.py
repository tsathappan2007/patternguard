import os
import time
import uuid
import json
import asyncio
import re
import ipaddress
import socket
import threading
import urllib.parse
from typing import List, Dict, Any, Optional, Callable
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

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

STATIC_DIR = os.getenv(
    "PATTERN_GUARD_STATIC_DIR",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
)
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
        ai_endpoint: Optional[str] = None,
        ai_model: Optional[str] = None,
        bright_data_wss_url: Optional[str] = None,
        event_callback: Optional[Callable[[Dict[str, Any]], Any]] = None,
        cancel_event: Optional[threading.Event] = None
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
            ai_endpoint=ai_endpoint,
            ai_model=ai_model,
            bright_data_wss_url=bright_data_wss_url,
            cancel_event=cancel_event,
            sync_emit=sync_emit
        )

    def _execute_scan_sync(
        self,
        target_url: str,
        site_name: Optional[str] = None,
        flow_type: str = "checkout",
        max_steps: int = 4,
        ai_api_key: Optional[str] = None,
        ai_endpoint: Optional[str] = None,
        ai_model: Optional[str] = None,
        bright_data_wss_url: Optional[str] = None,
        cancel_event: Optional[threading.Event] = None,
        sync_emit: Optional[Callable[[str, str, Dict[str, Any]], None]] = None
    ) -> Dict[str, Any]:
        scan_id = f"scan_{uuid.uuid4().hex[:10]}"
        site_id = f"site_{uuid.uuid4().hex[:8]}"

        def emit(event_type: str, data: Dict[str, Any]):
            if sync_emit:
                sync_emit(event_type, scan_id, data)

        if not target_url.startswith("http://") and not target_url.startswith("https://"):
            target_url = "https://" + target_url

        target_url = self._validate_public_target(target_url)
        parsed = urllib.parse.urlparse(target_url)
        domain = parsed.netloc or parsed.path.split("/")[0]
        if not site_name:
            site_name = domain.replace("www.", "").capitalize()

        emit("log", {"message": f"Initializing Autonomous Audit Harness for: {domain}"})
        active_ai_key = (ai_api_key or os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("GROK_API_KEY") or "").strip()
        has_ai = bool(active_ai_key or ai_endpoint)
        if has_ai:
            emit("log", {"message": "AI Inference Layer: Enabled (Active model resolution engaged)"})
        else:
            emit("log", {"message": "Deterministic Heuristic Engine: Active"})

        # Check Bright Data Scraping Routing
        try:
            from ..scraper.brightdata import BrightDataManager
        except ImportError:
            from scraper.brightdata import BrightDataManager

        brightdata = BrightDataManager(wss_url=bright_data_wss_url)
        use_bd, bd_reason = brightdata.should_use_brightdata(target_url)
        emit("log", {"message": f"[Network Shield]: {bd_reason}"})

        start_time = time.time()
        navigation_nodes = []
        all_findings = []
        flow_context = {"steps": [], "flow_type": flow_type, "signup_step_count": 1}
        visited_states = set()
        performed_actions = set()

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

            def guard_navigation(route):
                if route.request.is_navigation_request():
                    try:
                        self._validate_public_target(route.request.url)
                    except ValueError:
                        emit("log", {"message": f"Blocked unsafe navigation target: {route.request.url[:140]}"})
                        route.abort()
                        return
                route.continue_()

            context.route("**/*", guard_navigation)
            page = context.new_page()

            current_url = target_url
            page_is_ready = False

            for step_idx in range(1, max_steps + 1):
                if cancel_event and cancel_event.is_set():
                    emit("log", {"message": "Audit cancelled because the client disconnected."})
                    break
                step_title = f"Step {step_idx}"

                try:
                    if not page_is_ready:
                        emit("log", {"message": f"Step {step_idx}: Navigating to {current_url}..."})
                        page.goto(current_url, wait_until="domcontentloaded", timeout=25000)
                    try:
                        page.wait_for_load_state("networkidle", timeout=5000)
                    except Exception:
                        pass
                    try:
                        page.evaluate("document.fonts && document.fonts.ready")
                    except Exception:
                        pass
                    time.sleep(0.2)
                    step_title = page.title() or f"Step {step_idx}"
                    emit("log", {"message": f"Step {step_idx} Node Activated: '{step_title}'"})
                except PlaywrightTimeoutError as nav_error:
                    # Large commerce pages can leave analytics or ad resources
                    # pending even after their useful DOM has rendered. Preserve
                    # that page instead of discarding a valid inspection target.
                    try:
                        page.evaluate("window.stop()")
                        body_text = page.locator("body").inner_text(timeout=3000).strip()
                    except Exception:
                        body_text = ""
                    if len(body_text) >= 200 and page.url.startswith(("http://", "https://")):
                        step_title = page.title() or f"Step {step_idx}"
                        emit("log", {
                            "message": (
                                f"Step {step_idx}: Load timeout reached, but a usable DOM was recovered "
                                f"at {page.url}. Continuing inspection."
                            )
                        })
                        emit("log", {"message": f"Step {step_idx} Node Activated: '{step_title}'"})
                    else:
                        emit("log", {"message": f"Step {step_idx} navigation failed: {str(nav_error)[:160]}"})
                        if step_idx == 1:
                            raise RuntimeError(
                                "Unable to load target URL: the page timed out before a usable DOM was available. "
                                "Configure a valid Bright Data Scraping Browser WSS URL if the site blocks local automation."
                            ) from nav_error
                        break
                except Exception as nav_error:
                    emit("log", {"message": f"Step {step_idx} navigation failed: {str(nav_error)[:160]}"})
                    if step_idx == 1:
                        raise RuntimeError(f"Unable to load target URL: {nav_error}") from nav_error
                    break
                finally:
                    page_is_ready = False

                # Capture raw screenshot
                raw_filename = f"raw_{scan_id}_step{step_idx}.png"
                raw_filepath = os.path.join(SCREENSHOTS_DIR, raw_filename)
                raw_rel_url = f"/static/screenshots/{raw_filename}"
                page.screenshot(path=raw_filepath, full_page=False)

                # High-speed single JS evaluation for comprehensive DOM features (<10ms)
                step_data = self._fast_extract_dom(page, step_idx, raw_rel_url)
                state_key = (page.url.rstrip("/"), step_data.get("page_context", "unknown"))
                if state_key in visited_states:
                    emit("log", {"message": f"Navigation loop prevented at {page.url}"})
                    break
                visited_states.add(state_key)
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

                # Do not prosecute pages reached after the crawler has left the
                # requested checkout funnel (for example, sign-in or home pages).
                outside_requested_flow = (
                    step_idx > 1
                    and flow_type == "checkout"
                    and step_data.get("page_context") not in {"product", "cart", "checkout"}
                )
                if outside_requested_flow:
                    emit("log", {
                        "message": (
                            f"Step {step_idx}: {step_data.get('page_context', 'unknown').title()} boundary "
                            "is outside the verified checkout funnel; suppressing detector output."
                        )
                    })
                    step_findings = []
                else:
                    step_findings = self.engine.analyze_step(
                        step_data=step_data,
                        flow_context=flow_context,
                        api_key=None
                    )

                # If AI API key is connected, invoke AI inference
                if has_ai and not outside_requested_flow:
                    summary = {
                        "title": step_data.get("title"),
                        "buttons": [b.get("text") for b in step_data.get("buttons", [])[:6]],
                        "checkboxes": [cb.get("label") for cb in step_data.get("checkboxes", []) if cb.get("checked")],
                        "prices": step_data.get("prices", [])[:4],
                        "text": step_data.get("page_text", "")[:350]
                    }
                    def emit_log(msg: str):
                        emit("log", {"message": msg})
                    ai_findings = call_ai_inference(
                        active_ai_key,
                        summary,
                        emit_log=emit_log,
                        endpoint_override=ai_endpoint,
                        model_override=ai_model
                    )
                    for af in ai_findings:
                        af["id"] = f"find_{uuid.uuid4().hex[:8]}"
                        step_findings.append(af)

                for sf in step_findings:
                    sf["step_number"] = step_idx
                    sf["screenshot_path"] = raw_rel_url
                    all_findings.append(sf)
                    emit("finding_detected", sf)

                flow_context["steps"].append(step_data)

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
                navigation_action = None
                transition = {"continue": False, "page_ready": False}
                if step_idx < max_steps:
                    transition = self._advance_flow_safely(
                        page,
                        flow_type,
                        step_data.get("page_context", "unknown"),
                        performed_actions,
                        emit
                    )
                    next_url = transition.get("next_url")
                    nav_action_reason = transition.get("reason", "Completed Funnel Walkthrough")
                    navigation_action = transition.get("action_type")

                # Build rich navigation node structure
                node_structure = {
                    "step_number": step_idx,
                    "url": step_data.get("url", page.url),
                    "title": step_data.get("title") or step_title,
                    "raw_screenshot": raw_rel_url,
                    "annotated_screenshot": annotated_rel_url or raw_rel_url,
                    "findings_count": len(step_findings),
                    "findings": step_findings,
                    "buttons": step_data.get("buttons", []),
                    "checkboxes": step_data.get("checkboxes", []),
                    "prices": step_data.get("prices", []),
                    "price_detected": step_data.get("price_detected"),
                    "price_currency": step_data.get("price_currency"),
                    "price_symbol": step_data.get("price_symbol"),
                    "price_role": step_data.get("price_role"),
                    "price_selector": step_data.get("price_selector"),
                    "price_bounding_box": step_data.get("price_bounding_box"),
                    "page_context": step_data.get("page_context", "unknown"),
                    "disclaimers": step_data.get("disclaimers", []),
                    "next_navigation_target": next_url,
                    "navigation_intent": nav_action_reason,
                    "navigation_action": navigation_action
                }
                navigation_nodes.append(node_structure)

                emit("step_completed", {
                    "step_number": step_idx,
                    "annotated_screenshot": annotated_rel_url or raw_rel_url,
                    "findings_count": len(step_findings),
                    "node_data": node_structure
                })

                if not transition.get("continue") or not next_url:
                    break
                current_url = self._validate_public_target(next_url)
                page_is_ready = bool(transition.get("page_ready"))

            browser.close()

        duration_ms = int((time.time() - start_time) * 1000)
        all_findings = self._deduplicate_findings(all_findings)
        if flow_type == "cancellation":
            flow_context["asymmetry_ratio"] = max(1.0, len(navigation_nodes) / max(1, flow_context["signup_step_count"]))
        score_summary = calculate_manipulation_index(all_findings, flow_context)
        severity_rank = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}
        primary_finding = max(
            all_findings,
            key=lambda f: (severity_rank.get(f.get("severity"), 0), float(f.get("score_impact", 0))),
            default=None
        )
        primary_pattern = primary_finding["pattern_name"] if primary_finding else "Clean Flow"

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

        try:
            persisted_site_id = self._persist_scan(final_result, target_url, primary_pattern)
            final_result["site_id"] = persisted_site_id
            final_result["persisted"] = True
        except Exception as db_error:
            final_result["persisted"] = False
            final_result["persistence_error"] = str(db_error)
            emit("log", {"message": f"Audit completed, but database persistence failed: {str(db_error)[:140]}"})

        emit("scan_completed", final_result)
        return final_result

    @staticmethod
    def _deduplicate_findings(findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        unique = []
        seen = set()
        for finding in findings:
            key = (
                str(finding.get("category", "")).lower().strip(),
                str(finding.get("pattern_name", "")).lower().strip(),
                str(finding.get("element_text", "")).lower().strip()[:160],
                finding.get("step_number"),
            )
            if key not in seen:
                seen.add(key)
                unique.append(finding)
        return unique

    @staticmethod
    def _validate_public_target(target_url: str) -> str:
        parsed = urllib.parse.urlparse(target_url)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise ValueError("Target URL must be a valid HTTP or HTTPS URL")
        if parsed.username or parsed.password:
            raise ValueError("Credentials are not allowed in target URLs")

        host = parsed.hostname.lower()
        local_hosts = {"localhost", "127.0.0.1", "::1"}
        if host in local_hosts:
            if not parsed.path.startswith("/mock/") and parsed.path != "/mock":
                raise ValueError("Local targets are restricted to Pattern Guard's /mock routes")
            return target_url

        try:
            addresses = {item[4][0] for item in socket.getaddrinfo(host, parsed.port or 443, type=socket.SOCK_STREAM)}
        except socket.gaierror as error:
            raise ValueError(f"Target hostname could not be resolved: {host}") from error
        for address in addresses:
            ip = ipaddress.ip_address(address)
            if not ip.is_global:
                raise ValueError("Private, loopback, link-local, and reserved network targets are not allowed")
        return target_url

    def _persist_scan(self, result: Dict[str, Any], target_url: str, primary_pattern: str) -> str:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, scans_count FROM sites WHERE domain = ?", (result["domain"],))
            existing = cursor.fetchone()
            site_id = existing["id"] if existing else result["site_id"]
            score = result["score_summary"]
            top_violation = primary_pattern if result["findings"] else "None detected"

            if existing:
                cursor.execute("""
                    UPDATE sites SET name = ?, category = ?, manipulation_index = ?, grade = ?,
                        scans_count = ?, critical_count = ?, high_count = ?, medium_count = ?, low_count = ?,
                        top_violation = ?, primary_pattern = ?, ftc_risk_level = ?, last_scanned_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (
                    result["site_name"], result["flow_type"], score["manipulation_index"], score["grade"],
                    existing["scans_count"] + 1, score["critical_count"], score["high_count"],
                    score["medium_count"], score["low_count"], top_violation, primary_pattern,
                    score["ftc_risk_level"], site_id
                ))
            else:
                cursor.execute("""
                    INSERT INTO sites (
                        id, domain, name, category, manipulation_index, grade, status, scans_count,
                        critical_count, high_count, medium_count, low_count, top_violation,
                        primary_pattern, ftc_risk_level
                    ) VALUES (?, ?, ?, ?, ?, ?, 'audited', 1, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    site_id, result["domain"], result["site_name"], result["flow_type"],
                    score["manipulation_index"], score["grade"], score["critical_count"],
                    score["high_count"], score["medium_count"], score["low_count"],
                    top_violation, primary_pattern, score["ftc_risk_level"]
                ))

            cursor.execute("""
                INSERT INTO scans (
                    id, site_id, target_url, flow_type, status, manipulation_index, grade,
                    total_steps, findings_count, duration_ms
                ) VALUES (?, ?, ?, ?, 'completed', ?, ?, ?, ?, ?)
            """, (
                result["scan_id"], site_id, target_url, result["flow_type"], score["manipulation_index"],
                score["grade"], result["total_steps"], len(result["findings"]), result["duration_ms"]
            ))

            step_ids = {}
            for step in result["steps"]:
                step_id = f"step_{result['scan_id']}_{step['step_number']}"
                step_ids[step["step_number"]] = step_id
                cursor.execute("""
                    INSERT INTO flow_steps (
                        id, scan_id, step_number, step_name, url, action_type, screenshot_path,
                        annotated_screenshot_path, dom_snapshot, price_detected, raw_metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    step_id, result["scan_id"], step["step_number"], step["title"], step["url"],
                    step.get("navigation_intent"), step.get("raw_screenshot"), step.get("annotated_screenshot"),
                    json.dumps({"buttons": step.get("buttons", []), "checkboxes": step.get("checkboxes", [])}),
                    step.get("price_detected"), json.dumps({
                        "disclaimers": step.get("disclaimers", []),
                        "page_context": step.get("page_context"),
                        "price_currency": step.get("price_currency"),
                        "price_symbol": step.get("price_symbol"),
                        "price_role": step.get("price_role"),
                        "price_selector": step.get("price_selector"),
                        "navigation_action": step.get("navigation_action")
                    })
                ))

            for finding in result["findings"]:
                cursor.execute("""
                    INSERT INTO findings (
                        id, scan_id, step_id, site_id, category, pattern_name, severity, score_impact,
                        dom_selector, dom_snippet, element_text, bounding_box, screenshot_path,
                        annotated_path, plain_explanation, psychological_mechanism, regulatory_citation,
                        regulatory_statute, remedy_recommendation
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    finding["id"], result["scan_id"], step_ids.get(finding.get("step_number")), site_id,
                    finding.get("category", "General"), finding.get("pattern_name", "Unknown Pattern"),
                    finding.get("severity", "Medium"), float(finding.get("score_impact", 0)),
                    finding.get("dom_selector"), finding.get("dom_snippet"), finding.get("element_text"),
                    json.dumps(finding.get("bounding_box")) if finding.get("bounding_box") else None,
                    finding.get("screenshot_path"), finding.get("annotated_path"),
                    finding.get("plain_explanation", "No explanation provided"),
                    finding.get("psychological_mechanism"), finding.get("regulatory_citation"),
                    finding.get("regulatory_statute"), finding.get("remedy_recommendation")
                ))
            conn.commit()
            return site_id
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _fast_extract_dom(self, page, step_idx: int, screenshot_path: str) -> Dict[str, Any]:
        """Extracts deep DOM structure, checkboxes, buttons, disclaimers, and price elements."""
        try:
            dom_data = page.evaluate(r"""
                () => {
                    const box = el => {
                        const r = el.getBoundingClientRect();
                        return r.width > 0 && r.height > 0
                            ? {x: r.x, y: r.y, width: r.width, height: r.height}
                            : null;
                    };
                    const selector = el => {
                        if (el.id) return `#${CSS.escape(el.id)}`;
                        if (el.name) return `${el.tagName.toLowerCase()}[name="${CSS.escape(el.name)}"]`;
                        const cls = typeof el.className === 'string' ? el.className.trim().split(/\s+/).filter(Boolean).slice(0, 2) : [];
                        return el.tagName.toLowerCase() + cls.map(c => `.${CSS.escape(c)}`).join('');
                    };
                    const metadata = el => {
                        const style = window.getComputedStyle(el);
                        const label = el.closest('label')?.innerText || (el.id ? document.querySelector(`label[for="${CSS.escape(el.id)}"]`)?.innerText : '') || el.parentElement?.innerText || '';
                        return {
                            tag: el.tagName.toLowerCase(),
                            type: (el.type || '').toLowerCase(),
                            name: el.name || el.id || '',
                            id: el.id || '',
                            checked: Boolean(el.checked),
                            text: (el.innerText || el.value || el.getAttribute('aria-label') || label || '').trim().slice(0, 240),
                            label: label.trim().slice(0, 240),
                            href: el.href || '',
                            classes: typeof el.className === 'string' ? el.className : '',
                            selector: selector(el),
                            html: el.outerHTML.slice(0, 500),
                            color: style.color,
                            background_color: style.backgroundColor,
                            font_size_px: parseFloat(style.fontSize) || 14,
                            bounding_box: box(el)
                        };
                    };

                    const interactiveElements = Array.from(document.querySelectorAll(
                        'input[type="checkbox"], input[type="radio"], button, input[type="submit"], [role="button"], a[href]'
                    )).slice(0, 80).map(metadata);
                    const checkboxes = interactiveElements.filter(e => e.tag === 'input' && ['checkbox', 'radio'].includes(e.type));
                    const buttons = interactiveElements.filter(e => ['button', 'a'].includes(e.tag) || e.type === 'submit').slice(0, 30);

                    const disclosureNodes = Array.from(document.querySelectorAll(
                        'small, p.disclaimer, span.terms, div.fine-print, [class*="fineprint"], [class*="fine-print"], [class*="subtext"], [class*="renewal"], [class*="terms"]'
                    )).slice(0, 20);
                    const disclosureElements = disclosureNodes.map(metadata).filter(e => e.text.length > 8);
                    const disclaimers = disclosureElements.map(e => ({
                        text: e.text, tag: e.tag, fontSize: `${e.font_size_px}px`, color: e.color,
                        backgroundColor: e.background_color, selector: e.selector, bounding_box: e.bounding_box
                    }));

                    const allTextNodes = Array.from(document.querySelectorAll('div, li, p, span, td')).filter(el => el.children.length <= 3);
                    const feeRegex = /(service|convenience|platform|processing|handling|resort|facility|admin|regulatory|security|booking)\s+(fee|charge|surcharge)/i;
                    const moneyRegex = /(?:([$€£₹])|(USD|EUR|GBP|INR)\s*)([0-9][\d,]*(?:\.\d{1,2})?)/i;
                    const feeLineItems = allTextNodes.filter(el => {
                        const matches = feeRegex.test(el.innerText || '') && moneyRegex.test(el.innerText || '');
                        const matchingChild = Array.from(el.children).some(child => feeRegex.test(child.innerText || '') && moneyRegex.test(child.innerText || ''));
                        return matches && !matchingChild;
                    }).slice(0, 12).map(el => {
                        const item = metadata(el);
                        const amount = (el.innerText || '').match(moneyRegex);
                        const currencyMap = {'$': 'USD', '€': 'EUR', '£': 'GBP', '₹': 'INR'};
                        const currency = amount ? (amount[2] || currencyMap[amount[1]] || '').toUpperCase() : '';
                        return {
                            ...item,
                            name: item.text,
                            amount: amount ? Number(amount[3].replace(/,/g, '')) : 0,
                            currency,
                            currency_symbol: amount ? (amount[1] || {USD: '$', EUR: '€', GBP: '£', INR: '₹'}[currency] || '') : '',
                            is_mandatory: true
                        };
                    });

                    const pageText = document.body ? document.body.innerText.slice(0, 12000) : '';
                    const contextText = `${window.location.pathname} ${document.title} ${pageText.slice(0, 3000)}`;
                    const hasPasswordField = Boolean(document.querySelector('input[type="password"]'));
                    const authLocation = `${window.location.pathname} ${document.title}`;
                    const isAuth = hasPasswordField || /(?:\/ap\/signin|\/signin|\/login|\/register|amazon sign-in)/i.test(authLocation);
                    const strongProductSignal = /(?:\/dp\/|\/gp\/product\/)/i.test(window.location.pathname)
                        || Boolean(document.querySelector('[itemprop="product"], #buy-now-button, #add-to-cart-button'));
                    const isProduct = strongProductSignal
                        || /(?:product details?|buy now|add to cart|proceed(?: to)? .*checkout)/i.test(contextText);
                    const checkoutPath = /\/checkout(?:\/|\?|$)/i.test(window.location.pathname);
                    const cartPath = /\/(?:cart|basket)(?:\/|\?|$)/i.test(window.location.pathname);
                    const isCheckout = checkoutPath || (!strongProductSignal && (
                        Boolean(document.querySelector('[class*="order-total"], [class*="grand-total"], [class*="checkout-total"]'))
                        || /(?:order summary|review your order|place your order|payment method)/i.test(contextText)
                    ));
                    const isCart = cartPath || (!strongProductSignal && (
                        Boolean(document.querySelector('[class*="basket"], [id*="basket"], [class*="cart-total"], [id*="cart-total"]'))
                        || /(?:shopping cart|your basket)/i.test(contextText)
                    ));
                    const isCancellation = /(?:\/cancel|cancellation|terminate (?:plan|subscription)|end membership)/i.test(contextText);
                    const pageContext = isAuth ? 'auth' : isCheckout ? 'checkout' : isCart ? 'cart' : isProduct ? 'product' : isCancellation ? 'cancellation' : 'browse';

                    const currencyRegex = /(?:[$€£₹]|USD|EUR|GBP|INR)\s*\d[\d,]*(?:\.\d{1,2})?/i;
                    const totalRegex = /(?:grand\s*total|order\s*total|total\s*(?:due|payable|amount|price)|amount\s*(?:due|payable)|pay\s*now)/i;
                    const priceNodes = Array.from(document.querySelectorAll(
                        '[itemprop="price"], [data-testid*="price" i], [data-testid*="total" i], [id*="price" i], [id*="total" i], [class*="price" i], [class*="total" i]'
                    )).filter(el => box(el) && currencyRegex.test(el.innerText || el.textContent || el.getAttribute('content') || ''));
                    const semanticTotalNodes = allTextNodes.filter(el => {
                        const text = el.innerText || '';
                        return box(el) && totalRegex.test(text) && currencyRegex.test(text)
                            && !Array.from(el.children).some(child => totalRegex.test(child.innerText || '') && currencyRegex.test(child.innerText || ''));
                    });
                    const seenPriceNodes = new Set();
                    const priceCandidates = [...semanticTotalNodes, ...priceNodes].filter(el => {
                        if (seenPriceNodes.has(el)) return false;
                        seenPriceNodes.add(el);
                        return true;
                    }).slice(0, 20).map(el => {
                        const item = metadata(el);
                        const text = el.innerText || el.textContent || el.getAttribute('content') || '';
                        return {...item, text: text.trim().slice(0, 300), price_role: totalRegex.test(text) ? 'total' : 'product'};
                    });
                    const bannerElements = Array.from(document.querySelectorAll('[class*="urgency"], [class*="scarcity"], [class*="countdown"], [class*="timer"], [class*="alert"], [role="alert"]')).slice(0, 20).map(metadata);
                    const timerElement = Array.from(document.querySelectorAll('[class*="countdown"], [class*="timer"], [data-countdown]')).find(el => /\d{1,2}:\d{2}/.test(el.innerText || ''));
                    const scriptText = Array.from(document.scripts).map(s => s.textContent || '').join('\n');
                    const timerDetected = timerElement ? {
                        display_time: ((timerElement.innerText || '').match(/\d{1,2}:\d{2}/) || [''])[0],
                        resets_on_reload: /(?:let|var|const)\s+\w*(?:time|seconds|countdown)\w*\s*=\s*\d+/i.test(scriptText),
                        selector: selector(timerElement), html: timerElement.outerHTML.slice(0, 500), bounding_box: box(timerElement)
                    } : null;

                    const cancellationBarrierElement = allTextNodes.find(el =>
                        /cancel/i.test(el.innerText || '') && /(call|phone|email|contact support|support ticket)/i.test(el.innerText || '')
                    );
                    return {
                        checkboxes,
                        buttons,
                        disclaimers,
                        interactiveElements,
                        disclosureElements,
                        feeLineItems,
                        bannerElements,
                        timerDetected,
                        cancellationBarrier: cancellationBarrierElement ? metadata(cancellationBarrierElement) : null,
                        pageContext,
                        priceCandidates,
                        pageText,
                        domHtml: document.documentElement.outerHTML.slice(0, 20000)
                    };
                }
            """)
        except Exception:
            dom_data = {
                "checkboxes": [], "buttons": [], "disclaimers": [], "interactiveElements": [],
                "disclosureElements": [], "feeLineItems": [], "bannerElements": [], "priceCandidates": [],
                "pageContext": "browse", "pageText": "", "domHtml": ""
            }

        page_text = dom_data.get("pageText", "")
        page_context = dom_data.get("pageContext", "browse")
        candidates = dom_data.get("priceCandidates", [])
        if page_context in {"cart", "checkout"}:
            candidates = [candidate for candidate in candidates if candidate.get("price_role") == "total"]
        elif page_context == "product":
            product_candidates = [candidate for candidate in candidates if candidate.get("price_role") == "product"]
            candidates = product_candidates or candidates
        else:
            candidates = []

        prices = []
        selected_price = None
        selected_candidate = None
        for candidate in candidates:
            parsed_price = self._parse_money(candidate.get("text", ""))
            if parsed_price:
                prices.append(parsed_price[0])
                if selected_price is None:
                    selected_price = parsed_price
                    selected_candidate = candidate

        # Product pages often render the main price with utility classes rather
        # than semantic names. In that context only, the first visible money
        # value is a safer baseline than the previous page-wide maximum.
        if selected_price is None and page_context == "product":
            selected_price = self._parse_money(page_text)
            if selected_price:
                prices = [selected_price[0]]

        return {
            "step": step_idx,
            "step_number": step_idx,
            "url": page.url,
            "title": page.title() or "",
            "page_text": page_text,
            "dom_html": dom_data.get("domHtml", ""),
            "checkboxes": dom_data.get("checkboxes", []),
            "buttons": dom_data.get("buttons", []),
            "disclaimers": dom_data.get("disclaimers", []),
            "interactive_elements": dom_data.get("interactiveElements", []),
            "disclosure_elements": dom_data.get("disclosureElements", []),
            "fee_line_items": dom_data.get("feeLineItems", []),
            "banner_elements": dom_data.get("bannerElements", []),
            "timer_detected": dom_data.get("timerDetected"),
            "cancellation_barrier": dom_data.get("cancellationBarrier"),
            "page_context": page_context,
            "prices": prices,
            "price_detected": selected_price[0] if selected_price else None,
            "price_currency": selected_price[1] if selected_price else None,
            "price_symbol": selected_price[2] if selected_price else None,
            "price_role": selected_candidate.get("price_role") if selected_candidate else ("product" if selected_price else None),
            "price_selector": selected_candidate.get("selector") if selected_candidate else None,
            "price_bounding_box": selected_candidate.get("bounding_box") if selected_candidate else None,
            "screenshot_path": screenshot_path
        }

    @staticmethod
    def _parse_money(text: str):
        match = re.search(
            r"(?:(?P<symbol>[$€£₹])|(?P<code>USD|EUR|GBP|INR))\s*(?P<amount>\d[\d,]*(?:\.\d{1,2})?)",
            str(text or ""),
            re.IGNORECASE
        )
        if not match:
            return None
        symbol_to_currency = {"$": "USD", "€": "EUR", "£": "GBP", "₹": "INR"}
        currency_to_symbol = {"USD": "$", "EUR": "€", "GBP": "£", "INR": "₹"}
        currency = (match.group("code") or symbol_to_currency.get(match.group("symbol"), "")).upper()
        try:
            amount = float(match.group("amount").replace(",", ""))
        except ValueError:
            return None
        return amount, currency, currency_to_symbol.get(currency, match.group("symbol") or "")

    @staticmethod
    def _choose_safe_checkout_action(
        candidates: List[Dict[str, Any]],
        page_context: str,
        phase: str = "primary"
    ) -> Optional[Dict[str, Any]]:
        """Choose only reversible cart/navigation actions, never purchase actions."""
        blocked = re.compile(
            r"sign[ -]?in|log[ -]?in|register|create account|pay(?:ment)?\b|"
            r"place(?: your)? order|submit order|confirm order|complete purchase|"
            r"authorize|one[- ]?click|1[- ]?click",
            re.IGNORECASE
        )
        add_to_cart = re.compile(r"\badd(?: item)? to (?:cart|basket)\b", re.IGNORECASE)
        open_cart = re.compile(r"\b(?:view|go to|open|shopping|your) (?:cart|basket)\b", re.IGNORECASE)
        checkout = re.compile(r"\b(?:proceed(?: to)?|go to|start) checkout\b|\bcheckout\b", re.IGNORECASE)

        if page_context == "product" and phase == "primary":
            add_candidates = []
            for candidate in candidates:
                searchable = " ".join(str(candidate.get(key, "")) for key in ("label", "href", "form_action"))
                identifier = f'{candidate.get("id", "")} {candidate.get("name", "")}'
                if blocked.search(searchable) or not add_to_cart.search(searchable):
                    continue
                if re.search(r"nav-assist|keyboard|hotkey|shortcut|shift\s*\+\s*alt", f"{identifier} {searchable}", re.IGNORECASE):
                    continue
                score = 0
                if candidate.get("id", "").lower() == "add-to-cart-button":
                    score += 100
                if "submit.add-to-cart" in candidate.get("name", "").lower():
                    score += 90
                if re.search(r"handle-buy-box|add-to-cart", candidate.get("form_action", ""), re.IGNORECASE):
                    score += 60
                if candidate.get("tag") in {"button", "input"}:
                    score += 20
                add_candidates.append((score, candidate))
            if add_candidates:
                _, candidate = max(add_candidates, key=lambda item: item[0])
                return {**candidate, "action_type": "add_to_cart"}
            return None

        for candidate in candidates:
            searchable = " ".join(str(candidate.get(key, "")) for key in ("label", "href", "form_action"))
            if blocked.search(searchable):
                continue
            if phase == "after_add" and (
                open_cart.search(searchable)
                or re.search(r"/(?:gp/)?(?:cart|basket)(?:/|\?|$)", searchable, re.IGNORECASE)
            ):
                return {**candidate, "action_type": "open_cart"}
            if page_context == "cart" and checkout.search(searchable):
                return {**candidate, "action_type": "begin_checkout"}
        return None

    @staticmethod
    def _discover_action_candidates(page) -> List[Dict[str, Any]]:
        try:
            return page.evaluate(r"""
                () => {
                    const visible = el => {
                        const style = window.getComputedStyle(el);
                        const box = el.getBoundingClientRect();
                        return box.width > 0 && box.height > 0
                            && style.visibility !== 'hidden'
                            && style.display !== 'none'
                            && !el.disabled
                            && el.getAttribute('aria-disabled') !== 'true';
                    };
                    const elements = Array.from(document.querySelectorAll(
                        'button, input[type="submit"], input[type="button"], [role="button"], a[href]'
                    )).filter(visible).slice(0, 160);
                    return elements.map((el, index) => {
                        const actionId = `pg-safe-action-${index}`;
                        el.setAttribute('data-pattern-guard-action-id', actionId);
                        const form = el.closest('form');
                        return {
                            action_id: actionId,
                            label: (el.innerText || el.value || el.getAttribute('aria-label') || el.title || '').trim().slice(0, 240),
                            href: el.href || '',
                            form_action: form ? (form.action || '') : '',
                            id: el.id || '',
                            name: el.name || '',
                            tag: el.tagName.toLowerCase(),
                            type: (el.type || '').toLowerCase()
                        };
                    }).filter(item => {
                        if (!item.href) return true;
                        try { return new URL(item.href, window.location.href).origin === window.location.origin; }
                        catch { return false; }
                    });
                }
            """) or []
        except Exception:
            return []

    @staticmethod
    def _detect_page_context(page) -> str:
        try:
            return page.evaluate(r"""
                () => {
                    const text = `${window.location.pathname} ${document.title} ${(document.body?.innerText || '').slice(0, 2500)}`;
                    const authLocation = `${window.location.pathname} ${document.title}`;
                    if (document.querySelector('input[type="password"]') || /(?:\/ap\/signin|\/signin|\/login|\/register|amazon sign-in)/i.test(authLocation)) return 'auth';
                    if (/(?:\/checkout|order summary|review your order|payment method)/i.test(text)
                        || document.querySelector('[class*="order-total"], [class*="grand-total"], [class*="checkout-total"]')) return 'checkout';
                    if (/(?:\/cart|\/basket|shopping cart|your basket)/i.test(text)
                        || document.querySelector('[class*="basket"], [id*="basket"], [class*="cart-total"], [id*="cart-total"]')) return 'cart';
                    if (/(?:\/dp\/|\/gp\/product\/)/i.test(window.location.pathname)
                        || document.querySelector('[itemprop="product"], #buy-now-button, #add-to-cart-button')
                        || /product details?|add to cart/i.test(text)) return 'product';
                    return 'browse';
                }
            """)
        except Exception:
            return "unknown"

    def _click_safe_action(
        self,
        page,
        candidate: Dict[str, Any],
        performed_actions: set,
        emit: Callable[[str, Dict[str, Any]], None]
    ) -> bool:
        action_type = candidate.get("action_type", "safe_navigation")
        action_key = (
            page.url.rstrip("/"),
            action_type,
            candidate.get("label", "").lower().strip(),
        )
        if action_key in performed_actions:
            emit("log", {"message": f"Safe action loop prevented: {action_type}"})
            return False
        performed_actions.add(action_key)
        label = candidate.get("label") or action_type.replace("_", " ").title()
        label = " ".join(label.split())
        emit("log", {"message": f"[Safe Action]: {label[:100]}"})
        try:
            if candidate.get("id"):
                selector = f'[id={json.dumps(candidate["id"])}]'
            elif candidate.get("name"):
                selector = f'[name={json.dumps(candidate["name"])}]'
            else:
                selector = f'[data-pattern-guard-action-id={json.dumps(candidate["action_id"])}]'
            previous_url = page.url
            locator = page.locator(selector).first
            # Amazon often renders this control at the bottom edge of the
            # initial viewport. Center it first, then send a genuine pointer
            # click so the site's trusted-event handlers can update the cart.
            locator.evaluate("element => element.scrollIntoView({block: 'center', inline: 'center'})")
            page.wait_for_timeout(350)
            try:
                locator.click(force=True, timeout=8000)
            except Exception as pointer_error:
                emit("log", {
                    "message": f"[Safe Action Notice]: Pointer click failed: {' '.join(str(pointer_error).split())[:240]}"
                })
                # If the pointer click did not already navigate or update the
                # cart, submit the exact allow-listed form control directly.
                already_changed = page.url != previous_url
                if not already_changed:
                    try:
                        already_changed = bool(page.evaluate(r"""
                            () => {
                                const count = document.querySelector('#nav-cart-count, [data-testid*="cart-count" i]');
                                return Boolean(count && Number((count.textContent || '').trim()) > 0);
                            }
                        """))
                    except Exception:
                        already_changed = False
                if not already_changed:
                    emit("log", {"message": "[Safe Action]: Pointer click blocked; using verified form fallback."})
                    try:
                        locator.evaluate(r"""
                            element => {
                                const form = element.closest('form');
                                if (form && ['submit', 'image'].includes((element.type || '').toLowerCase())) {
                                    form.requestSubmit(element);
                                } else {
                                    element.click();
                                }
                            }
                        """)
                    except Exception:
                        raise pointer_error
            try:
                page.wait_for_load_state("domcontentloaded", timeout=8000)
            except Exception:
                pass
            if action_type == "add_to_cart":
                cart_change_confirmed = False
                try:
                    page.wait_for_url(lambda url: url != previous_url, timeout=8000)
                    cart_change_confirmed = True
                except Exception:
                    pass
                if not cart_change_confirmed:
                    try:
                        page.wait_for_function(r"""
                        () => {
                            const visible = el => {
                                const style = window.getComputedStyle(el);
                                const box = el.getBoundingClientRect();
                                return box.width > 0 && box.height > 0 && style.display !== 'none' && style.visibility !== 'hidden';
                            };
                            const count = document.querySelector('#nav-cart-count, [data-testid*="cart-count" i]');
                            if (count && Number((count.textContent || '').trim()) > 0) return true;
                            return Array.from(document.querySelectorAll('[role="alert"], h1, h2, div, span'))
                                .some(el => visible(el) && /added to (?:your )?(?:cart|basket)/i.test(el.innerText || ''));
                        }
                        """, timeout=8000)
                        cart_change_confirmed = True
                    except Exception:
                        pass
                if not cart_change_confirmed:
                    emit("log", {
                        "message": "[Safe Action Notice]: Add-to-cart did not produce a verified cart change."
                    })
                    return False
            page.wait_for_timeout(1000)
            return True
        except Exception as action_error:
            emit("log", {"message": f"[Safe Action Notice]: Could not perform {action_type}: {str(action_error)[:120]}"})
            return False

    def _advance_flow_safely(
        self,
        page,
        flow_type: str,
        page_context: str,
        performed_actions: set,
        emit: Callable[[str, Dict[str, Any]], None]
    ) -> Dict[str, Any]:
        """Advance a flow without authentication, payment, or order submission."""
        if flow_type != "checkout":
            next_url, reason = self._find_next_url_with_intent(page, flow_type)
            return {
                "continue": bool(next_url), "page_ready": False,
                "next_url": next_url, "reason": reason, "action_type": "follow_link" if next_url else None
            }

        if page_context == "auth":
            return {
                "continue": False, "page_ready": False, "next_url": None,
                "reason": "Authentication boundary reached; stopping unauthenticated audit",
                "action_type": "safety_stop_authentication"
            }
        if page_context == "checkout":
            return {
                "continue": False, "page_ready": False, "next_url": None,
                "reason": "Checkout review reached; payment and order submission are disabled",
                "action_type": "safety_stop_before_payment"
            }

        candidates = self._discover_action_candidates(page)
        if page_context == "product":
            add_action = self._choose_safe_checkout_action(candidates, page_context)
            if not add_action:
                next_url, reason = self._find_next_url_with_intent(page, flow_type)
                return {
                    "continue": bool(next_url), "page_ready": False,
                    "next_url": next_url, "reason": reason,
                    "action_type": "follow_checkout_link" if next_url else None
                }
            if not self._click_safe_action(page, add_action, performed_actions, emit):
                return {
                    "continue": False, "page_ready": False, "next_url": None,
                    "reason": "Add-to-cart control was found but could not be activated safely",
                    "action_type": "add_to_cart_failed"
                }

            resulting_context = self._detect_page_context(page)
            if resulting_context == "auth":
                return {
                    "continue": False, "page_ready": False, "next_url": None,
                    "reason": "Authentication boundary reached after cart action; stopping audit",
                    "action_type": "safety_stop_authentication"
                }
            if resulting_context in {"cart", "checkout"}:
                return {
                    "continue": True, "page_ready": True, "next_url": page.url,
                    "reason": "Added item to cart using a reversible safe action",
                    "action_type": "add_to_cart"
                }

            cart_action = self._choose_safe_checkout_action(
                self._discover_action_candidates(page), "product", phase="after_add"
            )
            if cart_action and self._click_safe_action(page, cart_action, performed_actions, emit):
                resulting_context = self._detect_page_context(page)
                if resulting_context == "auth":
                    return {
                        "continue": False, "page_ready": False, "next_url": None,
                        "reason": "Authentication boundary reached; stopping unauthenticated audit",
                        "action_type": "safety_stop_authentication"
                    }
                if resulting_context in {"cart", "checkout"}:
                    return {
                        "continue": True, "page_ready": True, "next_url": page.url,
                        "reason": "Added item to cart and opened the cart safely",
                        "action_type": "add_to_cart_then_open_cart"
                    }
            return {
                "continue": False, "page_ready": False, "next_url": None,
                "reason": "Item was added, but no verified cart transition was available",
                "action_type": "add_to_cart"
            }

        if page_context == "cart":
            cart_hostname = (urllib.parse.urlparse(page.url).hostname or "").lower()
            amazon_cart = bool(re.search(r"(?:^|\.)amazon\.", cart_hostname))
            try:
                visibly_signed_out = bool(page.evaluate(r"""
                    () => Array.from(document.querySelectorAll('a, button')).some(el => {
                        const style = window.getComputedStyle(el);
                        const box = el.getBoundingClientRect();
                        const visible = box.width > 0 && box.height > 0
                            && style.display !== 'none' && style.visibility !== 'hidden';
                        const label = (el.innerText || el.getAttribute('aria-label') || '').trim();
                        return visible && /^(?:hello,?\s*)?sign[ -]?in(?:\s|$)/i.test(label);
                    })
                """))
            except Exception:
                visibly_signed_out = False
            if amazon_cart or visibly_signed_out:
                return {
                    "continue": False, "page_ready": False, "next_url": None,
                    "reason": "Cart captured; authentication is required before checkout and was not attempted",
                    "action_type": "safety_stop_before_authentication"
                }
            checkout_action = self._choose_safe_checkout_action(candidates, page_context)
            if not checkout_action:
                return {
                    "continue": False, "page_ready": False, "next_url": None,
                    "reason": "Cart inspected; no safe checkout-entry control was found",
                    "action_type": "safety_stop_in_cart"
                }
            if not self._click_safe_action(page, checkout_action, performed_actions, emit):
                return {
                    "continue": False, "page_ready": False, "next_url": None,
                    "reason": "Checkout-entry control could not be activated safely",
                    "action_type": "begin_checkout_failed"
                }
            resulting_context = self._detect_page_context(page)
            if resulting_context == "auth":
                return {
                    "continue": False, "page_ready": False, "next_url": None,
                    "reason": "Authentication required to continue; sign-in was not attempted",
                    "action_type": "safety_stop_authentication"
                }
            if resulting_context == "checkout":
                return {
                    "continue": True, "page_ready": True, "next_url": page.url,
                    "reason": "Entered checkout review; payment remains disabled",
                    "action_type": "begin_checkout"
                }
            return {
                "continue": False, "page_ready": False, "next_url": None,
                "reason": "Checkout entry did not reach a verified checkout page",
                "action_type": "safety_stop_unverified_transition"
            }

        return {
            "continue": False, "page_ready": False, "next_url": None,
            "reason": "Page is outside the verified checkout funnel; stopping audit",
            "action_type": "safety_stop_outside_flow"
        }

    def _find_next_url_with_intent(self, page, flow_type: str) -> (Optional[str], str):
        """Finds next step URL and returns the strategic navigation intent."""
        try:
            navigation = page.evaluate(r"""
                (flowType) => {
                    const contextText = `${window.location.pathname} ${document.title}`;
                    if (document.querySelector('input[type="password"]') || /(?:\/signin|\/login|\/register|sign in|log in)/i.test(contextText)) {
                        return {url: null, reason: 'Authentication boundary reached; stopping unauthenticated audit'};
                    }
                    const links = Array.from(document.querySelectorAll('a[href]')).filter(link => {
                        try {
                            const url = new URL(link.href, window.location.href);
                            const label = `${link.innerText || ''} ${link.getAttribute('aria-label') || ''} ${url.pathname}`;
                            const unrelated = /amazon pay|sign in|log in|register|create account|home|logo|customer service|today'?s deals|best sellers|new releases|prime video/i.test(label);
                            return url.origin === window.location.origin
                                && ['http:', 'https:'].includes(url.protocol)
                                && !unrelated
                                && link.href !== window.location.href;
                        } catch { return false; }
                    });
                    
                    // 1. Cancellation funnel matches
                    const cancelRegex = /continue to cancel|proceed to cancel|cancel subscription|confirm cancellation|still want to cancel|keep membership|cancel/i;
                    if (flowType === 'cancellation') {
                        const cancelBtn = links.find(l => cancelRegex.test(`${l.innerText || ''} ${l.getAttribute('aria-label') || ''} ${l.href || ''}`));
                        if (cancelBtn && cancelBtn.href && cancelBtn.href !== window.location.href) {
                            return {url: cancelBtn.href, reason: 'Traversing Cancellation Obstacle Maze'};
                        }
                    }

                    // Require an explicit flow-specific progression link. Never
                    // wander through the site's global navigation as a fallback.
                    const priorityRegex = flowType === 'checkout'
                        ? /proceed(?: to)? checkout|checkout|view cart|go to cart|review order/i
                        : /start|free trial|get access|continue|sign up|join|select plan/i;
                    const nextBtn = links.find(l => priorityRegex.test(`${l.innerText || ''} ${l.getAttribute('aria-label') || ''} ${l.href || ''}`));
                    if (nextBtn && nextBtn.href && nextBtn.href !== window.location.href) {
                        return {url: nextBtn.href, reason: 'Progressing Verified Funnel Link'};
                    }

                    return {url: null, reason: 'No verified funnel transition found'};
                }
            """, flow_type)
            if navigation:
                return navigation.get("url"), navigation.get("reason", "Completed Funnel Walkthrough")
        except Exception:
            pass
        return None, "Completed Funnel Walkthrough"
