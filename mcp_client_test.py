#!/usr/bin/env python3
"""
Working MCP Client Test for Lemon Email
"""

import asyncio
import json
import os
import subprocess
import sys
import time

class WorkingMCPClient:
    """A simple working MCP client using subprocess"""
    
    def __init__(self):
        self.server_path = "simple_mcp_server.py"
        self.api_key = os.getenv("LEMON_EMAIL_API_KEY")
    
    async def test_mcp_server(self):
        """Test the MCP server with direct subprocess communication"""
        
        print("🔧 Testing MCP Server with Direct Communication")
        print("=" * 50)
        
        # Set up environment
        env = os.environ.copy()
        env["LEMON_EMAIL_API_KEY"] = self.api_key
        
        print("📡 Starting MCP server process...")
        
        # Start server process
        process = subprocess.Popen(
            [sys.executable, self.server_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
            bufsize=0  # Unbuffered
        )
        
        try:
            print("✅ Server process started (PID: {})".format(process.pid))
            
            # Wait a moment for server to initialize
            await asyncio.sleep(0.5)
            
            # Step 1: Initialize the connection
            print("\n🤝 Step 1: Initialize MCP connection")
            print("-" * 30)
            
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "experimental": {},
                        "sampling": {}
                    },
                    "clientInfo": {
                        "name": "lemon-email-test-client",
                        "version": "1.0.0"
                    }
                }
            }
            
            success = await self.send_and_receive(process, init_request, "initialization")
            if not success:
                return False
            
            # Step 2: Send initialized notification
            print("\n📢 Step 2: Send initialized notification")
            print("-" * 30)
            
            initialized_notif = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized"
            }
            
            await self.send_notification(process, initialized_notif)
            
            # Step 3: List available tools
            print("\n📋 Step 3: List available tools")
            print("-" * 30)
            
            list_tools_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list"
            }
            
            tools_response = await self.send_and_receive(process, list_tools_request, "tools list")
            if not tools_response:
                return False
            
            # Step 4: Call the send_email tool
            print("\n📧 Step 4: Test send_email tool")
            print("-" * 30)
            
            call_tool_request = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "send_email",
                    "arguments": {
                        "to": "manojk030303@gmail.com",
                        "subject": "🤖 MCP Protocol Test Success!",
                        "body": "Congratulations! 🎉\n\nYour Lemon Email MCP server is working perfectly!\n\nThis email was sent through:\n✅ MCP Protocol communication\n✅ Your custom MCP server\n✅ Lemon Email API\n\nYour server is ready for AI agent integration!",
                        "fromname": "MCP Test Robot",
                        "fromemail": "mail@member-notification.com",
                        "tag": "mcp-success-test"
                    }
                }
            }
            
            email_response = await self.send_and_receive(process, call_tool_request, "email sending")
            
            if email_response:
                print("\n🎉 SUCCESS! Your MCP server is working perfectly!")
                print("🎯 Ready for AI agent integration!")
                return True
            else:
                return False
                
        except Exception as e:
            print(f"❌ Test failed with error: {type(e).__name__}: {e}")
            return False
        finally:
            # Clean up
            try:
                process.terminate()
                await asyncio.sleep(1)
                if process.poll() is None:
                    process.kill()
            except:
                pass
    
    async def send_notification(self, process, notification):
        """Send a notification (no response expected)"""
        try:
            message = json.dumps(notification) + "\n"
            process.stdin.write(message)
            process.stdin.flush()
            print(f"📤 Sent notification: {notification['method']}")
            
            # Give server time to process
            await asyncio.sleep(0.2)
            
        except Exception as e:
            print(f"❌ Failed to send notification: {e}")
    
    async def send_and_receive(self, process, request, operation_name):
        """Send request and wait for response"""
        try:
            # Send request
            message = json.dumps(request) + "\n"
            process.stdin.write(message)
            process.stdin.flush()
            
            print(f"📤 Sent {operation_name} request (ID: {request.get('id')})")
            
            # Read response with timeout
            response_text = None
            for _ in range(50):  # 5 second timeout
                if process.stdout.readable():
                    line = process.stdout.readline()
                    if line.strip():
                        response_text = line.strip()
                        break
                await asyncio.sleep(0.1)
            
            if not response_text:
                print(f"❌ No response received for {operation_name}")
                return False
            
            # Parse response
            try:
                response = json.loads(response_text)
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON response for {operation_name}: {e}")
                print(f"Raw response: {response_text[:200]}...")
                return False
            
            # Check for errors
            if "error" in response:
                error = response["error"]
                print(f"❌ Server error for {operation_name}:")
                print(f"   Code: {error.get('code')}")
                print(f"   Message: {error.get('message')}")
                return False
            
            # Process successful response
            if "result" in response:
                result = response["result"]
                
                if operation_name == "initialization":
                    server_info = result.get("serverInfo", {})
                    print(f"✅ Connected to: {server_info.get('name', 'Unknown')} v{server_info.get('version', 'Unknown')}")
                    print(f"   Protocol version: {result.get('protocolVersion')}")
                    
                elif operation_name == "tools list":
                    tools = result.get("tools", [])
                    print(f"✅ Found {len(tools)} tool(s):")
                    for tool in tools:
                        print(f"   🔧 {tool['name']}: {tool['description'][:60]}...")
                    
                elif operation_name == "email sending":
                    content = result.get("content", [])
                    print("✅ Email tool response:")
                    for item in content:
                        text = item.get("text", "")
                        for line in text.split("\n"):
                            if line.strip():
                                print(f"   {line}")
                
                return True
            else:
                print(f"❌ Unexpected response format for {operation_name}")
                return False
                
        except Exception as e:
            print(f"❌ Communication error for {operation_name}: {type(e).__name__}: {e}")
            return False

