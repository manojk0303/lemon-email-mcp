# 🍋 Lemon Email MCP - Direct API Integration

> **Send emails directly from AI agents.** No intermediate servers. Zero config.

<div align="center">

[![Direct API](https://img.shields.io/badge/🔗_Direct_API-Lemon_Email-brightgreen?style=for-the-badge)](https://app.xn--lemn-sqa.com)
[![Open Source](https://img.shields.io/badge/📖_Open_Source-MIT-blue?style=for-the-badge)](LICENSE)
[![MCP Compatible](https://img.shields.io/badge/🤖_MCP-Compatible-orange?style=for-the-badge)](https://modelcontextprotocol.io)

</div>

---

## 🚀 What This Does

**Connects AI agents directly to Lemon Email API** - no intermediate servers, no proxies, just direct API calls.

- ✅ **Direct connection** to Lemon Email API
- ✅ **No Railway or other intermediates** - pure API client
- ✅ **MCP protocol** for AI agent integration
- ✅ **Works with Claude Desktop, Continue.dev, Cline**
- ✅ **Open source** - see exactly what it does

---

## ⚡ Quick Start (30 seconds)

**1. Clone & Install**
```bash
git clone https://github.com/manojk0303/lemon-email-mcp.git
cd lemon-email-mcp
pip install -r requirements.txt
```

**2. Get API Key**
- DM [@Norman_Szobotka](https://x.com/Norman_Szobotka) on Twitter
- Or email: [manojk030303@gmail.com](mailto:manojk030303@gmail.com)
- You'll get your key instantly!

**3. Set API Key**
```bash
export LEMON_EMAIL_API_KEY="your-key-here"
```

**4. Test It**
```bash
python simple_mcp_server.py test
```

Done! 🎉

---

## 🔧 Usage Methods

### **Method 1: Claude Desktop** (Recommended for Mac users)

**1. Find your Claude config:**
- Mac: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

**2. Add this to your config:**
```json
{
  "mcpServers": {
    "lemon-email": {
      "command": "python",
      "args": ["/full/path/to/lemon-email-mcp/simple_mcp_server.py"],
      "env": {
        "LEMON_EMAIL_API_KEY": "your-key-here"
      }
    }
  }
}
```

**3. Restart Claude Desktop**

**4. Test it:**
```
"Send a test email to test@example.com with subject 'Hello from Claude' and body 'This is amazing!'"
```

Claude will now send emails directly via Lemon API!

---

### **Method 2: Continue.dev** (VS Code)

**1. Install Continue.dev extension in VS Code**

**2. Create MCP config file:**

Create `.continue/config.json` in your project:
```json
{
  "mcpServers": [
    {
      "name": "lemon-email",
      "command": "python",
      "args": ["/full/path/to/lemon-email-mcp/simple_mcp_server.py"],
      "env": {
        "LEMON_EMAIL_API_KEY": "your-key-here"
      }
    }
  ]
}
```

**3. Restart VS Code**

**4. Ask Continue:**
```
"Send an email to user@example.com about the new feature"
```

---

### **Method 3: Direct API (No MCP)**

Want to use the Lemon API directly in your Python code?
```python
import httpx
import asyncio

async def send_email():
    headers = {
        "Content-Type": "application/json",
        "X-Auth-APIKey": "your-lemon-api-key"
    }
    
    payload = {
        "to": "user@example.com",
        "subject": "Hello World",
        "body": "This is a direct API call!",
        "fromname": "Your App",
        "fromemail": "mail@member-notification.com",
        "tag": "direct-api"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://app.xn--lemn-sqa.com/api/transactional/send",
            headers=headers,
            json=payload
        )
        print(response.json())

asyncio.run(send_email())
```

---

## 📚 How It Works
```
Your AI Agent → MCP Protocol → simple_mcp_server.py → Lemon Email API
                                                              ↓
                                                         📧 Email Sent
```

**No intermediate servers!** Direct connection to Lemon Email.

---

## 🔍 Available Tool

The MCP server exposes one tool: `send_email`

**Parameters:**
- `to` (required) - Recipient email
- `subject` (required) - Email subject
- `body` (required) - Email content
- `fromname` (optional) - Sender name (default: "Email Assistant")
- `fromemail` (optional) - Sender email (default: "mail@member-notification.com")
- `toname` (optional) - Recipient name
- `tag` (optional) - Email tag for tracking
- `variables` (optional) - Template variables
- `replyto` (optional) - Reply-to address

---

## 🧪 Testing

**Test direct API connection:**
```bash
python simple_mcp_server.py test
```

**Start MCP server:**
```bash
python simple_mcp_server.py
```

**Get help:**
```bash
python simple_mcp_server.py help
```

---

## 🛠️ Troubleshooting

**"LEMON_EMAIL_API_KEY required"**
- Set environment variable: `export LEMON_EMAIL_API_KEY="your-key"`
- Or add to your MCP config (see examples above)

**"MCP library not available"**
```bash
pip install mcp httpx pydantic
```

**"Connection timeout"**
- Check your internet connection
- Verify API key is correct
- Try test command: `python simple_mcp_server.py test`

**Claude Desktop not seeing the tool**
- Verify JSON syntax in config file
- Use full absolute paths, not ~
- Restart Claude Desktop completely
- Check Claude logs for errors

---

## 📖 Architecture

**What's removed:**
- ❌ Railway deployment
- ❌ Web server wrapper  
- ❌ FastAPI endpoints
- ❌ Intermediate API layer

**What remains:**
- ✅ Direct Lemon API client
- ✅ MCP protocol server
- ✅ Pure Python implementation
- ✅ Minimal dependencies

---

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 📄 License

MIT License - see [LICENSE](LICENSE)

---

## 🔑 Getting API Key

**Need a Lemon Email API key?**

1. DM [@Norman_Szobotka](https://x.com/Norman_Szobotka) on Twitter
2. Or email: [manojk030303@gmail.com](mailto:manojk030303@gmail.com)

You'll get your key within seconds!

---

## 🌟 Features

- **Direct API** - No proxies or intermediate servers
- **Fast** - Direct connection means lower latency
- **Simple** - One Python file, minimal dependencies
- **Reliable** - Fewer moving parts = fewer failures
- **Open Source** - See exactly what it does
- **AI-Ready** - Perfect for AI agents and automation

---

<div align="center">

## Ready to send emails from AI?

[![Get Started](https://img.shields.io/badge/🚀_Get_Started-Now-brightgreen?style=for-the-badge)](https://github.com/manojk0303/lemon-email-mcp)
[![Get API Key](https://img.shields.io/badge/🔑_Get_Key-Free-orange?style=for-the-badge)](https://x.com/Norman_Szobotka)

**Questions?** → [manojk030303@gmail.com](mailto:manojk030303@gmail.com)

</div>

---

<div align="center">
<sub>Direct API • No intermediates • MIT licensed</sub>
</div>