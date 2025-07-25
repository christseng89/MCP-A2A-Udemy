# MCP - Practical Guide 2

## FastMCP V2

- https://github.com/jlowin/fastmcp

## MCP Context

*Warning*: **"Context"** requires a **stateful** connection
  - Use case: Very long running tool (e.g. complex data analysis)

---

- **Stateless**: Clients must **wait** for the entire operation to finish with no visibility into its progress.

- **Stateful** with Context: Keep session open -> send **regular updates** from server to client (e.g. "24 of 1000 files processed")

- **Context** makes progress of tasks visible to clients

```python
@mcp.tool(
    name="process_items", description="Processes a list of items with progress updates"
)
async def process_items(items: list[str], ctx: Context) -> list[str]:
    ...
```

*Tool that processes a list of items*

### Context Essential Features

* **Streaming Log** Messages to the client
* Reporting **incremental progress** to the client

```cmd
cd 04_Context
uv run server.py
```

```cmd
cd 04_Context
npx @modelcontextprotocol/inspector
  Transport Type = Streamable-HTTP
  URL = http://127.0.0.1:8000/mcp
```

```cmd
cd 04_Context
uv run client.py
  ➕ Processing 100 items with progress updates
```

## MCP Discovery

### **Static Discovery**

```python
await client.list_tools()      # Lists all tools available via MCP server  
await client.list_resources()  # Lists all resources available via MCP server  
await client.list_prompts      # Lists all prompts available via MCP server  
```

---

### **Dynamic Discovery**

* Add, update, or remove tools, resources, and prompts at runtime
* Requires a **stateful MCP server** instance
* Requires a **valid context** object
* ⚠️ **Rarely needed** — increases system **complexity** due to state management overhead
* **Usecases:** Large number of tools, "Follow up" tools

---

### **Dynamic Discovery Tools**

Tool 1
Tool 2
…
Tool 1000

- Clean interface for **tool calling** → Provides a clean interface for tool calling
- Just load **necessary tools** upfront → Only load the tools you actually need upfront

---

```cmd
cd 05_Discovery
uv run server.py
```

```cmd
cd 05_Discovery
npx @modelcontextprotocol/inspector
    Transport Type = Streamable-HTTP
    URL = http://127.0.0.1:8000/mcp

```

```cmd
cd 05_Discovery
uv run client.py
    Tools BEFORE : ['router'] 

    📝 [Log | INFO] Result from lower_tool: 'please make this lower case'
    Tools AFTER1  : ['router', 'lower_tool']

    📝 [Log | INFO] Result from upper_tool: 'PLEASE MAKE THIS UPPER CASE'
    Tools AFTER2  : ['router', 'lower_tool', 'upper_tool']

    📝 [Log | INFO] Result from wordcount_tool: 5
    Tools AFTER3  : ['router', 'lower_tool', 'upper_tool', 'wordcount_tool']

```

### Summary

**Dynamic Discovery of Tools** avoids preloading **all 1000+ tools**, which:

* Improves performance
* Reduces memory usage
* Keeps the client interface clean and manageable

---

#### ⚠️ **However (Caveat):**

Dynamic discovery **requires**:

* A **stateful MCP server** (with context object)
* More complex state and lifecycle management
* A trade-off: **flexibility vs complexity**

---

| Feature                    | Static Discovery     | Dynamic Discovery                |
| -------------------------- | -------------------- | -------------------------------- |
| 🔍 Tool list known upfront | ✅ Yes                | ⚠️ No – built at runtime         |
| 🧠 Smart for many tools    | ❌ No – hard to scale | ✅ Yes – loads what's needed only |
| 🧰 Server state required   | ❌ No (stateless OK)  | ✅ Yes (requires context)         |
| 🔄 Flexibility             | ❌ Limited            | ✅ High                           |
| ⚙️ Complexity              | ✅ Simple             | ⚠️ More complex to manage        |

> ✅ Use **Dynamic Discovery** when you have **too many tools** or need **contextual tool availability**.

---

## MCP Roots

**Roots**

