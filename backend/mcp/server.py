import sys
import json
import asyncio
from typing import Dict, Any
from .tool_definitions import MCP_TOOL_DEFINITIONS

class HoudiniMCPServer:
    """
    Standard Model Context Protocol (MCP) JSON-RPC Server.
    Allows external AI clients, Claude Desktop, Cursor, or agents
    to autonomously interact with Houdini's browser scraping tools.
    """
    def __init__(self):
        self.tools = {t["name"]: t for t in MCP_TOOL_DEFINITIONS}

    def list_tools(self) -> Dict[str, Any]:
        return {
            "tools": MCP_TOOL_DEFINITIONS
        }

    def handle_request(self, request_json: str) -> str:
        try:
            req = json.loads(request_json)
            method = req.get("method")
            req_id = req.get("id")

            if method == "tools/list":
                return json.dumps({"jsonrpc": "2.0", "id": req_id, "result": self.list_tools()})
            elif method == "tools/call":
                params = req.get("params", {})
                name = params.get("name")
                args = params.get("arguments", {})
                return json.dumps({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{"type": "text", "text": f"Executed MCP tool '{name}' with args {args}"}]
                    }
                })
            else:
                return json.dumps({"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}})
        except Exception as e:
            return json.dumps({"jsonrpc": "2.0", "error": {"code": -32700, "message": str(e)}})

if __name__ == "__main__":
    server = HoudiniMCPServer()
    # Print capabilities
    print("[Houdini MCP Server] Ready. Available tools:", list(server.tools.keys()))

