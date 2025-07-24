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
