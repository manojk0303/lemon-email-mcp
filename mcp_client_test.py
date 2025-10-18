#!/usr/bin/env python3
"""
Lemon Email MCP Server Test Suite - Direct API Version
Tests MCP protocol communication and direct Lemon API integration
"""

import asyncio
import json
import os
import subprocess
import sys

class LemonMCPTester:
    """Test client for Lemon Email MCP server"""
    
    def __init__(self):
        self.server_path = "simple_mcp_server.py"
        self.api_key = os.getenv("LEMON_EMAIL_API_KEY")
        
        if not self.api_key:
            raise ValueError("LEMON_EMAIL_API_KEY environment variable required")
    
    async def test_mcp_protocol(self):
        """Test full MCP protocol communication"""
        
        print("🔧 Testing MCP Server with Direct Lemon API")
        print("=" * 60)
        
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
            bufsize=0
        )
        
        try:
            print(f"✅ Server process started (PID: {process.pid})")
            
            # Wait for server initialization
            await asyncio.sleep(0.5)
            
            # Step 1: Initialize MCP connection
            print("\n🤝 Step 1: Initialize MCP connection")
            print("-" * 40)
            
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
                        "version": "2.0.0"
                    }
                }
            }
            
            if not await self.send_and_receive(process, init_request, "initialization"):
                return False
            
            # Step 2: Send initialized notification
            print("\n📢 Step 2: Send initialized notification")
            print("-" * 40)
            
            initialized_notif = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized"
            }
            
            await self.send_notification(process, initialized_notif)
            
            # Step 3: List available tools
            print("\n📋 Step 3: List available tools")
            print("-" * 40)
            
            list_tools_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list"
            }
            
            if not await self.send_and_receive(process, list_tools_request, "tools list"):
                return False
            
            # Step 4: Test send_email tool with direct API
            print("\n📧 Step 4: Test send_email tool (Direct Lemon API)")
            print("-" * 40)
            
            call_tool_request = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "send_email",
                    "arguments": {
                        "to": "test@example.com",  # Change to your test email
                        "subject": "🚀 Direct API Test - MCP Protocol Success!",
                        "body": (
                            "Congratulations! 🎉\n\n"
                            "Your Lemon Email MCP server is working perfectly!\n\n"
                            "✅ MCP Protocol communication successful\n"
                            "✅ Direct connection to Lemon Email API\n"
                            "✅ No intermediate servers (Railway removed)\n"
                            "✅ Fast and reliable email delivery\n\n"
                            "Your server is ready for AI agent integration!\n\n"
                            "Next steps:\n"
                            "• Integrate with Claude Desktop\n"
                            "• Use with Continue.dev or Cline\n"
                            "• Build custom AI workflows\n\n"
                            "Happy automating! 🤖"
                        ),
                        "fromname": "MCP Test Robot",
                        "fromemail": "mail@member-notification.com",
                        "tag": "direct-api-test"
                    }
                }
            }
            
            if await self.send_and_receive(process, call_tool_request, "email sending"):
                print("\n" + "=" * 60)
                print("🎉 SUCCESS! Your MCP server is fully functional!")
                print("=" * 60)
                print("\n✅ Verified:")
                print("   • MCP protocol communication")
                print("   • Direct Lemon Email API connection")
                print("   • Tool discovery and execution")
                print("   • Email sending capability")
                print("\n🚀 Ready for:")
                print("   • Claude Desktop integration")
                print("   • Continue.dev / Cline integration")
                print("   • Custom AI agent workflows")
                return True
            else:
                return False
                
        except Exception as e:
            print(f"❌ Test failed: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            # Clean up process
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
                # Check for stderr output
                if process.stderr.readable():
                    stderr_line = process.stderr.readline()
                    if stderr_line:
                        print(f"⚠️  Server error: {stderr_line}")
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
                if "data" in error:
                    print(f"   Data: {error['data']}")
                return False
            
            # Process successful response
            if "result" in response:
                result = response["result"]
                
                if operation_name == "initialization":
                    server_info = result.get("serverInfo", {})
                    print(f"✅ Connected to: {server_info.get('name', 'Unknown')} v{server_info.get('version', 'Unknown')}")
                    print(f"   Protocol version: {result.get('protocolVersion')}")
                    capabilities = result.get("capabilities", {})
                    print(f"   Tools available: {capabilities.get('tools', {})}")
                    
                elif operation_name == "tools list":
                    tools = result.get("tools", [])
                    print(f"✅ Found {len(tools)} tool(s):")
                    for tool in tools:
                        print(f"   🔧 {tool['name']}")
                        print(f"      {tool['description'][:70]}...")
                        required = tool.get('inputSchema', {}).get('required', [])
                        print(f"      Required params: {', '.join(required)}")
                    
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

async def test_basic_setup():
    """Test basic setup and prerequisites"""
    print("🔍 Pre-flight Checks")
    print("=" * 60)
    
    checks_passed = True
    
    # Check 1: Server file exists
    print("\n1️⃣  Checking server file...")
    if os.path.exists("simple_mcp_server.py"):
        print("   ✅ simple_mcp_server.py found")
    else:
        print("   ❌ simple_mcp_server.py not found!")
        checks_passed = False
    
    # Check 2: API key set
    print("\n2️⃣  Checking API key...")
    if os.getenv("LEMON_EMAIL_API_KEY"):
        api_key = os.getenv("LEMON_EMAIL_API_KEY")
        masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
        print(f"   ✅ API key configured: {masked_key}")
    else:
        print("   ❌ LEMON_EMAIL_API_KEY not set!")
        print("   💡 Set it with: export LEMON_EMAIL_API_KEY='your-key'")
        checks_passed = False
    
    # Check 3: Dependencies
    print("\n3️⃣  Checking dependencies...")
    try:
        import mcp
        print("   ✅ mcp library installed")
    except ImportError:
        print("   ❌ mcp library not found!")
        print("   💡 Install with: pip install mcp")
        checks_passed = False
    
    try:
        import httpx
        print("   ✅ httpx library installed")
    except ImportError:
        print("   ❌ httpx library not found!")
        print("   💡 Install with: pip install httpx")
        checks_passed = False
    
    # Check 4: Standalone test
    if checks_passed:
        print("\n4️⃣  Testing standalone mode...")
        try:
            result = subprocess.run(
                [sys.executable, "simple_mcp_server.py", "test"],
                capture_output=True,
                text=True,
                timeout=15,
                env={**os.environ, "LEMON_EMAIL_API_KEY": os.getenv("LEMON_EMAIL_API_KEY")}
            )
            
            if result.returncode == 0 and "✅" in result.stdout:
                print("   ✅ Standalone test passed")
                print("   ✅ Direct Lemon API connection verified")
            else:
                print("   ❌ Standalone test failed")
                print(f"   Output: {result.stdout}")
                if result.stderr:
                    print(f"   Error: {result.stderr}")
                checks_passed = False
                
        except subprocess.TimeoutExpired:
            print("   ❌ Standalone test timed out")
            checks_passed = False
        except Exception as e:
            print(f"   ❌ Standalone test error: {e}")
            checks_passed = False
    
    print("\n" + "=" * 60)
    return checks_passed

async def test_mcp_server_startup():
    """Test that MCP server starts correctly"""
    print("\n🚀 Testing MCP Server Startup")
    print("=" * 60)
    
    env = os.environ.copy()
    env["LEMON_EMAIL_API_KEY"] = os.getenv("LEMON_EMAIL_API_KEY")
    
    print("📡 Starting MCP server...")
    
    process = subprocess.Popen(
        [sys.executable, "simple_mcp_server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env
    )
    
    try:
        await asyncio.sleep(2)
        
        if process.poll() is None:
            print("✅ MCP server started successfully")
            print(f"   PID: {process.pid}")
            process.terminate()
            return True
        else:
            stdout, stderr = process.communicate()
            print("❌ MCP server failed to start")
            print(f"Output: {stdout}")
            print(f"Error: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Startup test error: {e}")
        process.terminate()
        return False

async def main():
    """Main test orchestrator"""
    print("\n" + "=" * 70)
    print("🍋 LEMON EMAIL MCP SERVER - COMPREHENSIVE TEST SUITE")
    print("   Direct API Integration (No Railway)")
    print("=" * 70)
    
    # Phase 1: Basic setup checks
    basic_ok = await test_basic_setup()
    
    if not basic_ok:
        print("\n❌ Pre-flight checks failed!")
        print("🔧 Fix the issues above and try again.")
        return
    
    # Phase 2: Server startup
    startup_ok = await test_mcp_server_startup()
    
    if not startup_ok:
        print("\n❌ Server startup failed!")
        return
    
    # Phase 3: Full MCP protocol test
    print("\n" + "=" * 70)
    tester = LemonMCPTester()
    protocol_ok = await tester.test_mcp_protocol()
    
    # Final summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    
    if protocol_ok:
        print("\n🎉 ALL TESTS PASSED!")
        print("\n✅ Your Lemon Email MCP server is production-ready!")
        print("\n🚀 What's working:")
        print("   • Direct Lemon Email API connection (no Railway)")
        print("   • MCP protocol implementation")
        print("   • Tool discovery and execution")
        print("   • Email sending capability")
        print("\n📱 Next steps:")
        print("   1. Integrate with Claude Desktop")
        print("      Add to: ~/Library/Application Support/Claude/claude_desktop_config.json")
        print("\n   2. Integrate with Continue.dev or Cline")
        print("      Add to: .continue/config.json")
        print("\n   3. Build custom AI workflows")
        print("      Use the MCP protocol to send emails from any AI agent")
        print("\n📚 Documentation:")
        print("   See README.md for integration examples")
    else:
        print("\n❌ TESTS FAILED")
        print("\n🔧 Issues found:")
        print("   Check the error messages above")
        print("\n💡 Troubleshooting:")
        print("   • Verify your API key is correct")
        print("   • Check internet connection")
        print("   • Try standalone test: python simple_mcp_server.py test")
        print("   • Check Lemon API status")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n🛑 Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()