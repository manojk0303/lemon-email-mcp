#!/usr/bin/env python3
"""
Lemon Email MCP Server - Direct API Integration
No intermediate servers - connects directly to Lemon Email API
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
        Tool,
    )
    MCP_AVAILABLE = True
except ImportError as e:
    print(f"MCP not available: {e}")
    MCP_AVAILABLE = False

# Server configuration
SERVER_NAME = "lemon-email"
SERVER_VERSION = "2.0.0"
LEMON_API_URL = "https://app.xn--lemn-sqa.com/api/transactional/send"

class LemonEmailClient:
    """Direct client for Lemon Email API - no intermediates"""
    
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("Lemon Email API key is required")
        self.api_key = api_key
        self.api_url = LEMON_API_URL
    
    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        fromname: str = "Email Assistant",
        fromemail: str = "mail@member-notification.com",
        toname: str = "",
        tag: str = "mcp-agent",
        variables: Optional[Dict[str, Any]] = None,
        replyto: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send email directly to Lemon Email API
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body (plain text or HTML)
            fromname: Sender display name
            fromemail: Sender email address
            toname: Recipient display name
            tag: Tag for categorization/tracking
            variables: Template variables (dict)
            replyto: Reply-to address
            
        Returns:
            Dict with success status and response details
        """
        
        if not replyto:
            replyto = fromemail
        
        # Prepare payload for Lemon Email API
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
        
        # Set up headers with API key
        headers = {
            "Content-Type": "application/json",
            "X-Auth-APIKey": self.api_key
        }
        
        # Make direct API call to Lemon Email
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.api_url,
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
                    response_data["error"] = f"Lemon API error {response.status_code}: {response.text}"
                
                return response_data
                
            except httpx.TimeoutException:
                return {
                    "success": False,
                    "error": "Request to Lemon API timed out after 30 seconds"
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Network error connecting to Lemon API: {str(e)}"
                }

def create_mcp_server(api_key: str):
    """Create and configure the MCP server with direct Lemon API access"""
    
    if not MCP_AVAILABLE:
        raise ImportError("MCP library not available. Install with: pip install mcp")
    
    server = Server(SERVER_NAME)
    email_client = LemonEmailClient(api_key)
    
    @server.list_tools()
    async def list_tools() -> List[Tool]:
        """List available email tools"""
        return [
            Tool(
                name="send_email",
                description=(
                    "Send an email directly via Lemon Email API. "
                    "Perfect for AI agents to send transactional emails, notifications, and messages."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "to": {
                            "type": "string",
                            "description": "Recipient email address (required)"
                        },
                        "subject": {
                            "type": "string",
                            "description": "Email subject line (required)"
                        },
                        "body": {
                            "type": "string",
                            "description": "Email body content - supports plain text or HTML (required)"
                        },
                        "fromname": {
                            "type": "string",
                            "description": "Sender display name (default: 'Email Assistant')",
                            "default": "Email Assistant"
                        },
                        "fromemail": {
                            "type": "string",
                            "description": "Sender email address (default: 'mail@member-notification.com')",
                            "default": "mail@member-notification.com"
                        },
                        "toname": {
                            "type": "string",
                            "description": "Recipient display name (optional)",
                            "default": ""
                        },
                        "tag": {
                            "type": "string",
                            "description": "Tag for email categorization/tracking (default: 'mcp-agent')",
                            "default": "mcp-agent"
                        },
                        "variables": {
                            "type": "object",
                            "description": "Template variables as key-value pairs (optional)",
                            "additionalProperties": True
                        },
                        "replyto": {
                            "type": "string",
                            "description": "Reply-to email address (optional, defaults to fromemail)"
                        }
                    },
                    "required": ["to", "subject", "body"]
                }
            )
        ]
    
    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        """Handle tool execution - send emails via Lemon API"""
        
        if name != "send_email":
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"❌ Unknown tool: {name}"
                    }
                ]
            }
        
        try:
            # Validate required fields
            required = ["to", "subject", "body"]
            missing = [field for field in required if field not in arguments or not arguments[field]]
            
            if missing:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"❌ Missing required fields: {', '.join(missing)}"
                        }
                    ]
                }
            
            # Send email directly to Lemon API
            result = await email_client.send_email(**arguments)
            
            if result["success"]:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                f"✅ Email sent successfully via Lemon API!\n"
                                f"📧 To: {arguments['to']}\n"
                                f"📝 Subject: {arguments['subject']}\n"
                                f"🔖 Tag: {arguments.get('tag', 'mcp-agent')}\n"
                                f"📊 Status: {result['status_code']}\n"
                                f"🎯 Response: {result['response']}"
                            )
                        }
                    ]
                }
            else:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"❌ Email failed: {result.get('error', 'Unknown error from Lemon API')}"
                        }
                    ]
                }
                
        except Exception as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"❌ Error sending email: {type(e).__name__}: {str(e)}"
                    }
                ]
            }
    
    return server

