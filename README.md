# kali-mcp

This is a powerful addition. By adding custom tools, you aren't just using what Kali provides; you are building a tailored **AI Security Orchestrator**.

Since you installed `mcp-kali-server` via `apt`, the core logic resides in a protected system directory. To add custom tools, you have two choices: **modify the system file** (quickest) or **create a local wrapper** (cleanest). Let's go with the modification since we've already "broken the seal" by patching Pydantic.

---

### Step 1: Locating the Server Logic

The tools are defined in the Python script that runs the Flask API. On a standard `apt` installation, it is located here:
`/usr/lib/python3/dist-packages/kali_server.py`

### Step 2: Defining Your Custom Tool

Let's say you have a custom Python exploit script located at `/home/kali/scripts/my_exploit.py`. You want Claude to be able to run it.

1. Open the server file:
```bash
sudo nano /usr/lib/python3/dist-packages/kali_server.py

```


2. Look for the `@app.route` section. You will see existing tools like `nmap_scan`. Scroll to the bottom of that section and add your own entry:

```python
@app.route('/my_custom_tool', methods=['POST'])
def my_custom_tool():
    data = request.json
    target = data.get('target')
    # Use subprocess to run your local script
    cmd = f"python3 /home/kali/scripts/my_exploit.py --host {target}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return jsonify({"output": result.stdout, "error": result.stderr})

```

---

### Step 3: Registering the Tool with the Bridge

Now that the **API** knows how to run the script, the **MCP Bridge** needs to tell Claude that this tool exists.

1. Open the bridge script:
```bash
sudo nano /usr/lib/python3/dist-packages/mcp_server.py

```


2. Find the `FastMCP` tool definitions (usually starts with `@mcp.tool()`). Add a new one:

```python
@mcp.tool()
async def run_exploit(target: str) -> str:
    """
    Executes a custom internal exploit script against a specific target.
    """
    # This points to the route we just created in kali_server.py
    response = requests.post(f"{KALI_SERVER_URL}/my_custom_tool", json={"target": target})
    return response.json().get("output", "No output returned")

```

---

### Step 4: Applying Changes

Because you modified the system-level files, you need to restart your background service for the "Brain" to recognize its new "Hands."

```bash
sudo systemctl restart kali-mcp.service

```

---

### How to use it in Claude

Once you've restarted, simply ask Claude:

> **"Check if the target 10.53.120.50 is vulnerable using my custom exploit tool."**

Claude will see the `run_exploit` tool in its registry, map it to the Python function, call your Flask API, and execute your private script.

### 💡 Recommendation: Creating a `tools/` Directory

Instead of hardcoding every script, a pro-move is to create a folder at `/home/kali/mcp_tools/` and add a "generic" runner tool to the API. This allows you to just drop a new `.py` or `.sh` file into that folder, and Claude can find and execute it without you ever needing to edit the server code again.

**Would you like me to write the "Generic Runner" code so you can just drop scripts into a folder and have them work instantly?**
