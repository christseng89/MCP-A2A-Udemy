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

### **Discovery Dynamic Tools**

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