async def run_mcp_server():
    """Run the MCP server with direct Lemon API connection"""
    
    if not MCP_AVAILABLE:
        print("❌ MCP library not available. Install with: pip install mcp")
        return
    
    api_key = os.getenv("LEMON_EMAIL_API_KEY")
    if not api_key:
        print("❌ LEMON_EMAIL_API_KEY environment variable required")
        print("💡 Set it with: export LEMON_EMAIL_API_KEY='your-key-here'")
        return
    
    print(f"🍋 Starting {SERVER_NAME} MCP Server v{SERVER_VERSION}")
    print(f"🔗 Direct connection to: {LEMON_API_URL}")
    print("📡 Waiting for MCP client connection...")
    print("💡 Press Ctrl+C to stop")
    
    try:
        server = create_mcp_server(api_key)
        
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
    """Test direct connection to Lemon API"""
    
    print("🧪 Testing direct connection to Lemon Email API...")
    print("=" * 50)
    
    api_key = os.getenv("LEMON_EMAIL_API_KEY")
    if not api_key:
        print("❌ LEMON_EMAIL_API_KEY environment variable required")
        return
    
    try:
        email_client = LemonEmailClient(api_key)
        
        print("📧 Sending test email...")
        result = await email_client.send_email(
            to="test@example.com",  # Change to your email
            subject="🧪 Direct API Test - Lemon Email MCP",
            body=(
                "This is a test email sent directly to Lemon Email API!\n\n"
                "✅ No intermediate servers\n"
                "✅ Direct API connection\n"
                "✅ Fast and reliable\n\n"
                "Your MCP server is working perfectly!"
            ),
            fromname="Lemon MCP Test",
            fromemail="mail@member-notification.com",
            tag="direct-api-test"
        )
        
        print("\n" + "=" * 50)
        if result["success"]:
            print("✅ SUCCESS! Email sent directly to Lemon API")
            print(f"📊 Status Code: {result['status_code']}")
            print(f"📝 Response: {result['response']}")
            print("\n🎉 Your direct API connection is working!")
        else:
            print("❌ FAILED to send email")
            print(f"⚠️  Error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Test error: {type(e).__name__}: {e}")

def print_usage():
    """Print usage instructions"""
    print("🍋 Lemon Email MCP Server - Direct API")
    print("=" * 50)
    print("\nUsage:")
    print("  python simple_mcp_server.py          # Start MCP server")
    print("  python simple_mcp_server.py test     # Test direct API connection")
    print("  python simple_mcp_server.py help     # Show this help")
    print("\nEnvironment Variables:")
    print("  LEMON_EMAIL_API_KEY (required)       Your Lemon Email API key")
    print("\nGet API Key:")
    print("  DM @Norman_Szobotka on Twitter")
    print("  Email: manojk030303@gmail.com")
    print("\nDirect API Endpoint:")
    print(f"  {LEMON_API_URL}")

async def main():
    """Main entry point"""
    
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