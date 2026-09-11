import os
import sys
import json
import asyncio
import threading
import secrets
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any, Literal

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Set Windows Proactor event loop policy if on Windows
if sys.platform == "win32":
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    except Exception:
        pass

from fastapi import FastAPI, HTTPException, Query, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse, FileResponse
from pydantic import BaseModel, Field

try:
    from backend.database.db import get_db_connection, init_db
    from backend.database.seed_data import seed_database
    from backend.agent.flow_crawler import AutonomousFlowCrawler, STATIC_DIR
    from backend.mock_sites.mock_templates import (
        SHOPSNEAK_HTML_STEP1, SHOPSNEAK_HTML_STEP2,
        GYMTRAP_HTML_SIGNUP, GYMTRAP_HTML_DASHBOARD,
        GYMTRAP_HTML_CANCEL_1, GYMTRAP_HTML_CANCEL_2,
        GYMTRAP_HTML_CANCEL_3, GYMTRAP_HTML_CANCEL_4
    )
except ImportError:
    from database.db import get_db_connection, init_db
    from database.seed_data import seed_database
    from agent.flow_crawler import AutonomousFlowCrawler, STATIC_DIR
    from mock_sites.mock_templates import (
        SHOPSNEAK_HTML_STEP1, SHOPSNEAK_HTML_STEP2,
        GYMTRAP_HTML_SIGNUP, GYMTRAP_HTML_DASHBOARD,
        GYMTRAP_HTML_CANCEL_1, GYMTRAP_HTML_CANCEL_2,
        GYMTRAP_HTML_CANCEL_3, GYMTRAP_HTML_CANCEL_4
    )

@asynccontextmanager
async def lifespan(application: FastAPI):
    init_db()
    seed_database()
    yield


app = FastAPI(
    title="Pattern Guard Dark Pattern Prosecution API",
    description="Autonomous dark pattern detection, DOM analysis, and regulatory prosecution engine.",
    version="2.0.0",
    lifespan=lifespan
)

allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:8000,http://127.0.0.1:8000"
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static folder for screenshots and annotated evidence
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Mount frontend dist if built
FRONTEND_DIST = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "dist")
if os.path.exists(FRONTEND_DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")

crawler = AutonomousFlowCrawler()
scan_semaphore = asyncio.Semaphore(max(1, int(os.getenv("MAX_CONCURRENT_SCANS", "2"))))


def verify_scan_token(provided_token: Optional[str]) -> None:
    configured_token = os.getenv("SCAN_API_TOKEN", "").strip()
    if configured_token and not provided_token:
        raise HTTPException(status_code=401, detail="Missing scan API token")
    if configured_token and not secrets.compare_digest(provided_token, configured_token):
        raise HTTPException(status_code=403, detail="Invalid scan API token")

# Request Models
class ScanRequest(BaseModel):
    target_url: str = Field(min_length=3, max_length=2048)
    site_name: Optional[str] = Field(default=None, max_length=120)
    flow_type: Literal["checkout", "cancellation", "signup", "general"] = "checkout"
    max_steps: int = Field(default=4, ge=1, le=10)
    ai_api_key: Optional[str] = Field(default=None, max_length=512)
    grok_api_key: Optional[str] = Field(default=None, max_length=512)
    ai_endpoint: Optional[str] = Field(default=None, max_length=2048)
    ai_model: Optional[str] = Field(default=None, max_length=160)
    bright_data_wss_url: Optional[str] = Field(default=None, max_length=2048)

# Root Route: Serve compiled frontend if available
@app.get("/", response_class=HTMLResponse)
def serve_index():
    index_file = os.path.join(FRONTEND_DIST, "index.html")
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="""
        <html>
            <head><title>Pattern Guard API</title></head>
            <body style='font-family: monospace; padding: 2rem; background: #0a0a0a; color: #fff;'>
                <h2>Pattern Guard Dark Pattern Detection Engine</h2>
                <p>FastAPI Backend is running on port 8000.</p>
                <p>Access Dashboard at <a href='http://localhost:8000' style='color: #6798ff;'>http://localhost:8000</a></p>
            </body>
        </html>
    """)

@app.get("/api/health")
def health_check():
    return {"status": "operational", "engine": "Pattern Guard Prosecution Engine v2.0"}

@app.get("/api/stats")
def get_global_stats():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total_sites, AVG(manipulation_index) as avg_score FROM sites")
    site_stats = cursor.fetchone()

    cursor.execute("SELECT COUNT(*) as total_findings FROM findings")
    finding_stats = cursor.fetchone()

    cursor.execute("SELECT COUNT(*) as ftc_critical FROM findings WHERE severity IN ('Critical', 'High')")
    critical_stats = cursor.fetchone()

    cursor.execute("""
        SELECT category, COUNT(*) as count 
        FROM findings 
        GROUP BY category 
        ORDER BY count DESC
    """)
    categories = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return {
        "total_sites_audited": site_stats["total_sites"] or 0,
        "avg_manipulation_index": round(site_stats["avg_score"] or 0.0, 1),
        "total_patterns_prosecuted": finding_stats["total_findings"] or 0,
        "ftc_violations_flagged": critical_stats["ftc_critical"] or 0,
        "category_breakdown": categories
    }