* Roots define the operational boundaries of MCP servers
* Specify one or more root entries in a list
* Each root includes a base URI used for organizing resources
* Helps structure and guide how resources are managed and accessed
* Prevents accidental access to resources outside the project scope

### 🔍 What Are *Roots*?

**Roots** define **bounded file system access** for an MCP server — similar to a "sandboxed workspace." They specify which directories the server (and any connected LLM tools) can see and operate on.

---

### 🔒 **Why Restrict Access with Roots?**

1. **Security & Isolation**
   LLMs should **only modify files within the defined root** — not touch:

   * Global config files
   * Other users’ projects
   * Sensitive folders

2. **Scoped Operations**
   Prevents bugs or accidental file writes outside the intended context.

3. **Multi-project Support**
   You can work on **multiple projects in parallel** by assigning each its own root:

   ```python
   roots = [
       "file://{project_a}",
       "file://{project_b}",
   ]
   ```
---

### 🛠 Example:

Client-side:

```python
roots = [f"file://{project_root}"]
client = Client(transport, roots=roots)
```

Then on the server:

```python
roots = await ctx.list_roots()
```
---

Common use case: **coding**

* One project workspace = one **root**
* LLMs should only be allowed to modify files within the workspace/root
* Prevents modification of config files or unrelated folders
* Allows working on multiple projects side by side through root configuration

---

### ✅ Benefits of Root Configuration

| Feature         | Benefit                                                                             |
| --------------- | ----------------------------------------------------------------------------------- |
| **Isolation**   | Keeps tools and file operations within a single project boundary                    |
| **Security**    | Prevents LLMs from accessing or altering unrelated files                            |
| **Scalability** | Supports multiple project roots at once, making MCP usable in team/dev environments |
| **Clarity**     | Reduces ambiguity in where tools should read from or write to                       |

---

```cmd
cd 06_Roots
uv run server.py
```

```cmd
cd 06_Roots
npx @modelcontextprotocol/inspector
    Transport Type = Streamable-HTTP
    URL = http://127.0.0.1:8000/mcp
    Roots = file:///d:/development/mcp-PracticalGuide/06_Roots/demo_root/project => Add Root
```

```cmd
cd 06_Roots
uv run client.py
```

## **Sampling**

* **Server asks the client** to call an LLM to fulfill a requested tool call
* **Client has control** over whether to perform that LLM call or not

---

### 🔧 Use Case

**Tool to create docstrings for a function**

```python
@mcp.tool(
    name="generate_docstring",
    description="Generate a Python docstring for a given function code snippet",
)
async def generate_docstring(code: str, ctx: Context) -> str:
    print("[Server] Tool 'generate_docstring' called")
    print("[Server] Input code:\n", code)

    prompt = (
        "Given the following Python function code, write a concise, "
        "PEP-257-compliant docstring. Your answer should include only the "
        "triple-quoted docstring.\n\n"
        f"{code}"
    )
    print("[Server] Sampling prompt constructed:\n", prompt)

    response = await ctx.sample(
        messages=prompt,
        system_prompt="You are a Python documentation assistant.",
        temperature=0.7,
        max_tokens=150,
    )
```
This allows the **MCP server** to remain **stateless** and **LLM-agnostic**, while enabling **LLM-assisted functionality** like docstring generation to be offloaded to a capable client.

---

### 🧠 Explanation:

* **Server has no access to LLM.**
* Instead, it **delegates** the sampling task to the client, which uses an LLM.
* The **client has full control** to:

  * Accept
  * Modify
  * Reject the `ctx.sample()` request

---

### **Six sampling steps**

1. **Server** sends a sampling/createMessage request to the client
2. Client reviews the request and may modify it
3. Client triggers an LLM call
4. Client reviews and post-processes the LLM output
5. Client sends the polished result back to the server
6. **Server** uses the LLM response to complete the tool/function call (MCP Server to write the docstring)

---

```cmd
cd 07_Sampling
uv run server.py
``

```cmd
cd 07_Sampling
npx @modelcontextprotocol/inspector
    Transport Type = Streamable-HTTP
    URL = http://127.0.0.1:8000/mcp
    Sampling = true

```

```cmd
cd 07_Sampling
uv run client.py
``

