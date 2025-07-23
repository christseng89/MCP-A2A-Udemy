import asyncio
import sys
import os
from dotenv import load_dotenv

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp.client.sse import sse_client
from mcp.client.streamable_http import streamablehttp_client

# Load .env
load_dotenv()
transport = os.getenv("MCP_TRANSPORT", "stdio").lower()

# Server configurations
stdio_server_params = StdioServerParameters(
    command=sys.executable,
    args=["server.py"],
    env=None,
)

SSE_SERVER_URL = "http://127.0.0.1:8000/sse"
HTTP_SERVER_URL = "http://127.0.0.1:8000/mcp/"

# 🔁 Shared session logic
async def run_addition(session: ClientSession):
    # For stateless HTTP transport, we do not need to initialize the session
    if transport != "http":
        await session.initialize()
    res = await session.call_tool("add", {"a": 7, "b": 5})
    print(f"➕ 7 + 5 = {res.content[0].text} by using {transport.upper()} Transport")

# 🚀 Main entry
async def main() -> None:
    print(f"⚙️ Using '{transport.upper()}' transport...\n")

    if transport == "stdio":
        async with stdio_client(stdio_server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await run_addition(session)

    elif transport == "sse":
        async with sse_client(SSE_SERVER_URL) as (read, write):
            async with ClientSession(read, write) as session:
                await run_addition(session)

    elif transport == "http":
        async with streamablehttp_client(HTTP_SERVER_URL) as (read, write, _):
            async with ClientSession(read, write) as session:
                await run_addition(session)

    else:
        raise ValueError(f"❌ Unknown transport: '{transport}'. Supported: stdio, sse, http")

# Run it
if __name__ == "__main__":
    asyncio.run(main())