async def test_simple_connection():
    """Simple connection test"""
    print("🔌 Quick Connection Test")
    print("=" * 30)
    
    # Check if server file exists
    if not os.path.exists("simple_mcp_server.py"):
        print("❌ simple_mcp_server.py not found!")
        return False
    
    # Test standalone mode first
    print("1️⃣  Testing standalone mode...")
    try:
        if not os.getenv("LEMON_EMAIL_API_KEY"):
            print("❌ LEMON_EMAIL_API_KEY environment variable required")
            return
        result = subprocess.run([
            sys.executable, "simple_mcp_server.py", "test"
        ], capture_output=True, text=True, timeout=10, env={
            **os.environ,
            "LEMON_EMAIL_API_KEY": os.getenv("LEMON_EMAIL_API_KEY")
        })
        
        if result.returncode == 0 and "✅" in result.stdout:
            print("✅ Standalone mode works!")
        else:
            print("❌ Standalone mode failed")
            print(f"Output: {result.stdout}")
            print(f"Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Standalone test timed out")
        return False
    except Exception as e:
        print(f"❌ Standalone test error: {e}")
        return False
    
    print("\n2️⃣  Testing MCP server startup...")
    
    # Test MCP server starts
    env = os.environ.copy()
    env["LEMON_EMAIL_API_KEY"] = os.getenv("LEMON_EMAIL_API_KEY")
    
    process = subprocess.Popen([
        sys.executable, "simple_mcp_server.py"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
    
    try:
        # Wait for startup message
        await asyncio.sleep(2)
        
        if process.poll() is None:
            print("✅ MCP server started successfully!")
            process.terminate()
            return True
        else:
            stdout, stderr = process.communicate()
            print("❌ MCP server failed to start")
            print(f"Output: {stdout}")
            print(f"Error: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ MCP server test error: {e}")
        process.terminate()
        return False

async def main():
    """Main test runner"""
    print("🍋 LEMON EMAIL MCP - COMPREHENSIVE TEST")
    print("=" * 60)
    
    # Quick checks first
    simple_ok = await test_simple_connection()
    
    if not simple_ok:
        print("\n❌ Basic tests failed. Fix these issues first.")
        return
    
    print("\n" + "=" * 60)
    
    # Full MCP protocol test
    client = WorkingMCPClient()
    mcp_ok = await client.test_mcp_server()
    
    print("\n" + "=" * 60)
    print("📊 FINAL RESULTS")
    print("=" * 60)
    
    if mcp_ok:
        print("🎉 CONGRATULATIONS!")
        print("✅ Your Lemon Email MCP server is fully functional!")
        print("\n🚀 Next Steps:")
        print("   1. Your server works with the MCP protocol ✅")
        print("   2. AI agents can discover and use your email tool ✅") 
        print("   3. Ready to integrate with:")
        print("      • Continue.dev (VS Code extension)")
        print("      • Cline (VS Code extension)")  
        print("      • Other MCP-compatible tools")
        print("      • Custom AI applications")
        print("\n📦 Ready to publish to:")
        print("   • GitHub (for community use)")
        print("   • PyPI (pip install lemon-email-mcp)")
        
    else:
        print("❌ MCP protocol test failed")
        print("🔧 But your email API is working - check the errors above")

if __name__ == "__main__":
    asyncio.run(main())