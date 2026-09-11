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
from playwright.sync_api import sync_playwright

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
        visited_urls = set()

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

            for step_idx in range(1, max_steps + 1):
                if cancel_event and cancel_event.is_set():
                    emit("log", {"message": "Audit cancelled because the client disconnected."})
                    break
                normalized_current = current_url.rstrip("/")
                if normalized_current in visited_urls:
                    emit("log", {"message": f"Navigation loop prevented at {current_url}"})
                    break
                visited_urls.add(normalized_current)
                emit("log", {"message": f"Step {step_idx}: Navigating to {current_url}..."})
                step_title = f"Step {step_idx}"

                try:
                    page.goto(current_url, wait_until="domcontentloaded", timeout=15000)
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
                except Exception as nav_error:
                    emit("log", {"message": f"Step {step_idx} navigation failed: {str(nav_error)[:160]}"})
                    if step_idx == 1:
                        raise RuntimeError(f"Unable to load target URL: {nav_error}") from nav_error
                    break

                # Capture raw screenshot
                raw_filename = f"raw_{scan_id}_step{step_idx}.png"
                raw_filepath = os.path.join(SCREENSHOTS_DIR, raw_filename)
                raw_rel_url = f"/static/screenshots/{raw_filename}"
                page.screenshot(path=raw_filepath, full_page=False)

                # High-speed single JS evaluation for comprehensive DOM features (<10ms)
                step_data = self._fast_extract_dom(page, step_idx, raw_rel_url)
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
                    api_key=None
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

                if next_url and next_url.rstrip("/") not in visited_urls:
                    current_url = self._validate_public_target(next_url)
                else:
                    break

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
                    max(step.get("prices", []) or [0.0]), json.dumps({"disclaimers": step.get("disclaimers", [])})
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
                    const moneyRegex = /(?:\$|USD\s*)\s*([0-9]+(?:\.[0-9]{1,2})?)/i;
                    const feeLineItems = allTextNodes.filter(el => {
                        const matches = feeRegex.test(el.innerText || '') && moneyRegex.test(el.innerText || '');
                        const matchingChild = Array.from(el.children).some(child => feeRegex.test(child.innerText || '') && moneyRegex.test(child.innerText || ''));
                        return matches && !matchingChild;
                    }).slice(0, 12).map(el => {
                        const item = metadata(el);
                        const amount = (el.innerText || '').match(moneyRegex);
                        return {...item, name: item.text, amount: amount ? Number(amount[1]) : 0, is_mandatory: true};
                    });

                    const pageText = document.body ? document.body.innerText.slice(0, 12000) : '';
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
                        pageText,
                        domHtml: document.documentElement.outerHTML.slice(0, 20000)
                    };
                }
            """)
        except Exception:
            dom_data = {
                "checkboxes": [], "buttons": [], "disclaimers": [], "interactiveElements": [],
                "disclosureElements": [], "feeLineItems": [], "bannerElements": [], "pageText": "", "domHtml": ""
            }

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
            "prices": prices,
            "price_detected": max(prices) if prices else None,
            "screenshot_path": screenshot_path
        }

    def _find_next_url_with_intent(self, page, flow_type: str) -> (Optional[str], str):
        """Finds next step URL and returns the strategic navigation intent."""
        try:
            next_href = page.evaluate("""
                (flowType) => {
                    const links = Array.from(document.querySelectorAll('a[href]')).filter(link => {
                        try {
                            const url = new URL(link.href, window.location.href);
                            return url.origin === window.location.origin && ['http:', 'https:'].includes(url.protocol);
                        } catch { return false; }
                    });
                    
                    // 1. Cancellation funnel matches
                    const cancelRegex = /continue to cancel|proceed to cancel|cancel subscription|confirm cancellation|still want to cancel|keep membership|cancel/i;
                    if (flowType === 'cancellation') {
                        const cancelBtn = links.find(l => cancelRegex.test(`${l.innerText || ''} ${l.getAttribute('aria-label') || ''} ${l.href || ''}`));
                        if (cancelBtn && cancelBtn.href && cancelBtn.href !== window.location.href) {
                            return cancelBtn.href;
                        }
                    }

                    // 2. Progression matches (checkout, trial, start, continue, dashboard, order)
                    const priorityRegex = /proceed|checkout|buy now|start|free trial|get access|continue|view cart|order now|dashboard|sign up|join|plan/i;
                    const nextBtn = links.find(l => priorityRegex.test(`${l.innerText || ''} ${l.getAttribute('aria-label') || ''} ${l.href || ''}`));
                    if (nextBtn && nextBtn.href && nextBtn.href !== window.location.href) {
                        return nextBtn.href;
                    }

                    // 3. Fallback: first internal valid link
                    const anyLink = links.find(l => l.href && !l.href.includes('#') && l.href !== window.location.href);
                    if (anyLink && anyLink.href) return anyLink.href;

                    return null;
                }
            """, flow_type)
            if next_href:
                intent = "Traversing Cancellation Obstacle Maze" if "cancel" in (flow_type + next_href).lower() else "Progressing Funnel Walkthrough"
                return next_href, intent
        except Exception:
            pass
        return None, "Completed Funnel Walkthrough"
