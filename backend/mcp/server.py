import asyncio
import json
import sys
from typing import Dict, Any

from .tool_definitions import MCP_TOOL_DEFINITIONS
from ..agent.flow_crawler import AutonomousFlowCrawler
from ..database.db import get_db_connection, init_db


class PatternGuardMCPServer:
    """JSON-RPC MCP stdio server backed by Pattern Guard's crawler and database."""

    def __init__(self):
        init_db()
        self.tools = {tool["name"]: tool for tool in MCP_TOOL_DEFINITIONS}
        self.crawler = AutonomousFlowCrawler()

    def list_tools(self) -> Dict[str, Any]:
        return {"tools": MCP_TOOL_DEFINITIONS}

    def _get_site_audit(self, identifier: str) -> Dict[str, Any]:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sites WHERE id = ? OR domain = ?", (identifier, identifier))
            row = cursor.fetchone()
            if not row:
                raise ValueError("Site not found")
            site = dict(row)
            cursor.execute("SELECT * FROM scans WHERE site_id = ? ORDER BY created_at DESC", (site["id"],))
            scans = [dict(item) for item in cursor.fetchall()]
            cursor.execute("SELECT * FROM findings WHERE site_id = ? ORDER BY created_at DESC", (site["id"],))
            findings = [dict(item) for item in cursor.fetchall()]
            return {"site": site, "scans": scans, "findings": findings}
        finally:
            conn.close()

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        if name == "audit_url":
            max_steps = int(arguments.get("max_steps", 4))
            if not 1 <= max_steps <= 10:
                raise ValueError("max_steps must be between 1 and 10")
            return asyncio.run(self.crawler.run_scan(
                target_url=arguments["url"],
                site_name=arguments.get("site_name"),
                flow_type=arguments.get("flow_type", "general"),
                max_steps=max_steps
            ))
        if name == "get_site_audit":
            return self._get_site_audit(arguments["site_id_or_domain"])
        raise ValueError(f"Unknown MCP tool: {name}")

    def handle_request(self, request_json: str) -> str:
        request_id = None
        try:
            request = json.loads(request_json)
            request_id = request.get("id")
            method = request.get("method")
            if method == "initialize":
                result = {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "pattern-guard", "version": "2.0.0"}
                }
            elif method == "tools/list":
                result = self.list_tools()
            elif method == "tools/call":
                params = request.get("params", {})
                payload = self.call_tool(params.get("name", ""), params.get("arguments", {}))
                result = {"content": [{"type": "text", "text": json.dumps(payload)}]}
            elif method == "notifications/initialized":
                return ""
            else:
                raise KeyError("Method not found")
            return json.dumps({"jsonrpc": "2.0", "id": request_id, "result": result})
        except KeyError as error:
            return json.dumps({"jsonrpc": "2.0", "id": request_id, "error": {"code": -32601, "message": str(error)}})
        except Exception as error:
            return json.dumps({"jsonrpc": "2.0", "id": request_id, "error": {"code": -32000, "message": str(error)}})


if __name__ == "__main__":
    server = PatternGuardMCPServer()
    for line in sys.stdin:
        response = server.handle_request(line)
        if response:
            print(response, flush=True)
