#!/usr/bin/env python3
"""
Lemon Email MCP Server - ChatGPT App Store Version
HTTP-based MCP server for remote integration with ChatGPT

CHATGPT APP COMPLIANCE NOTES:
- No server-side API key storage (user provides per-request)
- User must own/control the sender email (fromemail required)
- Email confirmation handled by ChatGPT's confirmation UI
- Stateless operation (no data persistence)
- HTTP transport for remote access
"""

import os
import json
from typing import Any, Dict, Optional
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

# MCP imports
try:
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
    from mcp.types import Tool, TextContent, CallToolResult
    MCP_AVAILABLE = True
except ImportError as e:
    print(f"❌ MCP not available: {e}")
    print("Install with: pip install mcp")
    MCP_AVAILABLE = False

# Server configuration
SERVER_NAME = "lemon-email-chatgpt"
SERVER_VERSION = "3.0.0"
LEMON_API_URL = "https://app.xn--lemn-sqa.com/api/transactional/send"


class LemonEmailClient:
    """
    Direct client for Lemon Email API
    
    SECURITY: No API key stored server-side.
    API key is provided per-request by the user.
    """
    
    def __init__(self, api_key: str):
        """
        Initialize client with user's API key
        
        Args:
            api_key: User's Lemon Email API key (not stored)
        """
        if not api_key:
            raise ValueError("Lemon Email API key is required")
        self.api_key = api_key
        self.api_url = LEMON_API_URL
    
    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        fromemail: str,  # REQUIRED: User must own this email
        fromname: str = "Email Assistant",
        toname: str = "",
        tag: str = "chatgpt-mcp",
        variables: Optional[Dict[str, Any]] = None,
        replyto: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send email directly to Lemon Email API
        
        IMPORTANT: fromemail must be owned/verified by the user
        ChatGPT will show confirmation before sending
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body (plain text or HTML)
            fromemail: Sender email (REQUIRED - must be user's verified email)
            fromname: Sender display name
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
        
        # Set up headers with user's API key
        # NOTE: API key is not logged or stored anywhere
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


def create_mcp_server() -> Server:
    """
    Create MCP server instance
    
    CHATGPT COMPLIANCE:
    - Server has no persistent state
    - No API keys stored server-side
    - Each request is independent
    """
    
    if not MCP_AVAILABLE:
        raise ImportError("MCP library not available. Install with: pip install mcp")
    
    server = Server(SERVER_NAME)
    
    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """
        List available email tools
        
        TOOL DESIGN:
        - Single tool: send_email
        - Requires user's API key per request
        - Requires user's verified sender email
        - ChatGPT shows confirmation UI before execution
        """
        return [
            Tool(
                name="send_email",
                description=(
                    "Send an email via Lemon Email API. "
                    "USER CONFIRMATION: ChatGPT will ask for confirmation before sending. "
                    "REQUIREMENTS: You must provide your Lemon API key and use your verified sender email. "
                    "Get API key from: https://app.xn--lemn-sqa.com or contact manojk030303@gmail.com"
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "api_key": {
                            "type": "string",
                            "description": (
                                "Your Lemon Email API key (REQUIRED). "
                                "Get it from: DM @Norman_Szobotka or email manojk030303@gmail.com. "
                                "This is NOT stored on the server."
                            )
                        },
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
                        "fromemail": {
                            "type": "string",
                            "description": (
                                "YOUR verified sender email address (REQUIRED). "
                                "This must be an email you own and have verified in Lemon Email. "
                                "Example: your.email@yourdomain.com"
                            )
                        },
                        "fromname": {
                            "type": "string",
                            "description": "Sender display name (default: 'Email Assistant')",
                            "default": "Email Assistant"
                        },
                        "toname": {
                            "type": "string",
                            "description": "Recipient display name (optional)",
                            "default": ""
                        },
                        "tag": {
                            "type": "string",
                            "description": "Tag for email categorization/tracking (default: 'chatgpt-mcp')",
                            "default": "chatgpt-mcp"
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
                    "required": ["api_key", "to", "subject", "body", "fromemail"]
                }
            )
        ]
    
    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> CallToolResult:
        """
        Handle tool execution - send emails via Lemon API
        
        SECURITY:
        - API key extracted from request arguments
        - Used only for this request
        - Not logged or stored anywhere
        """
        
        if name != "send_email":
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"❌ Unknown tool: {name}"
                    )
                ]
            )
        
        try:
            # Validate required fields
            required = ["api_key", "to", "subject", "body", "fromemail"]
            missing = [field for field in required if field not in arguments or not arguments[field]]
            
            if missing:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"❌ Missing required fields: {', '.join(missing)}"
                        )
                    ]
                )
            
            # Extract API key from arguments (not stored)
            api_key = arguments.pop("api_key")
            
            # Validate sender email is provided
            if not arguments.get("fromemail"):
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text="❌ fromemail is required. You must use your verified email address."
                        )
                    ]
                )
            
            # Create client with user's API key (per-request)
            email_client = LemonEmailClient(api_key)
            
            # Send email directly to Lemon API
            result = await email_client.send_email(**arguments)
            
            if result["success"]:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=(
                                f"✅ Email sent successfully via Lemon API!\n"
                                f"📧 To: {arguments['to']}\n"
                                f"📝 Subject: {arguments['subject']}\n"
                                f"👤 From: {arguments['fromemail']}\n"
                                f"🔖 Tag: {arguments.get('tag', 'chatgpt-mcp')}\n"
                                f"📊 Status: {result['status_code']}\n"
                                f"🎯 Response: {result['response']}"
                            )
                        )
                    ]
                )
            else:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"❌ Email failed: {result.get('error', 'Unknown error from Lemon API')}"
                        )
                    ]
                )
                
        except Exception as e:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"❌ Error sending email: {type(e).__name__}: {str(e)}"
                    )
                ]
            )
    
    return server


