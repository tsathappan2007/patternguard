import os
import sys
import json
import asyncio
from typing import Optional, List, Dict, Any

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

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel

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

app = FastAPI(
    title="Houdini Dark Pattern Prosecution API",
    description="Autonomous dark pattern detection, DOM analysis, and regulatory prosecution engine.",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
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

@app.on_event("startup")
def on_startup():
    init_db()
    seed_database()

# Request Models
class ScanRequest(BaseModel):
    target_url: str
    site_name: Optional[str] = None
    flow_type: str = "checkout"
    max_steps: int = 4
    ai_api_key: Optional[str] = None
    grok_api_key: Optional[str] = None  # Backward compatibility

# Root Route: Serve compiled frontend if available
@app.get("/", response_class=HTMLResponse)
def serve_index():
    index_file = os.path.join(FRONTEND_DIST, "index.html")
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="""
        <html>
            <head><title>Houdini API</title></head>
            <body style='font-family: monospace; padding: 2rem; background: #0a0a0a; color: #fff;'>
                <h2>Houdini Dark Pattern Detection Engine</h2>
                <p>FastAPI Backend is running on port 8000.</p>
                <p>Access Dashboard at <a href='http://localhost:8000' style='color: #6798ff;'>http://localhost:8000</a></p>
            </body>
        </html>
    """)

@app.get("/api/health")
def health_check():
    return {"status": "operational", "engine": "Houdini Prosecution Engine v2.0"}

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
def get_leaderboard(sort: str = "manipulation_index", order: str = "desc"):
    conn = get_db_connection()
    cursor = conn.cursor()

    order_sql = "DESC" if order.lower() == "desc" else "ASC"
    cursor.execute(f"""
        SELECT id, domain, name, category, manipulation_index, grade, status,
               scans_count, critical_count, high_count, medium_count, low_count,
               top_violation, primary_pattern, ftc_risk_level, last_scanned_at
        FROM sites
        ORDER BY manipulation_index {order_sql}
    """)
    sites = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {"leaderboard": sites, "total": len(sites)}

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
async def trigger_scan(req: ScanRequest):
    try:
        active_key = req.ai_api_key or req.grok_api_key
        result = await crawler.run_scan(
            target_url=req.target_url,
            site_name=req.site_name,
            flow_type=req.flow_type,
            max_steps=req.max_steps,
            ai_api_key=active_key
        )
        return {
            "success": True,
            "message": "Scan completed and evidence recorded",
            "result": result
        }
    except Exception as e:
        print(f"[Scan Execution Error]: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

# Live Real-Time Streaming Scan (SSE)
@app.post("/api/scan/stream")
async def trigger_streaming_scan(req: ScanRequest):
    """
    Streams real-time crawler logs, viewport screenshots, and discovered findings as Server-Sent Events (SSE).
    """
    queue = asyncio.Queue()
    active_key = req.ai_api_key or req.grok_api_key

    def event_callback(event_data: Dict[str, Any]):
        try:
            queue.put_nowait(event_data)
        except Exception:
            pass

    async def scan_worker():
        try:
            await crawler.run_scan(
                target_url=req.target_url,
                site_name=req.site_name,
                flow_type=req.flow_type,
                max_steps=req.max_steps,
                ai_api_key=active_key,
                event_callback=event_callback
            )
        except Exception as err:
            queue.put_nowait({"event": "error", "message": str(err)})
        finally:
            queue.put_nowait({"event": "stream_end"})

    asyncio.create_task(scan_worker())

    async def event_generator():
        while True:
            item = await queue.get()
            if item.get("event") == "stream_end":
                yield f"data: {json.dumps({'event': 'stream_end'})}\n\n"
                break
            yield f"data: {json.dumps(item)}\n\n"

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
