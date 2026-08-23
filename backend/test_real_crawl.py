import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.agent.flow_crawler import AutonomousFlowCrawler

async def test_live_crawl():
    print("=== TESTING REAL-WORLD LIVE AUTONOMOUS CRAWLER ===")
    crawler = AutonomousFlowCrawler()

    events_received = []
    async def on_event(event):
        events_received.append(event.get("event"))
        if event.get("event") == "log":
            print(f"  [STREAM LOG] {event.get('message')}")
        elif event.get("event") == "step_started":
            print(f"  [STREAM STEP] Step {event.get('step_number')}: {event.get('title')}")
        elif event.get("event") == "finding_detected":
            print(f"  [STREAM FINDING] {event.get('pattern')} [{event.get('severity')}]")

    print("\n--- Scanning Live Public Site: https://news.ycombinator.com ---")
    result = await crawler.run_scan(
        target_url="https://news.ycombinator.com",
        site_name="Hacker News Live",
        flow_type="general",
        max_steps=1,
        event_callback=on_event
    )

    print("\n[OK] Scan completed successfully!")
    print(f"  Domain: {result['domain']}")
    print(f"  Total Steps: {result['total_steps']}")
    print(f"  Duration: {result['duration_ms']}ms")
    print(f"  Manipulation Index: {result['score_summary']['manipulation_index']}/100 [GRADE {result['score_summary']['grade']}]")
    print(f"  Events Streamed: {len(events_received)} ({set(events_received)})")
    
    assert result["total_steps"] >= 1
    rel_subpath = result["steps"][0]["raw_screenshot"].replace("/static/", "")
    full_screenshot_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", rel_subpath)
    assert os.path.exists(full_screenshot_path), f"Screenshot not found at {full_screenshot_path}"
    print(f"[OK] Real viewport screenshot verified at: {full_screenshot_path}")

if __name__ == "__main__":
    asyncio.run(test_live_crawl())
