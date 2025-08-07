import asyncio
import os

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def main():
    """
    Main client function to connect to MCP server and call tools.
    
    Uses environment variable MCP_SERVER_URL if available,
    otherwise defaults to localhost.
    """
    url = os.environ.get("MCP_SERVER_URL", "http://127.0.0.1:8000/mcp/")
    async with streamablehttp_client(url) as (read, write, get_session_id):
        async with ClientSession(read, write) as session:
            print("Before initialize:", get_session_id())

            await session.initialize()

            sid = get_session_id()
            print("Session ID after initialize:", sid)

            result = await session.call_tool("add", {"a": 21, "b": 18})
            print("Server result:", result)
            print("Result: ", result.content[0].text)


if __name__ == "__main__":
    asyncio.run(main())