@app.get("/api/leaderboard")
def get_leaderboard(
    sort: Literal["manipulation_index", "name", "last_scanned_at", "critical_count"] = "manipulation_index",
    order: Literal["asc", "desc"] = "desc"
):
    conn = get_db_connection()
    cursor = conn.cursor()

    order_sql = "DESC" if order.lower() == "desc" else "ASC"
    sort_sql = {
        "manipulation_index": "manipulation_index",
        "name": "name",
        "last_scanned_at": "last_scanned_at",
        "critical_count": "critical_count"
    }[sort]
    cursor.execute(f"""
        SELECT id, domain, name, category, manipulation_index, grade, status,
               scans_count, critical_count, high_count, medium_count, low_count,
               top_violation, primary_pattern, ftc_risk_level, last_scanned_at
        FROM sites
        ORDER BY {sort_sql} {order_sql}
    """)
    sites = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {"leaderboard": sites, "total": len(sites)}


def _json_value(value: Optional[str], fallback):
    if not value:
        return fallback
    try:
        return json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return fallback


def _hydrate_scan(cursor, scan_row) -> Dict[str, Any]:
    scan = dict(scan_row)
    cursor.execute("SELECT * FROM sites WHERE id = ?", (scan["site_id"],))
    site = dict(cursor.fetchone())
    cursor.execute("SELECT * FROM findings WHERE scan_id = ? ORDER BY created_at", (scan["id"],))
    findings = [dict(row) for row in cursor.fetchall()]
    for finding in findings:
        finding["bounding_box"] = _json_value(finding.get("bounding_box"), None)
    severity_counts = {
        severity: sum(1 for finding in findings if finding.get("severity") == severity)
        for severity in ("Critical", "High", "Medium", "Low")
    }
    score_value = scan["manipulation_index"]
    risk_level = "Compliant" if score_value <= 15 else "Low" if score_value <= 30 else "High" if score_value <= 65 else "Critical Violation Liability"

    findings_by_step = {}
    for finding in findings:
        findings_by_step.setdefault(finding.get("step_id"), []).append(finding)

    cursor.execute("SELECT * FROM flow_steps WHERE scan_id = ? ORDER BY step_number", (scan["id"],))
    nodes = []
    for row in cursor.fetchall():
        step = dict(row)
        dom_snapshot = _json_value(step.get("dom_snapshot"), {})
        metadata = _json_value(step.get("raw_metadata"), {})
        step_findings = findings_by_step.get(step["id"], [])
        nodes.append({
            "step_number": step["step_number"], "url": step["url"], "title": step["step_name"],
            "raw_screenshot": step.get("screenshot_path"),
            "annotated_screenshot": step.get("annotated_screenshot_path") or step.get("screenshot_path"),
            "findings_count": len(step_findings), "findings": step_findings,
            "buttons": dom_snapshot.get("buttons", []), "checkboxes": dom_snapshot.get("checkboxes", []),
            "prices": [step["price_detected"]] if step.get("price_detected") else [],
            "disclaimers": metadata.get("disclaimers", []), "navigation_intent": step.get("action_type")
        })

    return {
        "site_id": site["id"], "scan_id": scan["id"], "domain": site["domain"],
        "site_name": site["name"], "flow_type": scan["flow_type"], "duration_ms": scan["duration_ms"],
        "total_steps": scan["total_steps"], "created_at": scan["created_at"],
        "score_summary": {
            "manipulation_index": scan["manipulation_index"], "grade": scan["grade"],
            "ftc_risk_level": risk_level, "critical_count": severity_counts["Critical"],
            "high_count": severity_counts["High"], "medium_count": severity_counts["Medium"],
            "low_count": severity_counts["Low"], "total_findings": len(findings)
        },
        "findings": findings, "steps": nodes, "navigation_nodes": nodes, "persisted": True
    }


@app.get("/api/scans")
def get_recent_scans(limit: int = Query(default=50, ge=1, le=100)):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM scans ORDER BY created_at DESC LIMIT ?", (limit,))
        scans = [_hydrate_scan(cursor, row) for row in cursor.fetchall()]
        return {"scans": scans, "total": len(scans)}
    finally:
        conn.close()


@app.get("/api/scans/{scan_id}")
def get_scan(scan_id: str):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM scans WHERE id = ?", (scan_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Scan not found")
        return _hydrate_scan(cursor, row)
    finally:
        conn.close()

