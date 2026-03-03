# Kali Linux MCP Server: Installation & Setup Guide

## The Value Proposition: Why Give an AI Kali Linux?

Most LLMs are **"brains in a vat"**—they can tell you *how* to run an Nmap scan, but they can't actually see the results. By connecting Claude to Kali Linux via the **Model Context Protocol (MCP)**, you move from "static advice" to **"active assistance."**

### Key Benefits:

* **Real-time Analysis:** Claude can run a scan, interpret the results, and immediately suggest the next command.
* **Safety & Context:** You maintain control over the environment while the AI handles the complex syntax and data parsing.
* **Workflow Acceleration:** Complex multi-step reconnaissance (Nmap -> Gobuster -> Nikto) can be automated through natural language.

---

## 1. Understanding the Architecture

To make this work, we coordinate three distinct layers. Think of it like a translator sitting between a boss and a worker.

1. **The Client (Claude Desktop):** The "Boss" on your Mac. It sends instructions.
2. **The MCP Bridge (`mcp-server`):** The "Translator." It lives on the Kali machine. It listens to Claude and converts requests into a format the Kali API understands.
3. **The Backend API (`kali-server-mcp`):** The "Worker." This is a Flask-based service running on port 5000 that executes Linux commands and returns raw data.

---

## 2. The Initial Struggle: Network & Installation

Kali is a "rolling release," meaning packages and mirrors move fast.

### The Mirror Timeout

During `sudo apt install mcp-kali-server`, you may hit a dead mirror (e.g., `mirror.us.cdn-perfprod.com`).

* **The Fix:** Run `sudo apt update`. This refreshes the package list and forces the system to find a healthy, responsive mirror.
* **Lesson:** In Kali, if a download fails, refresh the sources first.

### SSH Configuration

To allow Claude on your Mac to talk to Kali securely, set up an SSH alias. Edit your Mac's `~/.ssh/config` file:

```text
Host kali
    HostName 10.53.120.12
    User kali
    IdentityFile ~/.ssh/id_rsa

```

This allows you to use the simple command `ssh kali` instead of typing the full IP and identity path every time.

---

## 3. The Compatibility War: Pydantic 2.10

This is the most common technical roadblock. The `mcp-kali-server` package (built with FastMCP) often conflicts with the latest **Pydantic 2.10** updates in Kali, which introduced strict "type annotation" rules.

### The Error

The server may crash with:
`pydantic.errors.PydanticUserError: A non-annotated attribute was detected: result = typing.Dict[str, typing.Any].`

### The Manual Patch

You must "hotfix" the library core. Edit the following file:
`sudo nano /usr/lib/python3/dist-packages/mcp/server/fastmcp/utilities/func_metadata.py`

**Change:**

```python
return create_model(model_name, result=annotation)

```

**To:**

```python
return create_model(model_name, result=(annotation, ...))

```

*Adding `(annotation, ...)` tells Pydantic that `result` is a required field with a specific type.*

---

## 4. Automation: The Systemd Service

To keep the server running permanently without manual terminal commands, create a systemd service for the **Backend API**.

### The Service File (`/etc/systemd/system/kali-mcp.service`)

We use `ExecStartPre` to clear port 5000 of any "ghost" processes before starting.

```ini
[Unit]
Description=Kali Linux MCP API Server
After=network.target

[Service]
Type=simple
User=kali
Environment=PYTHONUNBUFFERED=1
ExecStartPre=/usr/bin/bash -c "/usr/bin/fuser -k 5000/tcp || true"
ExecStart=/usr/bin/kali-server-mcp --port 5000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target

```

**To enable and start:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now kali-mcp.service

```

---

## 5. Connecting Claude to the Lab

Update the Claude Desktop configuration file on your **Mac**.

**File Path:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "kali-linux": {
      "command": "ssh",
      "args": [
        "-t",
        "kali",
        "mcp-server"
      ]
    }
  }
}

```

* **`-t`**: This is crucial. It forces a pseudo-terminal, which Python needs to handle the I/O stream via SSH.

---

## Summary of Maintenance Commands

| Action | Command |
| --- | --- |
| **Fix Broken Mirror** | `sudo apt update` |
| **Check API Health** | `curl http://localhost:5000/health` |
| **View Live Logs** | `journalctl -u kali-mcp.service -f` |
| **Restart Lab** | `sudo systemctl restart kali-mcp` |

---

Would you like me to help you create a **README.md** to go along with this, or perhaps a section on how to add custom Python tools to this specific API?
