# 🍋 Lemon Email MCP

> **The email API that just works.** Open source. AI-ready. Zero config.

<div align="center">

[![Live Demo](https://img.shields.io/badge/🌐_Try_Now-Live-brightgreen?style=for-the-badge)](https://lemon-email-mcp-production.up.railway.app/)
[![Open Source](https://img.shields.io/badge/📖_Open_Source-MIT-blue?style=for-the-badge)](https://github.com/manojk0303/lemon-email-mcp)
[![Get API Key](https://img.shields.io/badge/🔑_Get_Key-Instant-orange?style=for-the-badge)](https://x.com/Norman_Szobotka)

</div>

---

## ⚡ Send Your First Email in 30 Seconds

```bash
curl -X POST https://lemon-email-mcp-production.up.railway.app/send-email \
  -H "Content-Type: application/json" \
  -d '{
    "to": "user@example.com",
    "subject": "Hello World 👋",
    "body": "This was stupid easy to send.",
    "fromemail": "mail@member-notification.com",
    "api_key": "your-key-here"
  }'
```

**Need an API key?** → DM [@Norman_Szobotka](https://x.com/Norman_Szobotka) or email [manojk030303@gmail.com](mailto:manojk030303@gmail.com)

💡 **Pro tip**: Use `mail@member-notification.com` as your sender - it's pre-configured and works with any API key!

---

## 🚀 Why This is a No-Brainer

**🌐 Use Our API** (Recommended)
- Zero setup required
- Works instantly
- Use `mail@member-notification.com` as sender (pre-configured)
- Or configure your own domain
- Global infrastructure
- Free to try

**🏠 Run Locally** (Open Source)
- Full source code available
- Host anywhere you want  
- Customize everything
- MIT licensed

**🤖 AI Integration**
- Built for AI agents and assistants
- MCP protocol support
- Works with Claude Desktop, Continue.dev, and more
- Perfect for automation

---

## 🛠 Quick Integrations

<details>
<summary><b>JavaScript</b> - Copy & paste ready</summary>

```javascript
const response = await fetch('https://lemon-email-mcp-production.up.railway.app/send-email', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    to: 'user@example.com',
    subject: 'Your app just got email superpowers',
    body: 'Welcome to the future!',
    fromemail: 'mail@member-notification.com', // Pre-configured sender
    api_key: 'your-key-here'
  })
});

const result = await response.json();
console.log('Email sent!', result);
```

</details>

<details>
<summary><b>Python</b> - Two lines, that's it</summary>

```python
import requests

response = requests.post('https://lemon-email-mcp-production.up.railway.app/send-email', json={
    'to': 'user@example.com',
    'subject': 'Python made this easy',
    'body': 'No complicated setup needed!',
    'fromemail': 'mail@member-notification.com',  # Pre-configured sender
    'api_key': 'your-key-here'
})

print('Done!', response.json())
```

</details>

<details>
<summary><b>Continue.dev (VS Code)</b> - AI email assistant</summary>

**1. Clone the repo:**
```bash
git clone https://github.com/manojk0303/lemon-email-mcp.git
cd lemon-email-mcp
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**2. Install Continue.dev extension in VS Code**

**3. Create MCP config:**
Create `.continue/mcpServers/lemon-email.yaml` in your workspace:

```yaml
name: Lemon Email MCP Server
version: 1.0.0
schema: v1
mcpServers:
  - name: Email Assistant
    command: /path/to/your/lemon-email-mcp/venv/bin/python
    args:
      - "/path/to/your/lemon-email-mcp/simple_mcp_server.py"
    env:
      LEMON_EMAIL_API_KEY: "your-key-here"
```

**4. Restart VS Code and ask Continue:**
```
"Send a welcome email to user@example.com"
```

Now Continue can compose and send emails automatically!

</details>

<details>
<summary><b>Claude Desktop</b> - AI email assistant</summary>

**1. Clone the repo:**
```bash
git clone https://github.com/manojk0303/lemon-email-mcp.git
cd lemon-email-mcp
pip install -r requirements.txt
```

**2. Add to your Claude Desktop config:**

```json
{
  "mcpServers": {
    "lemon-email": {
      "command": "python",
      "args": ["/path/to/your/lemon-email-mcp/simple_mcp_server.py"],
      "env": {
        "LEMON_EMAIL_API_KEY": "your-key-here"
      }
    }
  }
}
```

Now Claude can send emails for you automatically!

</details>

---

## 🏠 Run It Locally (Open Source)

**1. Clone & Setup**
```bash
git clone https://github.com/manojk0303/lemon-email-mcp.git
cd lemon-email-mcp
pip install -r requirements.txt

# Set your API key
export LEMON_EMAIL_API_KEY="your-key-here"
```

**2. Test MCP Server**
```bash
python simple_mcp_server.py test
```

**3. Start Web Server** (Optional)
```bash
python web_server.py
# Your local server runs at http://localhost:8000
```

**4. Deploy Anywhere**
- Railway ✅
- Vercel ✅  
- Heroku ✅
- Your own server ✅

---

## 🔥 Real Use Cases

**🤖 AI Agents**
- Customer support automation
- Smart notifications  
- Workflow orchestration

**🚀 Web Apps**
- User onboarding sequences
- Password reset flows
- Order confirmations

**⚡ Side Projects**
- Newsletter campaigns
- Contact form handling
- Event notifications

---

## 📚 What You Get

**☁️ Hosted API**
- `POST /send-email` - Send emails instantly
- `GET /health` - System status
- `GET /docs` - Interactive documentation

**📦 Open Source Code**
- Full Python implementation
- MIT license - use anywhere
- Deploy to any platform
- Customize everything

**🤖 AI-Ready MCP Server**
- Works with Claude Desktop
- Continue.dev integration
- VS Code Copilot compatible
- Any MCP-compatible tool

---

## 🌟 Getting Started

**Option 1: Use Our API (2 minutes)**
1. Get API key → DM [@Norman_Szobotka](https://x.com/Norman_Szobotka)
2. Copy code example above
3. Send your first email
4. Done!

**Option 2: AI Integration (5 minutes)**
1. Clone this repo
2. Install dependencies
3. Configure your AI tool (Claude/Continue.dev)
4. Ask AI to send emails for you

**Option 3: Self-Host (10 minutes)**  
1. Clone and setup locally
2. Deploy to your preferred platform
3. Use your own infrastructure

---

<div align="center">

## 🚀 Ready to send emails the easy way?

[![Try the API](https://img.shields.io/badge/🌐_Try_API_Now-Free-brightgreen?style=for-the-badge)](https://lemon-email-mcp-production.up.railway.app/)
[![Download Code](https://img.shields.io/badge/📦_Get_Source_Code-Open_Source-blue?style=for-the-badge)](https://github.com/manojk0303/lemon-email-mcp)
[![Get API Key](https://img.shields.io/badge/🔑_Get_API_Key-30_seconds-orange?style=for-the-badge)](https://x.com/Norman_Szobotka)

**Questions?** → [manojk030303@gmail.com](mailto:manojk030303@gmail.com) | **Updates** → [@Norman_Szobotka](https://x.com/Norman_Szobotka)

</div>

---

<div align="center">
<sub>Open source • MIT licensed • Made for developers</sub>
</div>