@app.get("/api/sites/{site_id}")
def get_site_details(site_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM sites WHERE id = ? OR domain = ?", (site_id, site_id))
    site_row = cursor.fetchone()
    if not site_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Site not found")

    site = dict(site_row)

    cursor.execute("SELECT * FROM scans WHERE site_id = ? ORDER BY created_at DESC", (site["id"],))
    scans = [dict(r) for r in cursor.fetchall()]

    cursor.execute("""
        SELECT * FROM findings 
        WHERE site_id = ? 
        ORDER BY CASE severity 
            WHEN 'Critical' THEN 1 
            WHEN 'High' THEN 2 
            WHEN 'Medium' THEN 3 
            ELSE 4 END
    """, (site["id"],))
    findings = [dict(r) for r in cursor.fetchall()]
    for finding in findings:
        finding["bounding_box"] = _json_value(finding.get("bounding_box"), None)

    conn.close()
    return {
        "site": site,
        "scans": scans,
        "findings": findings
    }

@app.get("/api/findings/{finding_id}")
def get_finding_by_id(finding_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM findings WHERE id = ?", (finding_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Finding not found")
    return dict(row)

# Standard REST Scan Trigger
@app.post("/api/scan")
async def trigger_scan(req: ScanRequest, x_pattern_guard_token: Optional[str] = Header(default=None)):
    verify_scan_token(x_pattern_guard_token)
    try:
        active_key = req.ai_api_key or req.grok_api_key
        async with scan_semaphore:
            result = await crawler.run_scan(
                target_url=req.target_url,
                site_name=req.site_name,
                flow_type=req.flow_type,
                max_steps=req.max_steps,
                ai_api_key=active_key,
                ai_endpoint=req.ai_endpoint,
                ai_model=req.ai_model,
                bright_data_wss_url=req.bright_data_wss_url
            )
        return {
            "success": True,
            "message": "Scan completed and evidence recorded",
            "result": result
        }
    except ValueError as e:
        return JSONResponse(status_code=400, content={"success": False, "error": str(e)})
    except Exception as e:
        print(f"[Scan Execution Error]: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

# Live Real-Time Streaming Scan (SSE)
@app.post("/api/scan/stream")
async def trigger_streaming_scan(req: ScanRequest, x_pattern_guard_token: Optional[str] = Header(default=None)):
    """
    Streams real-time crawler logs, viewport screenshots, and discovered findings as Server-Sent Events (SSE).
    """
    verify_scan_token(x_pattern_guard_token)
    queue = asyncio.Queue(maxsize=512)
    cancel_event = threading.Event()
    active_key = req.ai_api_key or req.grok_api_key

    def event_callback(event_data: Dict[str, Any]):
        try:
            queue.put_nowait(event_data)
        except Exception:
            pass

    async def scan_worker():
        try:
            async with scan_semaphore:
                await crawler.run_scan(
                    target_url=req.target_url,
                    site_name=req.site_name,
                    flow_type=req.flow_type,
                    max_steps=req.max_steps,
                    ai_api_key=active_key,
                    ai_endpoint=req.ai_endpoint,
                    ai_model=req.ai_model,
                    bright_data_wss_url=req.bright_data_wss_url,
                    event_callback=event_callback,
                    cancel_event=cancel_event
                )
        except Exception as err:
            queue.put_nowait({"event": "error", "message": str(err)})
        finally:
            queue.put_nowait({"event": "stream_end"})

    asyncio.create_task(scan_worker())

    async def event_generator():
        try:
            while True:
                item = await queue.get()
                if item.get("event") == "stream_end":
                    yield f"data: {json.dumps({'event': 'stream_end'})}\n\n"
                    break
                yield f"data: {json.dumps(item)}\n\n"
        finally:
            cancel_event.set()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

# Mock Target Testground Webpages
@app.get("/mock/styles.css", response_class=FileResponse)
def mock_stylesheet():
    return FileResponse(
        os.path.join(PROJECT_ROOT, "backend", "mock_sites", "mock.css"),
        media_type="text/css"
    )


@app.get("/mock/shopsneak", response_class=HTMLResponse)
def mock_shopsneak_step1():
    return HTMLResponse(content=SHOPSNEAK_HTML_STEP1)

@app.get("/mock/shopsneak/checkout", response_class=HTMLResponse)
def mock_shopsneak_step2():
    return HTMLResponse(content=SHOPSNEAK_HTML_STEP2)

@app.get("/mock/gymtrap", response_class=HTMLResponse)
def mock_gymtrap_signup():
    return HTMLResponse(content=GYMTRAP_HTML_SIGNUP)

@app.get("/mock/gymtrap/dashboard", response_class=HTMLResponse)
def mock_gymtrap_dashboard():
    return HTMLResponse(content=GYMTRAP_HTML_DASHBOARD)

@app.get("/mock/gymtrap/cancel-1", response_class=HTMLResponse)
def mock_gymtrap_cancel_step1():
    return HTMLResponse(content=GYMTRAP_HTML_CANCEL_1)

@app.get("/mock/gymtrap/cancel-2", response_class=HTMLResponse)
def mock_gymtrap_cancel_step2():
    return HTMLResponse(content=GYMTRAP_HTML_CANCEL_2)

@app.get("/mock/gymtrap/cancel-3", response_class=HTMLResponse)
def mock_gymtrap_cancel_step3():
    return HTMLResponse(content=GYMTRAP_HTML_CANCEL_3)

@app.get("/mock/gymtrap/cancel-4", response_class=HTMLResponse)
def mock_gymtrap_cancel_step4():
    return HTMLResponse(content=GYMTRAP_HTML_CANCEL_4)
