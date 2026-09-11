MCP_TOOL_DEFINITIONS = [
    {
        "name": "audit_url",
        "description": "Run a Pattern Guard dark-pattern audit and persist the resulting evidence.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Public HTTP(S) URL or a built-in localhost /mock URL."},
                "site_name": {"type": "string"},
                "flow_type": {
                    "type": "string",
                    "enum": ["checkout", "cancellation", "signup", "general"],
                    "default": "general"
                },
                "max_steps": {"type": "integer", "minimum": 1, "maximum": 10, "default": 4}
            },
            "required": ["url"]
        }
    },
    {
        "name": "get_site_audit",
        "description": "Retrieve a persisted site, its scan history, and forensic findings by site ID or domain.",
        "inputSchema": {
            "type": "object",
            "properties": {"site_id_or_domain": {"type": "string"}},
            "required": ["site_id_or_domain"]
        }
    }
]