# Global MCP server instance
mcp_server = create_mcp_server()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan manager
    
    CHATGPT COMPLIANCE:
    - Stateless server startup/shutdown
    - No persistent connections or storage
    """
    print(f"🍋 {SERVER_NAME} v{SERVER_VERSION} starting...")
    print(f"🔗 Direct connection to: {LEMON_API_URL}")
    print(f"🌐 HTTP MCP endpoint ready for ChatGPT")
    print(f"🔒 Security: No server-side API keys, user confirmation required")
    yield
    print("🛑 Server shutting down...")


# FastAPI app for HTTP-based MCP
app = FastAPI(
    title="Lemon Email MCP Server",
    description="ChatGPT App Store compatible MCP server for Lemon Email",
    version=SERVER_VERSION,
    lifespan=lifespan
)


@app.get("/")
async def root():
    """
    Root endpoint - server info
    """
    return {
        "name": SERVER_NAME,
        "version": SERVER_VERSION,
        "type": "mcp-server",
        "transport": "http",
        "lemon_api": LEMON_API_URL,
        "chatgpt_compatible": True,
        "security": {
            "api_key_storage": "none - user provides per request",
            "sender_email": "user must own/verify",
            "confirmation": "handled by ChatGPT UI"
        },
        "get_api_key": {
            "twitter": "@Norman_Szobotka",
            "email": "manojk030303@gmail.com",
            "website": "https://app.xn--lemn-sqa.com"
        }
    }


@app.get("/health")
async def health():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "server": SERVER_NAME,
        "version": SERVER_VERSION
    }


@app.post("/mcp")
async def mcp_endpoint(request: Request):
    """
    MCP protocol endpoint for ChatGPT
    
    CHATGPT INTEGRATION:
    - Receives MCP protocol messages via HTTP POST
    - Processes initialization, tool list, and tool calls
    - Returns MCP-formatted responses
    
    SECURITY:
    - No API keys stored on server
    - Stateless request processing
    - User confirmation before email sending
    """
    
    try:
        # Parse incoming MCP request
        body = await request.json()
        
        # Handle MCP protocol messages
        if body.get("method") == "initialize":
            # Return server capabilities
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "result": {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": {
                        "name": SERVER_NAME,
                        "version": SERVER_VERSION
                    },
                    "capabilities": {
                        "tools": {
                            "listChanged": False
                        }
                    }
                }
            })
        
        elif body.get("method") == "tools/list":
            # Return available tools - call the list_tools handler directly
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "result": {
                    "tools": [
                        {
                            "name": "send_email",
                            "description": (
                                "Send an email via Lemon Email API. "
                                "USER CONFIRMATION: ChatGPT will ask for confirmation before sending. "
                                "REQUIREMENTS: You must provide your Lemon API key and use your verified sender email. "
                                "Get API key from: https://app.xn--lemn-sqa.com or contact manojk030303@gmail.com"
                            ),
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "api_key": {
                                        "type": "string",
                                        "description": (
                                            "Your Lemon Email API key (REQUIRED). "
                                            "Get it from: DM @Norman_Szobotka or email manojk030303@gmail.com. "
                                            "This is NOT stored on the server."
                                        )
                                    },
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
                                    "fromemail": {
                                        "type": "string",
                                        "description": (
                                            "YOUR verified sender email address (REQUIRED). "
                                            "This must be an email you own and have verified in Lemon Email. "
                                            "Example: your.email@yourdomain.com"
                                        )
                                    },
                                    "fromname": {
                                        "type": "string",
                                        "description": "Sender display name (default: 'Email Assistant')",
                                        "default": "Email Assistant"
                                    },
                                    "toname": {
                                        "type": "string",
                                        "description": "Recipient display name (optional)",
                                        "default": ""
                                    },
                                    "tag": {
                                        "type": "string",
                                        "description": "Tag for email categorization/tracking (default: 'chatgpt-mcp')",
                                        "default": "chatgpt-mcp"
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
                                "required": ["api_key", "to", "subject", "body", "fromemail"]
                            }
                        }
                    ]
                }
            })
        
        elif body.get("method") == "tools/call":
            # Execute tool call - handle send_email directly
            params = body.get("params", {})
            name = params.get("name")
            arguments = params.get("arguments", {})
            
            if name != "send_email":
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": body.get("id"),
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": f"❌ Unknown tool: {name}"
                            }
                        ]
                    }
                })
            
            # Validate required fields
            required = ["api_key", "to", "subject", "body", "fromemail"]
            missing = [field for field in required if field not in arguments or not arguments[field]]
            
            if missing:
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": body.get("id"),
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": f"❌ Missing required fields: {', '.join(missing)}"
                            }
                        ]
                    }
                })
            
            # Extract API key from arguments (not stored)
            api_key = arguments.pop("api_key")
            
            # Validate sender email is provided
            if not arguments.get("fromemail"):
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": body.get("id"),
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": "❌ fromemail is required. You must use your verified email address."
                            }
                        ]
                    }
                })
            
            # Create client with user's API key (per-request)
            email_client = LemonEmailClient(api_key)
            
            # Send email directly to Lemon API
            result = await email_client.send_email(**arguments)
            
            if result["success"]:
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": body.get("id"),
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": (
                                    f"✅ Email sent successfully via Lemon API!\n"
                                    f"📧 To: {arguments['to']}\n"
                                    f"📝 Subject: {arguments['subject']}\n"
                                    f"👤 From: {arguments['fromemail']}\n"
                                    f"🔖 Tag: {arguments.get('tag', 'chatgpt-mcp')}\n"
                                    f"📊 Status: {result['status_code']}\n"
                                    f"🎯 Response: {result['response']}"
                                )
                            }
                        ]
                    }
                })
            else:
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": body.get("id"),
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": f"❌ Email failed: {result.get('error', 'Unknown error from Lemon API')}"
                            }
                        ]
                    }
                })
        
        else:
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {body.get('method')}"
                }
            }, status_code=400)
            
    except Exception as e:
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": body.get("id") if isinstance(body, dict) else None,
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        }, status_code=500)


def main():
    """
    Main entry point
    
    DEPLOYMENT:
    - Reads PORT from environment (default: 8000)
    - Runs uvicorn HTTP server
    - Ready for cloud deployment (Railway, Render, etc.)
    """
    
    if not MCP_AVAILABLE:
        print("❌ MCP library not available. Install with: pip install mcp")
        return
    
    port = int(os.getenv("PORT", "8000"))
    
    print(f"🚀 Starting HTTP MCP server on port {port}")
    print(f"🔒 ChatGPT App Store compatible")
    print(f"📧 Lemon Email API: {LEMON_API_URL}")
    
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )


if __name__ == "__main__":
    main()