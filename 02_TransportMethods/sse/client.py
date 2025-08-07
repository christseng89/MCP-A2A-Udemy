import asyncio
import os

from mcp import ClientSession
from mcp.client.sse import sse_client

SERVER_URL = os.environ.get("MCP_SSE_SERVER_URL", "http://127.0.0.1:8000/sse")


async def main() -> None:
    """
    Main client function to connect to SSE MCP server.
    
    Uses environment variable MCP_SSE_SERVER_URL if available,
    otherwise defaults to localhost.
    """
    async with sse_client(SERVER_URL) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            res = await session.call_tool("add", {"a": 7, "b": 5})
            print("7 + 5 =", res.content[0].text)


if __name__ == "__main__":
    asyncio.run(main())
