#!/usr/bin/env python3
"""
Lemon Email MCP Server - Fixed Version with Proper CallToolResult Handling
"""

import asyncio
import json
import os
import sys
from typing import Any, Dict, List, Optional

import httpx

# MCP imports with error handling
try:
    from mcp.server.models import InitializationOptions
    from mcp.server import NotificationOptions, Server
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        CallToolRequest,
        CallToolResult,
        ListToolsRequest, 
        ListToolsResult,
        TextContent,
        Tool,
    )
    MCP_AVAILABLE = True
except ImportError as e:
    print(f"MCP not available: {e}")
    MCP_AVAILABLE = False

# Server configuration
SERVER_NAME = "lemon-email"
SERVER_VERSION = "1.0.0"

class LemonEmailServer:
    def __init__(self):
        self.api_base_url = os.getenv("LEMON_EMAIL_API_BASE_URL", "https://app.xn--lemn-sqa.com/api")
        self.api_key = os.getenv("LEMON_EMAIL_API_KEY")
        
        if not self.api_key:
            raise ValueError("LEMON_EMAIL_API_KEY environment variable is required")
    
    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        fromname: str = "Email Assistant",
        fromemail: Optional[str] = None,
        toname: str = "",
        tag: str = "mcp-agent",
        variables: Optional[Dict[str, Any]] = None,
        replyto: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send an email using the Lemon Email API"""
        
        if not replyto:
            replyto = fromemail
        
        payload = {
            "fromname": fromname,
            "fromemail": fromemail,
            "to": to,
            "toname": toname,
            "subject": subject,
            "body": body,
            "tag": tag,
            "variables": variables or {},
            "replyto": replyto
        }
        
        headers = {
            "Content-Type": "application/json",
            "X-Auth-APIKey": self.api_key
        }
        
        url = f"{self.api_base_url}/transactional/send"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url, 
                    headers=headers, 
                    json=payload,
                    timeout=30.0
                )
                
                response_data = {
                    "status_code": response.status_code,
                    "response": response.text,
                    "success": response.is_success
                }
                
                if not response.is_success:
                    response_data["error"] = f"API error {response.status_code}: {response.text}"
                
                return response_data
                
            except httpx.TimeoutException:
                return {
                    "success": False,
                    "error": "Request timed out after 30 seconds"
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Network error: {str(e)}"
                }

def create_server():
    """Create and configure the MCP server"""
    if not MCP_AVAILABLE:
        raise ImportError("MCP library not available")
        
    server = Server(SERVER_NAME)
    email_server = LemonEmailServer()
    
    @server.list_tools()
    async def list_tools() -> List[Tool]:
        """List available tools"""
        return [
            Tool(
                name="send_email",
                description=(
                    "Send an email using the Lemon Email service. "
                    "This tool allows AI agents to send transactional emails."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "to": {
                            "type": "string",
                            "description": "Recipient email address"
                        },
                        "subject": {
                            "type": "string", 
                            "description": "Email subject line"
                        },
                        "body": {
                            "type": "string",
                            "description": "Email body content"
                        },
                        "fromname": {
                            "type": "string",
                            "description": "Sender name",
                            "default": "Email Assistant"
                        },
                        "fromemail": {
                            "type": "string",
                            "description": "Sender email address (required)"
                        },
                        "toname": {
                            "type": "string",
                            "description": "Recipient name",
                            "default": ""
                        },
                        "tag": {
                            "type": "string",
                            "description": "Email tag for tracking",
                            "default": "mcp-agent"
                        },
                        "variables": {
                            "type": "object",
                            "description": "Template variables (key-value pairs)",
                            "additionalProperties": True
                        },
                        "replyto": {
                            "type": "string",
                            "description": "Reply-to email address"
                        }
                    },
                    "required": ["to", "subject", "body", "fromemail"]
                }
            )
        ]
    
    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        """Handle tool calls with simplified return"""
        if name == "send_email":
            try:
                # Validate required fields
                required = ["to", "subject", "body", "fromemail"]
                missing = [field for field in required if field not in arguments or not arguments[field]]
                
                if missing:
                    # Return simple dict instead of CallToolResult
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": f"❌ Missing required fields: {', '.join(missing)}"
                            }
                        ]
                    }
                
                result = await email_server.send_email(**arguments)
                
                if result["success"]:
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": f"✅ Email sent successfully!\nStatus: {result['status_code']}\nResponse: {result['response']}"
                            }
                        ]
                    }
                else:
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": f"❌ Email failed: {result.get('error', 'Unknown error')}"
                            }
                        ]
                    }
                    
            except Exception as e:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"❌ Error sending email: {str(e)}"
                        }
                    ]
                }
        else:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"❌ Unknown tool: {name}"
                    }
                ]
            }
    
    return server

async def run_mcp_server():
    """Run the MCP server with better error handling"""
    if not MCP_AVAILABLE:
        print("❌ MCP library not available. Install with: pip install mcp")
        return
        
    if not os.getenv("LEMON_EMAIL_API_KEY"):
        print("❌ LEMON_EMAIL_API_KEY environment variable required")
        return
    
    print(f"🚀 Starting {SERVER_NAME} MCP server v{SERVER_VERSION}...")
    print("📡 Waiting for MCP client connection...")
    print("💡 Press Ctrl+C to stop")
    
    try:
        server = create_server()
        
        async with stdio_server() as (read_stream, write_stream):
            initialization_options = InitializationOptions(
                server_name=SERVER_NAME,
                server_version=SERVER_VERSION,
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
            
            await server.run(
                read_stream, 
                write_stream, 
                initialization_options
            )
            
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

async def run_standalone_test():
    """Run standalone test without MCP"""
    print("🧪 Running standalone email test...")
    
    try:
        email_server = LemonEmailServer()
        
        result = await email_server.send_email(
            to="manojk030303@gmail.com",
            subject="Standalone Test Email",
            body="This is a test email from the standalone server.",
            fromname="Standalone Test",
            fromemail="mail@member-notification.com"
        )
        
        if result["success"]:
            print(f"✅ Email sent successfully!")
            print(f"   Status: {result['status_code']}")
            print(f"   Response: {result['response']}")
        else:
            print(f"❌ Email failed: {result['error']}")
            
    except Exception as e:
        print(f"❌ Test error: {type(e).__name__}: {e}")

def print_usage():
    """Print usage instructions"""
    print("🍋 Lemon Email MCP Server")
    print("=" * 30)
    print("Usage:")
    print("  python simple_mcp_server.py          # Start MCP server")
    print("  python simple_mcp_server.py test     # Run standalone test")
    print("  python simple_mcp_server.py help     # Show this help")
    print("\nEnvironment:")
    print("  LEMON_EMAIL_API_KEY     Required API key")
    print("  LEMON_EMAIL_API_BASE_URL Optional base URL")

async def main():
    """Main entry point with better argument handling"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "test":
            await run_standalone_test()
        elif command in ["help", "-h", "--help"]:
            print_usage()
        else:
            print(f"❌ Unknown command: {command}")
            print_usage()
    else:
        await run_mcp_server()

if __name__ == "__main__":
    asyncio.run(main())