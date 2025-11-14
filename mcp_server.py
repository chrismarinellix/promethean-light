#!/usr/bin/env python3
"""MCP Server for Promethean Light - Gives Claude access to your database"""

import json
import sys
from typing import Any
import requests


class PrometheanLightMCP:
    """MCP Server for Promethean Light database"""

    def __init__(self):
        self.base_url = "http://localhost:8000"

    def is_daemon_running(self) -> bool:
        """Check if Promethean Light daemon is running"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=1)
            return response.status_code == 200
        except Exception:
            return False

    def search(self, query: str, limit: int = 10) -> dict:
        """Search the Promethean Light database"""
        if not self.is_daemon_running():
            return {
                "error": "Promethean Light daemon not running. Start it with START.bat"
            }

        try:
            response = requests.post(
                f"{self.base_url}/search",
                json={"query": query, "limit": limit},
                timeout=10
            )
            response.raise_for_status()
            results = response.json()

            return {
                "success": True,
                "query": query,
                "results": results,
                "count": len(results)
            }
        except Exception as e:
            return {"error": str(e)}

    def add_note(self, text: str) -> dict:
        """Add a note to Promethean Light"""
        if not self.is_daemon_running():
            return {
                "error": "Promethean Light daemon not running. Start it with START.bat"
            }

        try:
            response = requests.post(
                f"{self.base_url}/add",
                json={"text": text, "source": "claude"},
                timeout=30
            )
            response.raise_for_status()
            return {"success": True, "result": response.json()}
        except Exception as e:
            return {"error": str(e)}

    def get_stats(self) -> dict:
        """Get database statistics"""
        if not self.is_daemon_running():
            return {
                "error": "Promethean Light daemon not running. Start it with START.bat"
            }

        try:
            response = requests.get(f"{self.base_url}/stats", timeout=5)
            response.raise_for_status()
            return {"success": True, "stats": response.json()}
        except Exception as e:
            return {"error": str(e)}

    def get_tags(self) -> dict:
        """Get all tags from the database"""
        if not self.is_daemon_running():
            return {
                "error": "Promethean Light daemon not running. Start it with START.bat"
            }

        try:
            response = requests.get(f"{self.base_url}/tags", timeout=5)
            response.raise_for_status()
            return {"success": True, "tags": response.json()}
        except Exception as e:
            return {"error": str(e)}


def run_mcp_server():
    """Run the MCP server"""
    server = PrometheanLightMCP()

    # MCP protocol loop
    for line in sys.stdin:
        try:
            request = json.loads(line)
            method = request.get("method")
            params = request.get("params", {})

            if method == "tools/list":
                # List available tools
                response = {
                    "tools": [
                        {
                            "name": "promethean_search",
                            "description": "Search your Promethean Light knowledge base. Use this to find information from your ingested files, emails, and notes.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "query": {
                                        "type": "string",
                                        "description": "The search query"
                                    },
                                    "limit": {
                                        "type": "number",
                                        "description": "Maximum results to return",
                                        "default": 10
                                    }
                                },
                                "required": ["query"]
                            }
                        },
                        {
                            "name": "promethean_add_note",
                            "description": "Add a note or piece of information to your Promethean Light database",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "text": {
                                        "type": "string",
                                        "description": "The note/text to add"
                                    }
                                },
                                "required": ["text"]
                            }
                        },
                        {
                            "name": "promethean_stats",
                            "description": "Get statistics about your Promethean Light database (total documents, tags, etc.)",
                            "inputSchema": {
                                "type": "object",
                                "properties": {}
                            }
                        },
                        {
                            "name": "promethean_tags",
                            "description": "Get all tags from your knowledge base to see what topics you have",
                            "inputSchema": {
                                "type": "object",
                                "properties": {}
                            }
                        }
                    ]
                }
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})

                if tool_name == "promethean_search":
                    result = server.search(
                        arguments.get("query"),
                        arguments.get("limit", 10)
                    )
                elif tool_name == "promethean_add_note":
                    result = server.add_note(arguments.get("text"))
                elif tool_name == "promethean_stats":
                    result = server.get_stats()
                elif tool_name == "promethean_tags":
                    result = server.get_tags()
                else:
                    result = {"error": f"Unknown tool: {tool_name}"}

                response = {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
            else:
                response = {"error": f"Unknown method: {method}"}

            print(json.dumps(response), flush=True)

        except Exception as e:
            error_response = {"error": str(e)}
            print(json.dumps(error_response), flush=True)


if __name__ == "__main__":
    run_mcp_server()
